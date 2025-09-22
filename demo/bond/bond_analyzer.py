import akshare as ak
import pandas as pd
import numpy as np
import mplfinance as mpf
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from typing import Optional
from pathlib import Path
import os

class BondAnalyzer:
    def __init__(self, symbol: str, data_dir: Optional[str] = None, name: Optional[str] = None, save_csv: bool = True):
        """
        初始化可转债分析器
        
        参数:
        symbol: str, 可转债代码
        data_dir: str, 可选，数据存储目录
        name: str, 可选，可转债名称，用于图表展示
        save_csv: bool, 是否保存从akshare获取的历史数据到CSV文件
        """
        self.symbol = symbol
        self.data = None
        self.indicator_data = None
        self.name = name or symbol  # 如果没有提供名称，则使用代码
        self.save_csv = save_csv
        
        # 设置数据目录
        if data_dir is None:
            data_dir = Path(__file__).parent.parent.parent / 'data'
        self.data_dir = Path(data_dir) / 'bond'
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # 设置字体
        self.font = self._setup_chinese_font()
        
    def _setup_chinese_font(self):
        """设置中文字体"""
        # 设置matplotlib的字体
        plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
        plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号
        return plt.rcParams['font.sans-serif'][0]
        
    def set_name(self, name: str):
        """设置可转债名称"""
        self.name = name
        
    def _get_data_path(self, date: str) -> Path:
        """获取数据文件路径"""
        csv_dir = self.data_dir / 'csv'
        csv_dir.mkdir(parents=True, exist_ok=True)
        return csv_dir / f"{self.symbol}_{date}.csv"
        
    def fetch_data(self, start_date: Optional[str] = None, end_date: Optional[str] = None) -> pd.DataFrame:
        """
        获取可转债数据
        
        参数:
        start_date: str, 开始日期，格式：'YYYY-MM-DD'
        end_date: str, 结束日期，格式：'YYYY-MM-DD'
        
        返回:
        DataFrame: 包含OHLC数据的DataFrame
        """
        if start_date is None:
            start_date = (datetime.now() - timedelta(days=180)).strftime('%Y-%m-%d')
        if end_date is None:
            end_date = datetime.now().strftime('%Y-%m-%d')
            
        try:
            # 添加交易所前缀
            if self.symbol.startswith('11'):
                symbol = f"sh{self.symbol}"  # 上交所可转债
            elif self.symbol.startswith('12'):
                symbol = f"sz{self.symbol}"  # 深交所可转债
            else:
                # 尝试根据代码前缀判断交易所
                if len(self.symbol) == 6:
                    if self.symbol.startswith('1'):
                        symbol = f"sh{self.symbol}"
                    else:
                        symbol = f"sz{self.symbol}"
                else:
                    raise ValueError(f"不支持的可转债代码格式: {self.symbol}")
            
            try:
                df = ak.bond_zh_hs_cov_daily(symbol=symbol)
                print("原始数据列名:", df.columns.tolist())
                print("数据预览:")
                print(df.head())
                
                # 检查数据是否为空
                if df.empty:
                    print(f"获取到的数据为空，可能是代码 {self.symbol} 不正确或不存在")
                    return None
                    
                # 检查必要的列是否存在
                required_columns = ['date', 'open', 'high', 'low', 'close']
                for col in required_columns:
                    if col not in df.columns:
                        print(f"数据中缺少必要的列: {col}")
                        return None
                
                # 重命名列以匹配需求（如果需要的话）
                df = df.rename(columns={
                    'date': 'date',
                    'open': 'open',
                    'high': 'high',
                    'low': 'low',
                    'close': 'close'
                })
                
            except Exception as e:
                print(f"获取可转债数据失败，尝试其他接口: {str(e)}")
                # 尝试使用ETF接口作为备选
                try:
                    df = ak.bond_cov_comparison()
                    # 查找对应的可转债数据
                    df = df[df['转债代码'] == self.symbol]
                    if df.empty:
                        print(f"在可转债列表中未找到代码: {self.symbol}")
                        return None
                        
                    # 获取详细数据（这里需要根据实际API调整）
                    df = pd.DataFrame({
                        'date': pd.date_range(start=start_date, end=end_date, freq='B'),
                        'open': [float(df['转债现价'].iloc[0])] * len(pd.date_range(start=start_date, end=end_date, freq='B')),
                        'high': [float(df['转债现价'].iloc[0])] * len(pd.date_range(start=start_date, end=end_date, freq='B')),
                        'low': [float(df['转债现价'].iloc[0])] * len(pd.date_range(start=start_date, end=end_date, freq='B')),
                        'close': [float(df['转债现价'].iloc[0])] * len(pd.date_range(start=start_date, end=end_date, freq='B')),
                        'volume': [0] * len(pd.date_range(start=start_date, end=end_date, freq='B'))
                    })
                except Exception as e2:
                    print(f"备选接口也失败了: {str(e2)}")
                    return None
            
            # 确保数据类型正确
            df['open'] = pd.to_numeric(df['open'])
            df['high'] = pd.to_numeric(df['high'])
            df['low'] = pd.to_numeric(df['low'])
            df['close'] = pd.to_numeric(df['close'])
            
            # 按日期排序
            df['date'] = pd.to_datetime(df['date'])
            df = df.sort_values('date')
            
            # 过滤日期范围
            df = df[(df['date'] >= pd.to_datetime(start_date)) & (df['date'] <= pd.to_datetime(end_date))]
            
            # 确保日期列是datetime类型
            df['date'] = pd.to_datetime(df['date'])
            df.set_index('date', inplace=True)
            
            # 保存数据（如果启用）
            if self.save_csv:
                try:
                    save_path = self._get_data_path(end_date)
                    df.to_csv(save_path, encoding='utf-8-sig')
                    print(f"数据已保存到: {save_path}")
                except Exception as e:
                    print(f"保存数据时出错: {str(e)}")
                    # 继续执行，不中断程序
            
            self.data = df
            return df
            
        except Exception as e:
            print(f"获取数据时出错: {str(e)}")
            import traceback
            traceback.print_exc()
            return None
            
    def calculate_main_force_indicator(self) -> pd.DataFrame:
        """
        计算主力资金进出场指标
        
        返回:
        DataFrame: 包含主力进场和洗盘信号的DataFrame
        """
        if self.data is None:
            raise ValueError("请先调用fetch_data()获取数据")
            
        df = self.data.copy()
        
        # VAR1: 典型价格的前一日值
        typical_price = (df['low'] + df['open'] + df['close'] + df['high']) / 4
        df['VAR1'] = typical_price.shift(1)
        
        # VAR2: 计算比率
        abs_diff = abs(df['low'] - df['VAR1'])
        max_diff = np.maximum(df['low'] - df['VAR1'], 0)
        
        def sma(series, periods, weight):
            """简单移动平均"""
            weights = np.repeat(weight, periods)
            return series.rolling(window=periods).apply(
                lambda x: np.sum(x * weights) / np.sum(weights)
            )
        
        df['VAR2'] = sma(abs_diff, 13, 1) / sma(max_diff, 10, 1)
        
        # VAR3: 10日EMA
        df['VAR3'] = df['VAR2'].ewm(span=10, adjust=False).mean()
        
        # VAR4: 33日最低价的最小值
        df['VAR4'] = df['low'].rolling(window=33).min()
        
        # VAR5: 条件EMA
        condition = df['low'] <= df['VAR4']
        df['temp'] = np.where(condition, df['VAR3'], 0)
        df['VAR5'] = df['temp'].ewm(span=3, adjust=False).mean()
        
        # 主力进场信号
        df['main_force_entry'] = np.where(
            df['VAR5'] > df['VAR5'].shift(1),
            df['VAR5'],
            0
        )
        
        # 洗盘信号
        df['main_force_washout'] = np.where(
            df['VAR5'] < df['VAR5'].shift(1),
            df['VAR5'],
            0
        )
        
        self.indicator_data = df
        return df[['main_force_entry', 'main_force_washout']]
        
    def plot_chart(self, save_path: Optional[str] = None, save_dir: Optional[str] = None, only_save_with_signal: bool = False):
        """
        绘制K线图和主力资金信号图
        
        参数:
        save_path: str, 可选，保存图片的完整路径
        save_dir: str, 可选，保存图片的目录，如果提供则会在此目录下生成文件名
        only_save_with_signal: bool, 是否只在有主力进场信号时保存图片，默认为False
        """
        if self.indicator_data is None:
            raise ValueError("请先调用calculate_main_force_indicator()计算指标")
            
        # 准备数据
        df = self.indicator_data.copy()
        
        # 筛选最近90天的数据用于绘图
        ninety_days_ago = datetime.now() - timedelta(days=90)
        ninety_days_ago_pd = pd.Timestamp(ninety_days_ago)
        df = df[df.index >= ninety_days_ago_pd]
        
        print(f"使用最近90天的数据进行绘图，数据点数量: {len(df)}")
        
        # 检查最近一周是否存在主力进场信号
        has_signal = False
        if only_save_with_signal:
            # 获取当前日期
            now = datetime.now()
            # 一周前的日期
            week_ago = now - timedelta(days=5)
            
            # 转换为pandas日期格式，用于比较
            week_ago_pd = pd.Timestamp(week_ago)
            
            # 筛选最近一周的数据
            recent_data = df[df.index >= week_ago_pd]
            
            # 检查是否存在主力进场信号
            if len(recent_data) > 0 and (recent_data['main_force_entry'] > 0).any():
                has_signal = True
                print(f"{self.name}({self.symbol}) 最近一周内存在主力进场信号")
            else:
                print(f"{self.name}({self.symbol}) 最近一周内不存在主力进场信号，不保存图片")
                return None
        
        # 创建额外的数据列用于绘图
        df['main_force_entry_volume'] = df['main_force_entry']
        df['main_force_washout_volume'] = df['main_force_washout']
        
        # 设置绘图样式
        style = mpf.make_mpf_style(
            marketcolors=mpf.make_marketcolors(
                up='red',
                down='green',
                edge='inherit',
                wick='inherit',
                volume='inherit'
            ),
            gridstyle='dotted',
            rc={
                'font.family': 'SimHei',
                'axes.unicode_minus': False
            }
        )
        
        # 创建额外的图表
        apds = [
            mpf.make_addplot(df['main_force_entry_volume'], type='bar', color='red', alpha=0.5, panel=1),
            mpf.make_addplot(df['main_force_washout_volume'], type='bar', color='green', alpha=0.5, panel=1)
        ]
        
        # 绘制图表（使用名称+代码作为标题）
        fig, axes = mpf.plot(
            df,
            type='candle',
            style=style,
            addplot=apds,
            panel_ratios=(2, 1),
            volume=False,
            title=f'\n{self.name}({self.symbol})',
            returnfig=True,
            figscale=1.5,
            datetime_format='%Y-%m-%d',  # 设置横坐标日期格式
            xrotation=15  # 设置横坐标标签旋转角度
        )
        
        # 设置标题和图例的字体
        axes[1].legend(['主力进场', '洗盘'], prop=self.font)
        
        # 处理保存路径
        if not save_path:
            # 使用可转债名称作为文件名
            filename = f"{self.name}.png"
            
            if save_dir:
                # 确保目录存在
                save_dir_path = Path(save_dir)
                save_dir_path.mkdir(parents=True, exist_ok=True)
                save_path = save_dir_path / filename
            else:
                save_path = filename
        
        # 检查文件是否已存在，如果存在则删除
        if os.path.exists(save_path):
            try:
                os.remove(save_path)
                print(f"已删除已存在的图表文件: {save_path}")
            except Exception as e:
                print(f"删除已存在的图表文件时出错: {str(e)}")
            
        plt.savefig(save_path)
        print(f"图表已保存至: {save_path}")
        plt.close(fig)
        
        return save_path 