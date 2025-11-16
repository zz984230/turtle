"""可转债数据处理

基于 AKShare 获取与处理沪深可转债相关数据，提供列表与单券历史行情拉取，并支持本地 CSV 缓存。
"""

import akshare as ak
import pandas as pd
from pathlib import Path
import os
from datetime import datetime, timedelta

class BondData:
    """可转债数据处理类

    使用 AKShare 接口获取可转债列表与历史行情，并提供 CSV 持久化选项。
    """

    def __init__(self, data_dir: str = None):
        """初始化

        参数
        - data_dir: 数据存储根目录（默认 `data/bond/`）
        """
        if data_dir is None:
            data_dir = Path(__file__).parent.parent.parent / 'data' / 'bond'
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def get_all_bonds(self, save_path: str = None) -> pd.DataFrame:
        """获取所有可转债列表

        参数
        - save_path: 可选 CSV 保存路径

        返回
        - DataFrame：基础信息字段包含 `bond_id, bond_name, listing_date, issue_size, credit_rating`
        """
        try:
            bond_df = ak.bond_zh_cov()
            bond_df = bond_df[['债券代码', '债券简称', '上市时间', '发行规模', '信用评级']]
            bond_df = bond_df.rename(columns={
                '债券代码': 'bond_id',
                '债券简称': 'bond_name',
                '上市时间': 'listing_date',
                '发行规模': 'issue_size',
                '信用评级': 'credit_rating'
            })
            bond_df = bond_df[bond_df['listing_date'].notna() & (bond_df['listing_date'] != '')]

            if save_path:
                save_dir = os.path.dirname(save_path)
                if save_dir and not os.path.exists(save_dir):
                    os.makedirs(save_dir)
                bond_df.to_csv(save_path, index=False, encoding='utf-8-sig')

            return bond_df
        except Exception as e:
            print(f"Error getting bonds: {str(e)}")
            return pd.DataFrame()

    def fetch_bond_data(self, symbol: str, start_date: str = None, end_date: str = None, save_csv: bool = True) -> pd.DataFrame:
        """获取单券历史行情（日频）

        参数
        - symbol: 债券代码（11* 为上交所，12* 为深交所）
        - start_date: 起始日期（YYYY-MM-DD，默认近 180 天）
        - end_date: 结束日期（YYYY-MM-DD，默认当天）
        - save_csv: 是否保存到 CSV（`data/bond/csv/`）

        返回
        - DataFrame：按日期索引的 OHLC 数据
        """
        if start_date is None:
            start_date = (datetime.now() - timedelta(days=180)).strftime('%Y-%m-%d')
        if end_date is None:
            end_date = datetime.now().strftime('%Y-%m-%d')

        try:
            if symbol.startswith('11'):
                symbol_prefixed = f"sh{symbol}"
            elif symbol.startswith('12'):
                symbol_prefixed = f"sz{symbol}"
            else:
                raise ValueError(f"Unsupported bond code: {symbol}")

            df = ak.bond_zh_hs_cov_daily(symbol=symbol_prefixed)
            if df.empty:
                return pd.DataFrame()

            df = df[['date', 'open', 'high', 'low', 'close']]
            df['date'] = pd.to_datetime(df['date'])
            df = df.sort_values('date')
            df = df[(df['date'] >= pd.to_datetime(start_date)) & (df['date'] <= pd.to_datetime(end_date))]
            df.set_index('date', inplace=True)

            if save_csv:
                csv_dir = self.data_dir / 'csv'
                csv_dir.mkdir(parents=True, exist_ok=True)
                save_path = csv_dir / f"{symbol}_{end_date}.csv"
                df.to_csv(save_path, encoding='utf-8-sig')

            return df
        except Exception as e:
            print(f"Error fetching bond data: {str(e)}")
            return pd.DataFrame()
