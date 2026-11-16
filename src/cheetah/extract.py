"""Read any document locally and pull out the few facts Claude needs, so the full text never has to go to Claude.

Engines, cheapest first:
  - digital PDFs (bank statements, invoices, SARS letters): pdfplumber's exact text layer, keeping the column layout
  - scans, photos, Word, Excel, PowerPoint, HTML: Docling (layout + table structure + OCR), fully offline after
    its models download once
  - CSV and text: read as is
"""
import csv, datetime, io, os, re
from pathlib import Path

TEXT = {'.csv', '.txt', '.tsv', '.md', '.ofx', '.qif'}
DOCLING = {'.png', '.jpg', '.jpeg', '.tif', '.tiff', '.bmp', '.webp', '.docx', '.xlsx', '.pptx', '.html', '.htm'}
SUPPORTED = TEXT | DOCLING | {'.pdf'}
_converter = None


def docling(path):
    global _converter
    if _converter is None:
        from docling.datamodel.settings import settings
        if any((settings.cache_dir / 'models').glob('*layout*')):
            # models are on disk: never wait on (or talk to) the internet while reading documents
            os.environ.setdefault('HF_HUB_OFFLINE', '1')
        from docling.datamodel.base_models import InputFormat
        from docling.datamodel.pipeline_options import PdfPipelineOptions
        from docling.document_converter import DocumentConverter, ImageFormatOption, PdfFormatOption
        opts = PdfPipelineOptions(do_ocr=True, do_table_structure=True)
        _converter = DocumentConverter(format_options={InputFormat.PDF: PdfFormatOption(pipeline_options=opts),
                                                       InputFormat.IMAGE: ImageFormatOption(pipeline_options=opts)})
    return _converter.convert(str(path)).document.export_to_markdown()


def pdf_text(path):
    import pdfplumber
    with pdfplumber.open(path) as pdf:
        # x_tolerance below the default: some banks pack letters so closely that words run together
        return '\n\f\n'.join(p.extract_text(layout=True, x_tolerance=1.5) or '' for p in pdf.pages), len(pdf.pages)


def extract(path):
    """Return (text, method). Scanned PDFs (almost no text layer) go to Docling with OCR."""
    path = Path(path)
    ext = path.suffix.lower()
    if ext in TEXT:
        return path.read_text(encoding='utf-8-sig', errors='replace'), 'text'
    if ext == '.pdf':
        text, pages = pdf_text(path)
        if len(re.sub(r'\s', '', text)) >= 80 * max(pages, 1):
            return text, 'pdf text layer'
        return docling(path), 'docling OCR'
    if ext in DOCLING:
        return docling(path), 'docling'
    raise ValueError(f'unsupported file type {ext}; supported: {", ".join(sorted(SUPPORTED))}')


MONTHS = {m: i for i, m in enumerate('jan feb mar apr may jun jul aug sep oct nov dec'.split(), 1)}
DATE = re.compile(r'\b(\d{4})[-/](\d{1,2})[-/](\d{1,2})\b|\b(\d{1,2})[-/ ](\d{1,2}|[A-Za-z]{3,9})[-/ ,]+(\d{4})\b')
MONEY = r'R?\s?-?\(?\d{1,3}(?:[ ,]\d{3})*\.\d{2}\)?'


def dates(text):
    out = []
    for m in DATE.finditer(text):
        try:
            if m.group(1):
                y, mo, d = int(m.group(1)), int(m.group(2)), int(m.group(3))
            else:
                d, y, mo = int(m.group(4)), int(m.group(6)), m.group(5)
                mo = int(mo) if mo.isdigit() else MONTHS.get(mo[:3].lower())
            out.append(datetime.date(y, mo, d).isoformat())
        except (TypeError, ValueError):
            pass
    return out


def money(s):
    s = s.replace('R', '').replace(' ', '').replace(',', '').strip()
    neg = s.startswith('-') or s.startswith('(')
    return -float(s.strip('-()')) if neg else float(s.strip('-()'))


def kind_of(text, name):
    t = (text[:6000] + ' ' + name).lower()
    if re.search(r'irp5|it3\s*\(a\)|\b3601\b|\b3605\b|\b4102\b', t):
        return 'certificates', 'IRP5/IT3(a) employee tax certificate'
    if re.search(r'it3\s*\(b\)|it3b|interest certificate', t):
        return 'certificates', 'IT3(b) investment income certificate'
    if re.search(r'medical (aid|scheme)', t) and 'certificate' in t:
        return 'certificates', 'medical aid tax certificate'
    if re.search(r'retirement annuity|ra contribution|section 11f|s11f', t) and 'certificate' in t:
        return 'certificates', 'retirement annuity certificate'
    if re.search(r'section 18a|s18a', t):
        return 'certificates', 'section 18A donation receipt'
    if re.search(r'south african revenue service|\bsars\b|ita34|notice of assessment|statement of account|efiling', t):
        return 'sars', 'SARS letter, assessment or statement'
    if re.search(r'\bcipc\b|companies and intellectual property|annual return|beneficial ownership', t):
        return 'cipc', 'CIPC document'
    if re.search(r'(opening|closing) balance|balance brought forward|statement period|transaction history', t) \
            or name.lower().endswith(('.csv', '.ofx', '.qif')):
        return 'bank', 'bank or card statement'
    if re.search(r'tax invoice|\binvoice\b', t):
        return 'invoices', 'invoice'
    if re.search(r'\b(total|amount due|change|cash|card)\b', t) and len(text) < 4000:
        return 'receipts', 'till slip or receipt'
    return 'other', 'other document'


def facts(text, kind):
    """Small structured summary: the part Claude actually reads."""
    f = {}
    ds = dates(text)
    if ds:
        f['dates'] = f'{min(ds)} .. {max(ds)}' if len(set(ds)) > 1 else ds[0]
    vat = sorted(set(re.findall(r'\b4\d{9}\b', text)))
    if vat:
        f['vat_numbers'] = vat[:3]
    if kind == 'certificates':  # SARS source codes and their amounts, e.g. 3601 Salary 250 000.00
        codes = {}
        for m in re.finditer(r'\b(3[6-9]\d\d|4\d{3})\b[^\n\d]{0,60}?(' + MONEY + ')', text):
            codes.setdefault(m.group(1), money(m.group(2)))
        if codes:
            f['source_codes'] = codes
    if kind in ('invoices', 'receipts', 'sars'):
        for label in ['total due', 'amount due', 'balance due', 'total', 'vat']:
            m = re.search(label + r'[^\n\d-]{0,30}(' + MONEY + ')', text, re.I)
            if m:
                f[label.replace(' ', '_')] = money(m.group(1))
    if kind == 'bank':
        m = re.search(r'account (?:number|no\.?)\s*:?\s*([\d -]{6,20}\d)', text, re.I)
        if m:
            f['account_last4'] = re.sub(r'\D', '', m.group(1))[-4:]
        for bank in ['FNB', 'First National Bank', 'Capitec', 'Absa', 'Standard Bank', 'Nedbank', 'Investec',
                     'TymeBank', 'Discovery', 'African Bank', 'Bank Zero']:
            if bank.lower() in text[:3000].lower():
                f['bank'] = 'FNB' if bank == 'First National Bank' else bank
                break
    return f


def csv_rows(text):
    return list(csv.reader(io.StringIO(text)))
