import json
from pathlib import Path
import time
import zipfile

def create_backup(paths, out_dir=None):
    if out_dir is None:
        out_dir = Path(__file__).resolve().parents[2] / 'backups'
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    ts = time.strftime('%Y%m%d_%H%M%S')
    archive = out_dir / f'{ts}.zip'
    manifest = {'version': ts, 'files': []}
    with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED) as z:
        for p in paths:
            p = Path(p)
            if p.is_dir():
                for f in p.rglob('*'):
                    if f.is_file():
                        z.write(f, f.as_posix())
                        manifest['files'].append(f.as_posix())
            elif p.is_file():
                z.write(p, p.as_posix())
                manifest['files'].append(p.as_posix())
    (out_dir / f'{ts}.manifest.json').write_text(json.dumps(manifest, ensure_ascii=False), encoding='utf-8')
    return str(archive)

def restore_backup(archive_path, target_dir=None):
    if target_dir is None:
        target_dir = Path(__file__).resolve().parents[2]
    target_dir = Path(target_dir)
    with zipfile.ZipFile(archive_path, 'r') as z:
        z.extractall(target_dir)
    return str(target_dir)