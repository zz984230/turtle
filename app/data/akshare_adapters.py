"""akshare 适配器模块

封装常用 A 股数据接口，统一加入本地 TTL 缓存与简单日志记录，便于上层分析与策略模块复用。

函数返回值均为 `pandas.DataFrame`，字段命名保持 akshare 原始输出，避免不必要的转换。
"""

import akshare as ak
import pandas as pd
from typing import Optional
from app.cache.cache_manager import CacheManager
from app.utils.logging import get_logger

_cache = CacheManager()
_log = get_logger('akshare_adapters')

def _store(category: str, key: str, df: pd.DataFrame, use_cache: bool, ttl_seconds: int) -> pd.DataFrame:
    """读取或写入缓存并返回数据

    参数
    - category: 缓存分类目录名
    - key: 当前数据键（通常由 symbol 或日期组成）
    - df: 待缓存的数据帧
    - use_cache: 是否启用缓存读取
    - ttl_seconds: 缓存有效期（秒）

    返回
    - DataFrame：命中缓存则返回缓存内容，否则写入后返回最新内容
    """
    if use_cache:
        cached = _cache.read(category, key, ttl_seconds)
        if cached is not None:
            return cached
    _cache.write(category, key, df)
    return df

def index_spot_em(symbol_group: str = '沪深重要指数', use_cache: bool = True, ttl_seconds: int = 300) -> pd.DataFrame:
    """东方财富-沪深京指数实时行情

    参数
    - symbol_group: 指数分组（如“沪深重要指数”、“上证系列指数”等）
    - use_cache: 是否启用缓存
    - ttl_seconds: 缓存有效期（秒）

    返回
    - DataFrame：实时指数行情列表
    """
    key = f'{symbol_group}'.replace('/', '_')
    df = ak.stock_zh_index_spot_em(symbol=symbol_group)
    return _store('index_spot_em', key, df, use_cache, ttl_seconds)

def index_daily(symbol: str, use_cache: bool = True, ttl_seconds: int = 3600) -> pd.DataFrame:
    """股票指数日频历史行情（新浪）

    参数
    - symbol: 指数代码（如“sh000001”、“sz399001”）
    - use_cache: 是否启用缓存
    - ttl_seconds: 缓存有效期（秒）

    返回
    - DataFrame：包含 `date, open, high, low, close, volume` 等字段
    """
    key = f'{symbol}'.replace('/', '_')
    df = ak.stock_zh_index_daily(symbol=symbol)
    return _store('index_daily', key, df, use_cache, ttl_seconds)

def industry_fund_flow(use_cache: bool = True, ttl_seconds: int = 300) -> pd.DataFrame:
    """行业资金流向（同花顺数据中心）

    参数
    - use_cache: 是否启用缓存
    - ttl_seconds: 缓存有效期（秒）

    返回
    - DataFrame：行业维度的资金流数据
    """
    key = 'latest'
    df = ak.stock_fund_flow_industry()
    return _store('industry_fund_flow', key, df, use_cache, ttl_seconds)

def individual_fund_flow(stock: str, market: Optional[str] = None, use_cache: bool = True, ttl_seconds: int = 300) -> pd.DataFrame:
    """个股资金流（同花顺数据中心）

    参数
    - stock: 股票代码（如“000651”、“600000”）
    - market: 市场标识（默认根据代码首位推断：6→sh，其它→sz）
    - use_cache: 是否启用缓存
    - ttl_seconds: 缓存有效期（秒）

    返回
    - DataFrame：近若干交易日的个股资金流数据
    """
    if market is None:
        market = 'sh' if stock.startswith('6') else 'sz'
    key = f'{market}_{stock}'
    df = ak.stock_individual_fund_flow(stock=stock, market=market)
    return _store('individual_fund_flow', key, df, use_cache, ttl_seconds)

def a_spot_em(use_cache: bool = True, ttl_seconds: int = 60) -> pd.DataFrame:
    """A股实时行情快照（东方财富）

    参数
    - use_cache: 是否启用缓存
    - ttl_seconds: 缓存有效期（秒）

    返回
    - DataFrame：全市场实时行情，含涨跌幅等字段
    """
    key = 'all'
    df = ak.stock_zh_a_spot_em()
    return _store('a_spot_em', key, df, use_cache, ttl_seconds)

def margin_sse(start_date: str, end_date: str, use_cache: bool = True, ttl_seconds: int = 86400) -> pd.DataFrame:
    """上交所融资融券汇总（历史区间）

    参数
    - start_date: 起始日期，格式 `YYYYMMDD`
    - end_date: 结束日期，格式 `YYYYMMDD`
    - use_cache: 是否启用缓存
    - ttl_seconds: 缓存有效期（秒）

    返回
    - DataFrame：区间内融资融券汇总数据
    """
    key = f'{start_date}_{end_date}'
    df = ak.stock_margin_sse(start_date=start_date, end_date=end_date)
    return _store('margin_sse', key, df, use_cache, ttl_seconds)

def margin_szse(start_date: str, end_date: str, use_cache: bool = True, ttl_seconds: int = 86400) -> pd.DataFrame:
    """深交所融资融券汇总（历史区间）

    参数
    - start_date: 起始日期，格式 `YYYYMMDD`
    - end_date: 结束日期，格式 `YYYYMMDD`
    - use_cache: 是否启用缓存
    - ttl_seconds: 缓存有效期（秒）

    返回
    - DataFrame：区间内融资融券汇总数据
    """
    key = f'{start_date}_{end_date}'
    df = ak.stock_margin_szse(start_date=start_date, end_date=end_date)
    return _store('margin_szse', key, df, use_cache, ttl_seconds)

def zt_pool_em(date: str, use_cache: bool = True, ttl_seconds: int = 86400) -> pd.DataFrame:
    """涨停股池（东方财富）

    参数
    - date: 交易日，格式 `YYYYMMDD` 或 `YYYY-MM-DD`
    - use_cache: 是否启用缓存
    - ttl_seconds: 缓存有效期（秒）

    返回
    - DataFrame：指定交易日的涨停股池数据
    """
    key = f'{date}'
    df = ak.stock_zt_pool_em(date=date)
    return _store('zt_pool_em', key, df, use_cache, ttl_seconds)