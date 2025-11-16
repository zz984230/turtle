"""TTL 缓存管理

将 DataFrame 以 Parquet 形式持久化，并记录元数据（时间戳），支持按分类与键读取，提供简单的 TTL 过期判断。
"""

import json
import time
from pathlib import Path
from typing import Optional
import pandas as pd

class CacheManager:
    """缓存管理器

    参数
    - base_dir: 缓存根目录（默认项目根下 `data/cache/`）
    """
    def __init__(self, base_dir: Optional[Path] = None):
        if base_dir is None:
            base_dir = Path(__file__).resolve().parents[2] / 'data' / 'cache'
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def _paths(self, category: str, key: str):
        """返回数据与元数据路径"""
        cat_dir = self.base_dir / category
        cat_dir.mkdir(parents=True, exist_ok=True)
        data_path = cat_dir / f'{key}.parquet'
        meta_path = cat_dir / f'{key}.meta.json'
        return data_path, meta_path

    def read(self, category: str, key: str, ttl_seconds: int) -> Optional[pd.DataFrame]:
        """读取缓存，如过期或不存在返回 None

        参数
        - category: 分类目录名
        - key: 数据键
        - ttl_seconds: 过期时间（秒），<=0 表示总是过期
        """
        data_path, meta_path = self._paths(category, key)
        if not data_path.exists() or not meta_path.exists():
            return None
        try:
            meta = json.loads(meta_path.read_text(encoding='utf-8'))
            ts = meta.get('timestamp', 0)
            if ttl_seconds > 0 and time.time() - ts > ttl_seconds:
                return None
            return pd.read_parquet(data_path)
        except Exception:
            return None

    def write(self, category: str, key: str, df: pd.DataFrame):
        """写入缓存（Parquet + 元数据时间戳）"""
        data_path, meta_path = self._paths(category, key)
        df.to_parquet(data_path, index=False)
        meta = {'timestamp': int(time.time())}
        meta_path.write_text(json.dumps(meta, ensure_ascii=False), encoding='utf-8')