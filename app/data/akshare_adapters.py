"""akshare 适配器模块

封装常用 A 股数据接口，统一加入本地 TTL 缓存与简单日志记录，便于上层分析与策略模块复用。

函数返回值均为 `pandas.DataFrame`，字段命名保持 akshare 原始输出，避免不必要的转换。
"""

import akshare as ak
import pandas as pd
from typing import Optional
from app.cache.cache_manager import CacheManager
from app.utils.logging import get_logger

class AkshareClient:
    """Akshare 数据客户端（面向对象）

    提供常用 A 股数据查询方法，并内置 TTL 缓存与日志。
    """

    def __init__(self):
        self.cache = CacheManager()
        self.log = get_logger('akshare_adapters')

    def _store(self, category: str, key: str, df: pd.DataFrame, use_cache: bool, ttl_seconds: int) -> pd.DataFrame:
        if use_cache:
            cached = self.cache.read(category, key, ttl_seconds)
            if cached is not None:
                return cached
        self.cache.write(category, key, df)
        return df

    def index_spot_em(self, symbol_group: str = '沪深重要指数', use_cache: bool = True, ttl_seconds: int = 300) -> pd.DataFrame:
        key = f'{symbol_group}'.replace('/', '_')
        df = ak.stock_zh_index_spot_em(symbol=symbol_group)
        return self._store('index_spot_em', key, df, use_cache, ttl_seconds)

    def index_daily(self, symbol: str, use_cache: bool = True, ttl_seconds: int = 3600) -> pd.DataFrame:
        key = f'{symbol}'.replace('/', '_')
        df = ak.stock_zh_index_daily(symbol=symbol)
        return self._store('index_daily', key, df, use_cache, ttl_seconds)

    def industry_fund_flow(self, use_cache: bool = True, ttl_seconds: int = 300) -> pd.DataFrame:
        key = 'latest'
        df = ak.stock_fund_flow_industry()
        return self._store('industry_fund_flow', key, df, use_cache, ttl_seconds)

    def individual_fund_flow(self, stock: str, market: Optional[str] = None, use_cache: bool = True, ttl_seconds: int = 300) -> pd.DataFrame:
        if market is None:
            market = 'sh' if stock.startswith('6') else 'sz'
        key = f'{market}_{stock}'
        df = ak.stock_individual_fund_flow(stock=stock, market=market)
        return self._store('individual_fund_flow', key, df, use_cache, ttl_seconds)

    def a_spot_em(self, use_cache: bool = True, ttl_seconds: int = 60) -> pd.DataFrame:
        key = 'all'
        df = ak.stock_zh_a_spot_em()
        return self._store('a_spot_em', key, df, use_cache, ttl_seconds)

    def margin_sse(self, start_date: str, end_date: str, use_cache: bool = True, ttl_seconds: int = 86400) -> pd.DataFrame:
        key = f'{start_date}_{end_date}'
        df = ak.stock_margin_sse(start_date=start_date, end_date=end_date)
        return self._store('margin_sse', key, df, use_cache, ttl_seconds)

    def margin_szse(self, start_date: str, end_date: str, use_cache: bool = True, ttl_seconds: int = 86400) -> pd.DataFrame:
        key = f'{start_date}_{end_date}'
        df = ak.stock_margin_szse(start_date=start_date, end_date=end_date)
        return self._store('margin_szse', key, df, use_cache, ttl_seconds)

    def zt_pool_em(self, date: str, use_cache: bool = True, ttl_seconds: int = 86400) -> pd.DataFrame:
        key = f'{date}'
        df = ak.stock_zt_pool_em(date=date)
        return self._store('zt_pool_em', key, df, use_cache, ttl_seconds)

_client = AkshareClient()

def index_spot_em(symbol_group: str = '沪深重要指数', use_cache: bool = True, ttl_seconds: int = 300) -> pd.DataFrame:
    return _client.index_spot_em(symbol_group, use_cache, ttl_seconds)

def index_daily(symbol: str, use_cache: bool = True, ttl_seconds: int = 3600) -> pd.DataFrame:
    return _client.index_daily(symbol, use_cache, ttl_seconds)

def industry_fund_flow(use_cache: bool = True, ttl_seconds: int = 300) -> pd.DataFrame:
    return _client.industry_fund_flow(use_cache, ttl_seconds)

def individual_fund_flow(stock: str, market: Optional[str] = None, use_cache: bool = True, ttl_seconds: int = 300) -> pd.DataFrame:
    return _client.individual_fund_flow(stock, market, use_cache, ttl_seconds)

def a_spot_em(use_cache: bool = True, ttl_seconds: int = 60) -> pd.DataFrame:
    return _client.a_spot_em(use_cache, ttl_seconds)

def margin_sse(start_date: str, end_date: str, use_cache: bool = True, ttl_seconds: int = 86400) -> pd.DataFrame:
    return _client.margin_sse(start_date, end_date, use_cache, ttl_seconds)

def margin_szse(start_date: str, end_date: str, use_cache: bool = True, ttl_seconds: int = 86400) -> pd.DataFrame:
    return _client.margin_szse(start_date, end_date, use_cache, ttl_seconds)

def zt_pool_em(date: str, use_cache: bool = True, ttl_seconds: int = 86400) -> pd.DataFrame:
    return _client.zt_pool_em(date, use_cache, ttl_seconds)