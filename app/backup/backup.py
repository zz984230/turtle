"""备份与回滚原型

支持对指定目录/文件进行打包归档（zip）并生成 `manifest.json`，提供解压恢复到目标目录的能力。
"""

import json
from pathlib import Path
import time
import zipfile

class BackupManager:
    """备份回滚管理器（面向对象）"""

    def __init__(self, out_dir=None):
        if out_dir is None:
            out_dir = Path(__file__).resolve().parents[2] / 'backups'
        self.out_dir = Path(out_dir)
        self.out_dir.mkdir(parents=True, exist_ok=True)

    def create_backup(self, paths):
        ts = time.strftime('%Y%m%d_%H%M%S')
        archive = self.out_dir / f'{ts}.zip'
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
        (self.out_dir / f'{ts}.manifest.json').write_text(json.dumps(manifest, ensure_ascii=False), encoding='utf-8')
        return str(archive)

    def restore_backup(self, archive_path, target_dir=None):
        if target_dir is None:
            target_dir = Path(__file__).resolve().parents[2]
        target_dir = Path(target_dir)
        with zipfile.ZipFile(archive_path, 'r') as z:
            z.extractall(target_dir)
        return str(target_dir)