"""命令行入口

提供基础运行模式：回测/实时，当前支持债券资产的数据获取与海龟策略信号演示。
"""

import argparse
import pandas as pd
from app.bond.bond_data import BondData
from app.turtle_algo.turtle_strategy import TurtleStrategy

def main():
    """命令行主函数

    参数（通过 CLI 传入）
    - asset: 资产类型（bond/stock/etf）
    - symbol: 资产代码
    - mode: 运行模式（backtest/live）
    - equity: 初始权益
    """
    parser = argparse.ArgumentParser(description="Turtle Trading System")
    parser.add_argument("--asset", type=str, default="bond", choices=["bond", "stock", "etf"], help="资产类型")
    parser.add_argument("--symbol", type=str, required=True, help="资产代码")
    parser.add_argument("--mode", type=str, default="backtest", choices=["backtest", "live"], help="运行模式")
    parser.add_argument("--equity", type=float, default=10000.0, help="初始权益")

    args = parser.parse_args()

    # 数据获取
    if args.asset == "bond":
        data_handler = BondData()
        data = data_handler.fetch_bond_data(args.symbol)
    else:
        # TODO: 实现股票和ETF数据获取
        print(f"{args.asset} 数据获取尚未实现")
        return

    if data.empty:
        print("无法获取数据")
        return

    # 策略初始化
    strategy = TurtleStrategy()

    # 计算指标
    df = strategy.compute_indicators(data)

    # 生成信号（对于回测，使用固定权益；实时可动态更新）
    signals = strategy.generate_signals(df, args.equity)

    if args.mode == "backtest":
        # 简单回测逻辑：打印信号
        print("回测信号：")
        print(signals[signals['signal'].notna()])
    elif args.mode == "live":
        # 实时模式：监控最新信号
        latest_signal = signals['signal'].iloc[-1]
        print(f"实时信号: {latest_signal if latest_signal else '无信号'}")

if __name__ == "__main__":
    main()
