"""Setup commands the installer runs: register with Claude Desktop, build skill zips, fetch Docling models, check health.

Usage: uv run cheetah setup-claude | build-skills | warm | doctor
"""
import json, os, platform, shutil, sys, zipfile
from pathlib import Path
from . import workspace as ws


def config_paths():
    s = platform.system()
    if s == 'Windows':
        paths = [Path(os.environ['APPDATA']) / 'Claude' / 'claude_desktop_config.json']
        # the Microsoft Store build keeps its config inside its package folder
        pkgs = Path(os.environ.get('LOCALAPPDATA', '')) / 'Packages'
        paths += [p / 'LocalCache' / 'Roaming' / 'Claude' / 'claude_desktop_config.json' for p in pkgs.glob('Claude_*')] if pkgs.exists() else []
        return paths
    if s == 'Darwin':
        return [Path.home() / 'Library' / 'Application Support' / 'Claude' / 'claude_desktop_config.json']
    return [Path.home() / '.config' / 'Claude' / 'claude_desktop_config.json']


def setup_claude():
    uv = shutil.which('uv') or shutil.which('uv.exe')
    if not uv:
        sys.exit('uv not found on PATH; run the installer again')
    entry = {'command': uv, 'args': ['run', '--directory', str(ws.APP), 'cheetah-mcp'],
             'env': {'CHEETAH_WORKSPACE': str(ws.root())}}
    for f in config_paths():
        f.parent.mkdir(parents=True, exist_ok=True)
        cfg = json.loads(f.read_text(encoding='utf-8') or '{}') if f.exists() else {}
        if f.exists():
            shutil.copy(f, f.with_suffix('.json.bak'))
        cfg.setdefault('mcpServers', {})['cheetah'] = entry
        f.write_text(json.dumps(cfg, indent=2), encoding='utf-8')
        print(f'registered with Claude Desktop: {f}')


def build_skills():
    out = ws.APP / 'dist' / 'skills'
    out.mkdir(parents=True, exist_ok=True)
    for d in sorted((ws.APP / 'skills').iterdir()):
        if (d / 'SKILL.md').exists():
            with zipfile.ZipFile(out / f'{d.name}.zip', 'w', zipfile.ZIP_DEFLATED) as z:
                for f in d.rglob('*'):
                    z.write(f, Path(d.name) / f.relative_to(d))
            print(f'skill: {out / (d.name + ".zip")}')


def warm():
    """Download Docling's layout, table and OCR models now, so the first document is not slow (about 500 MB)."""
    from docling.utils.model_downloader import download_models
    download_models(progress=True, with_rapidocr=False, with_code_formula=False, with_picture_classifier=False)
    for attempt in range(3):  # OCR models come from modelscope.cn, which can be slow from South Africa
        try:
            download_models(progress=True, with_layout=False, with_tableformer=False, with_code_formula=False,
                            with_picture_classifier=False, with_rapidocr=True)
            print('Docling models ready')
            return
        except Exception as e:
            print(f'OCR model download failed ({type(e).__name__}); retry {attempt + 1}/3')
    print('Layout models ready. OCR models will download the first time a scan or photo is read.')


def doctor():
    ok = True
    print(f'app        {ws.APP}')
    print(f'workspace  {ws.root()}')
    for mod in ('mcp', 'pdfplumber', 'docling'):
        try:
            __import__(mod)
            print(f'{mod:10} ok')
        except ImportError as e:
            ok = False
            print(f'{mod:10} MISSING ({e})')
    for f in config_paths():
        reg = f.exists() and 'cheetah' in json.loads(f.read_text(encoding='utf-8') or '{}').get('mcpServers', {})
        ok &= reg
        print(f'claude     {"registered" if reg else "NOT registered"} in {f}')
    sys.exit(0 if ok else 1)


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'doctor'
    {'setup-claude': setup_claude, 'build-skills': build_skills, 'warm': warm, 'doctor': doctor}[cmd]()


if __name__ == '__main__':
    main()
