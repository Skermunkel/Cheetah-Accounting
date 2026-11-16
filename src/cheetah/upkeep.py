"""Updates from GitHub and feedback to the maintainer. Neither sends any workspace data anywhere."""
import io, re, shutil, subprocess, tempfile, urllib.parse, urllib.request, webbrowser, zipfile
from pathlib import Path
from .workspace import APP

REPO = 'Skermunkel/Cheetah-Accounting'


def version(text):
    m = re.search(r'^version\s*=\s*"([^"]+)"', text, re.M)
    return m.group(1) if m else '?'


def local_version():
    return version((APP / 'pyproject.toml').read_text(encoding='utf-8'))


def remote_version():
    url = f'https://raw.githubusercontent.com/{REPO}/main/pyproject.toml'
    with urllib.request.urlopen(url, timeout=10) as r:
        return version(r.read().decode())


def update(check_only=False):
    old = local_version()
    try:
        new = remote_version()
    except OSError as e:
        return f'could not reach GitHub ({e}); try again later'
    if check_only or new == old:
        return f'installed {old}, latest {new}' + ('' if new != old else ' (up to date)')
    if (APP / '.git').exists():
        before = subprocess.run(['git', '-C', str(APP), 'rev-parse', 'HEAD'], capture_output=True, text=True).stdout.strip()
        r = subprocess.run(['git', '-C', str(APP), 'pull', '--ff-only'], capture_output=True, text=True)
        if r.returncode:
            return f'update failed: {r.stderr.strip()[:400]}'
        log = subprocess.run(['git', '-C', str(APP), 'log', '--oneline', f'{before}..HEAD'], capture_output=True, text=True).stdout
    else:  # installed from a zip: replace the app files, keep the Python environment
        with urllib.request.urlopen(f'https://codeload.github.com/{REPO}/zip/refs/heads/main', timeout=60) as r:
            z = zipfile.ZipFile(io.BytesIO(r.read()))
        with tempfile.TemporaryDirectory() as tmp:
            z.extractall(tmp)
            src = next(Path(tmp).iterdir())
            for item in src.iterdir():
                dest = APP / item.name
                if dest.is_dir():
                    shutil.rmtree(dest)
                elif dest.exists():
                    dest.unlink()
                shutil.move(str(item), dest)
        log = '(installed from zip: see CHANGELOG.md)'
    return (f'updated {old} -> {new}. Fully quit and reopen Claude Desktop so the new version starts '
            f'(it installs any new requirements on start).\n{log}')


REDACT = [
    (r'[\w.+-]+@[\w-]+\.[\w.]+', '[email]'),
    (r'\b\d{13}\b', '[ID number]'),
    (r'\b[0-49]\d{9}\b', '[tax or VAT number]'),
    (r'\b\d{6,}\b', '[number]'),
    (r'\b0\d{2}[ -]?\d{3}[ -]?\d{4}\b|\+27[\d ]{9,12}', '[phone]'),
    (r'\bR ?\d[\d ,]*\.\d{2}\b', '[amount]'),
]


def redact(text):
    for pat, rep in REDACT:
        text = re.sub(pat, rep, text)
    return text


def feedback(title, body, open_browser=True):
    """Open a pre-filled GitHub issue (the person reviews it and clicks Submit). Personal details are masked first."""
    title, body = redact(title), redact(body)
    url = f'https://github.com/{REPO}/issues/new?' + urllib.parse.urlencode(
        {'title': title, 'body': body + '\n\n_Sent from Cheetah ' + local_version() + '_', 'labels': 'feedback'})
    if open_browser:
        webbrowser.open(url)
    return title, body, url
