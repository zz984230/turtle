import pandas as pd
import numpy as np
import pandas_ta as ta  # 使用 pandas-ta 作为 ta-lib 的纯 Python 替代

class TurtleStrategy:
    """海龟交易策略的面向对象实现"""

    def __init__(self, entry_length=20, exit_length=10, atr_period=14, risk_per_trade=0.02,
                 initial_stop_atr_multiple=2, pyramid_atr_multiple=0.5, max_units=4,
                 mode='Mode 1', entry_length_mode2=55, exit_length_mode2=20):
        """
        初始化策略参数
        :param entry_length: 系统1进场长度
        :param exit_length: 系统1出场长度
        :param atr_period: ATR周期
        :param risk_per_trade: 每笔交易风险比例
        :param initial_stop_atr_multiple: 初始止损ATR倍数
        :param pyramid_atr_multiple: 加仓ATR倍数
        :param max_units: 最大头寸单位数
        :param mode: 'Mode 1' 或 'Mode 2'
        :param entry_length_mode2: 系统2进场长度
        :param exit_length_mode2: 系统2出场长度
        """
        self.entry_length = entry_length
        self.exit_length = exit_length
        self.atr_period = atr_period
        self.risk_per_trade = risk_per_trade
        self.initial_stop_atr_multiple = initial_stop_atr_multiple
        self.pyramid_atr_multiple = pyramid_atr_multiple
        self.max_units = max_units
        self.mode = mode
        self.entry_length_mode2 = entry_length_mode2
        self.exit_length_mode2 = exit_length_mode2

        # 内部状态
        self.units = 0
        self.trailing_stop_long = np.nan
        self.trailing_stop_short = np.nan
        self.real_entry_price_long = np.nan
        self.real_entry_price_short = np.nan
        self.add_unit_price_long = np.nan
        self.add_unit_price_short = np.nan
        self.last_trade_win = False
        self.position = 0  # 0: 无仓位, 1: 多头, -1: 空头
        self.avg_price = np.nan

    def compute_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        计算策略所需指标
        :param data: DataFrame with 'high', 'low', 'close' columns
        :return: DataFrame with added indicators
        """
        df = data.copy()

        # 计算ATR
        df['atr'] = ta.volatility.atr(df['high'], df['low'], df['close'], window=self.atr_period)

        # 根据模式计算进出场价格
        if self.mode == 'Mode 1':
            df['entry_long'] = df['high'].rolling(window=self.entry_length).max()
            df['entry_short'] = df['low'].rolling(window=self.entry_length).min()
            df['exit_long'] = df['low'].rolling(window=self.exit_length).min()
            df['exit_short'] = df['high'].rolling(window=self.exit_length).max()
        else:
            df['entry_long'] = df['high'].rolling(window=self.entry_length_mode2).max()
            df['entry_short'] = df['low'].rolling(window=self.entry_length_mode2).min()
            df['exit_long'] = df['low'].rolling(window=self.exit_length_mode2).min()
            df['exit_short'] = df['high'].rolling(window=self.exit_length_mode2).max()

        return df

    def generate_signals(self, df: pd.DataFrame, equity: float) -> pd.DataFrame:
        """
        生成交易信号
        :param df: DataFrame with indicators
        :param equity: 当前权益
        :return: DataFrame with signals ('signal': 'long', 'short', 'exit', 'add', 'stop')
        """
        df['signal'] = None

        for i in range(1, len(df)):
            close = df['close'].iloc[i]
            prev_close = df['close'].iloc[i-1]
            atr = df['atr'].iloc[i]
            entry_long = df['entry_long'].iloc[i-1]
            entry_short = df['entry_short'].iloc[i-1]
            exit_long = df['exit_long'].iloc[i-1]
            exit_short = df['exit_short'].iloc[i-1]

            # 单位大小
            unit_size = (equity * self.risk_per_trade) / (self.initial_stop_atr_multiple * atr) if atr > 0 else 0

            # 模式信号（Mode 1 跳过失败交易）
            mode_signal = self.last_trade_win or self.mode != 'Mode 1'

            # 长信号
            if self.position == 0 and prev_close <= entry_long < close and mode_signal:
                df.at[df.index[i], 'signal'] = 'long'
                self.position = 1
                self.units = 1
                self.avg_price = close
                self.real_entry_price_long = close
                self.add_unit_price_long = close + self.pyramid_atr_multiple * atr
                self.trailing_stop_long = close - self.initial_stop_atr_multiple * atr
                self.last_trade_win = False  # 重置为等待下次

            # 短信号
            elif self.position == 0 and prev_close >= entry_short > close and mode_signal:
                df.at[df.index[i], 'signal'] = 'short'
                self.position = -1
                self.units = 1
                self.avg_price = close
                self.real_entry_price_short = close
                self.add_unit_price_short = close - self.pyramid_atr_multiple * atr
                self.trailing_stop_short = close + self.initial_stop_atr_multiple * atr
                self.last_trade_win = False

            # 退出长
            elif self.position > 0 and prev_close >= exit_long > close:
                df.at[df.index[i], 'signal'] = 'exit'
                self.last_trade_win = self.avg_price < close
                self._reset_state()

            # 退出短
            elif self.position < 0 and prev_close <= exit_short < close:
                df.at[df.index[i], 'signal'] = 'exit'
                self.last_trade_win = self.avg_price > close
                self._reset_state()

            # 加仓
            if self.units < self.max_units:
                if self.position > 0 and close > self.add_unit_price_long:
                    df.at[df.index[i], 'signal'] = 'add_long'
                    self.units += 1
                    self.avg_price = (self.avg_price * (self.units - 1) + close) / self.units
                    self.real_entry_price_long = close
                    self.add_unit_price_long = close + self.pyramid_atr_multiple * atr
                    self.trailing_stop_long = close - self.initial_stop_atr_multiple * atr

                elif self.position < 0 and close < self.add_unit_price_short:
                    df.at[df.index[i], 'signal'] = 'add_short'
                    self.units += 1
                    self.avg_price = (self.avg_price * (self.units - 1) + close) / self.units
                    self.real_entry_price_short = close
                    self.add_unit_price_short = close - self.pyramid_atr_multiple * atr
                    self.trailing_stop_short = close + self.initial_stop_atr_multiple * atr

            # 止损
            if self.position > 0 and close < self.trailing_stop_long:
                df.at[df.index[i], 'signal'] = 'stop_long'
                self.last_trade_win = self.avg_price < close
                self._reset_state()

            elif self.position < 0 and close > self.trailing_stop_short:
                df.at[df.index[i], 'signal'] = 'stop_short'
                self.last_trade_win = self.avg_price > close
                self._reset_state()

        return df

    def _reset_state(self):
        """重置内部状态"""
        self.units = 0
        self.position = 0
        self.trailing_stop_long = np.nan
        self.trailing_stop_short = np.nan
        self.real_entry_price_long = np.nan
        self.real_entry_price_short = np.nan
        self.add_unit_price_long = np.nan
        self.add_unit_price_short = np.nan
        self.avg_price = np.nan
