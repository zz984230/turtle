import json
import time
from pathlib import Path
from typing import Optional
import pandas as pd

class CacheManager:
    def __init__(self, base_dir: Optional[Path] = None):
        if base_dir is None:
            base_dir = Path(__file__).resolve().parents[2] / 'data' / 'cache'
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def _paths(self, category: str, key: str):
        cat_dir = self.base_dir / category
        cat_dir.mkdir(parents=True, exist_ok=True)
        data_path = cat_dir / f'{key}.parquet'
        meta_path = cat_dir / f'{key}.meta.json'
        return data_path, meta_path

    def read(self, category: str, key: str, ttl_seconds: int) -> Optional[pd.DataFrame]:
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
        data_path, meta_path = self._paths(category, key)
        df.to_parquet(data_path, index=False)
        meta = {'timestamp': int(time.time())}
        meta_path.write_text(json.dumps(meta, ensure_ascii=False), encoding='utf-8')