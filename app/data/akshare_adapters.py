import akshare as ak
import pandas as pd
from typing import Optional
from app.cache.cache_manager import CacheManager
from app.utils.logging import get_logger

_cache = CacheManager()
_log = get_logger('akshare_adapters')

def _store(category: str, key: str, df: pd.DataFrame, use_cache: bool, ttl_seconds: int) -> pd.DataFrame:
    if use_cache:
        cached = _cache.read(category, key, ttl_seconds)
        if cached is not None:
            return cached
    _cache.write(category, key, df)
    return df

def index_spot_em(symbol_group: str = '沪深重要指数', use_cache: bool = True, ttl_seconds: int = 300) -> pd.DataFrame:
    key = f'{symbol_group}'.replace('/', '_')
    df = ak.stock_zh_index_spot_em(symbol=symbol_group)
    return _store('index_spot_em', key, df, use_cache, ttl_seconds)

def index_daily(symbol: str, use_cache: bool = True, ttl_seconds: int = 3600) -> pd.DataFrame:
    key = f'{symbol}'.replace('/', '_')
    df = ak.stock_zh_index_daily(symbol=symbol)
    return _store('index_daily', key, df, use_cache, ttl_seconds)

def industry_fund_flow(use_cache: bool = True, ttl_seconds: int = 300) -> pd.DataFrame:
    key = 'latest'
    df = ak.stock_fund_flow_industry()
    return _store('industry_fund_flow', key, df, use_cache, ttl_seconds)

def individual_fund_flow(stock: str, market: Optional[str] = None, use_cache: bool = True, ttl_seconds: int = 300) -> pd.DataFrame:
    if market is None:
        market = 'sh' if stock.startswith('6') else 'sz'
    key = f'{market}_{stock}'
    df = ak.stock_individual_fund_flow(stock=stock, market=market)
    return _store('individual_fund_flow', key, df, use_cache, ttl_seconds)

def a_spot_em(use_cache: bool = True, ttl_seconds: int = 60) -> pd.DataFrame:
    key = 'all'
    df = ak.stock_zh_a_spot_em()
    return _store('a_spot_em', key, df, use_cache, ttl_seconds)

def margin_sse(start_date: str, end_date: str, use_cache: bool = True, ttl_seconds: int = 86400) -> pd.DataFrame:
    key = f'{start_date}_{end_date}'
    df = ak.stock_margin_sse(start_date=start_date, end_date=end_date)
    return _store('margin_sse', key, df, use_cache, ttl_seconds)

def margin_szse(start_date: str, end_date: str, use_cache: bool = True, ttl_seconds: int = 86400) -> pd.DataFrame:
    key = f'{start_date}_{end_date}'
    df = ak.stock_margin_szse(start_date=start_date, end_date=end_date)
    return _store('margin_szse', key, df, use_cache, ttl_seconds)

def zt_pool_em(date: str, use_cache: bool = True, ttl_seconds: int = 86400) -> pd.DataFrame:
    key = f'{date}'
    df = ak.stock_zt_pool_em(date=date)
    return _store('zt_pool_em', key, df, use_cache, ttl_seconds)