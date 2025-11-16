"""备份与回滚原型

支持对指定目录/文件进行打包归档（zip）并生成 `manifest.json`，提供解压恢复到目标目录的能力。
"""

import json
from pathlib import Path
import time
import zipfile

def create_backup(paths, out_dir=None):
    """创建备份归档

    参数
    - paths: 待备份的目录/文件列表
    - out_dir: 备份输出目录，默认项目根下 `backups/`

    返回
    - str：生成的 zip 文件路径
    """
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
    """从备份归档恢复文件

    参数
    - archive_path: zip 归档路径
    - target_dir: 解压目标目录，默认项目根

    返回
    - str：恢复后的目标目录路径
    """
    if target_dir is None:
        target_dir = Path(__file__).resolve().parents[2]
    target_dir = Path(target_dir)
    with zipfile.ZipFile(archive_path, 'r') as z:
        z.extractall(target_dir)
    return str(target_dir)