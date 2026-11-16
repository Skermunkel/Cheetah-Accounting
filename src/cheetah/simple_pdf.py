"""Minimal dependency-free PDF writer for text reports (A4 portrait, built-in Courier / Helvetica-Bold).

Usage from Python:
    from simple_pdf import Report
    r = Report('Title shown on every page')
    r.heading('Section'); r.text('A line of text'); r.row(['2022-03-01', 'Tops', '12.50'], [12, 60, 14], right={2})
    r.save('out.pdf')
Column widths are in characters (Courier 8 pt fits about 105 per line).
"""

W, H, M = 595, 842, 40          # A4 in points, margin
SIZE, LEAD = 8, 10.5             # body font size and line height
CHARS = int((W - 2 * M) / (SIZE * 0.6))


def esc(s):
    return s.replace('\\', '\\\\').replace('(', '\\(').replace(')', '\\)').encode('latin-1', 'replace').decode('latin-1')


class Report:
    def __init__(self, title):
        self.title, self.pages, self.cur, self.y = title, [], None, 0
        self.new_page()

    def new_page(self):
        self.cur = []
        self.pages.append(self.cur)
        self.y = H - M
        self._put(self.title, 'F2', 10)
        self.y -= 4

    def _put(self, s, font='F1', size=SIZE, x=M):
        if self.y < M + LEAD:
            self.new_page()
        self.cur.append(f'BT /{font} {size} Tf {x} {self.y:.1f} Td ({esc(s)}) Tj ET')
        self.y -= max(LEAD, size + 3)

    def heading(self, s):
        self.y -= 6
        self._put(s, 'F2', 10)

    def text(self, s):
        while len(s) > CHARS:                      # simple word wrap
            cut = s.rfind(' ', 0, CHARS)
            cut = cut if cut > 0 else CHARS
            self._put(s[:cut])
            s = s[cut:].lstrip()
        self._put(s)

    def row(self, cells, widths, right=(), bold=False):
        parts = []
        for i, (c, w) in enumerate(zip(cells, widths)):
            c = str(c)[:w - 1] if len(str(c)) >= w else str(c)
            parts.append(c.rjust(w - 1) + ' ' if i in right else c.ljust(w))
        self._put(''.join(parts), 'F3' if bold else 'F1')

    def rule(self, n=CHARS):
        self._put('-' * n)

    def save(self, path):
        objs = ['<< /Type /Catalog /Pages 2 0 R >>', None,
                '<< /Type /Font /Subtype /Type1 /BaseFont /Courier /Encoding /WinAnsiEncoding >>',
                '<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold /Encoding /WinAnsiEncoding >>',
                '<< /Type /Font /Subtype /Type1 /BaseFont /Courier-Bold /Encoding /WinAnsiEncoding >>']
        kids = []
        total = len(self.pages)
        for i, ops in enumerate(self.pages, 1):
            ops = ops + [f'BT /F1 7 Tf {W - M - 60} {M - 18} Td (Page {i} of {total}) Tj ET']
            stream = '\n'.join(ops).encode('latin-1')
            objs.append(f'<< /Length {len(stream)} >>\nstream\n'.encode('latin-1') + stream + b'\nendstream')
            objs.append(f'<< /Type /Page /Parent 2 0 R /MediaBox [0 0 {W} {H}] /Contents {len(objs)} 0 R '
                        f'/Resources << /Font << /F1 3 0 R /F2 4 0 R /F3 5 0 R >> >> >>')
            kids.append(f'{len(objs)} 0 R')
        objs[1] = f'<< /Type /Pages /Kids [{" ".join(kids)}] /Count {total} >>'
        out, offs = bytearray(b'%PDF-1.4\n'), []
        for n, o in enumerate(objs, 1):
            offs.append(len(out))
            body = o if isinstance(o, bytes) else o.encode('latin-1')
            out += f'{n} 0 obj\n'.encode() + body + b'\nendobj\n'
        x = len(out)
        out += f'xref\n0 {len(objs) + 1}\n0000000000 65535 f \n'.encode()
        out += ''.join(f'{o:010d} 00000 n \n' for o in offs).encode()
        out += f'trailer\n<< /Size {len(objs) + 1} /Root 1 0 R /Info << /Title ({esc(self.title)}) >> >>\nstartxref\n{x}\n%%EOF\n'.encode()
        open(path, 'wb').write(out)
