# 策略分析示例

调试策略可能很耗时。Freqtrade 提供了辅助函数来可视化原始数据。
以下假设您使用 SampleStrategy，来自 Binance 的 5m 时间框架数据，并已将它们下载到默认位置的数据目录中。
请参考[文档](https://www.freqtrade.io/en/stable/data-download/)了解更多详情。

## 设置

### 将工作目录更改为仓库根目录

```python
import os
from pathlib import Path

# 更改目录
# 修改此单元格以确保输出显示正确的路径。
# 定义相对于单元格输出中显示的项目根目录的所有路径
project_root = "somedir/freqtrade"
i = 0
try:
    os.chdir(project_root)
    if not Path("LICENSE").is_file():
        i = 0
        while i < 4 and (not Path("LICENSE").is_file()):
            os.chdir(Path(Path.cwd(), "../"))
            i += 1
        project_root = Path.cwd()
except FileNotFoundError:
    print("请定义相对于当前目录的项目根目录")
print(Path.cwd())
```

### 配置 Freqtrade 环境

```python
from freqtrade.configuration import Configuration

# 根据您的需要自定义这些。

# 初始化空配置对象
config = Configuration.from_files([])
# 可选（推荐），使用现有配置文件
# config = Configuration.from_files(["user_data/config.json"])

# 定义一些常量
config["timeframe"] = "5m"
# 注意：确保您的配置包含交易所名称！
config["exchange"] = {
    "name": "binance",
    "sandbox": False,
    "pair_whitelist": ["BTC/USDT"],
    "ccxt_config": {"enableRateLimit": True},
    "ccxt_async_config": {
        "enableRateLimit": True,
        "rateLimit": 200
    }
}
config["stake_currency"] = "USDT"
config["stake_amount"] = 1000
config["dry_run"] = True
config["cancel_open_orders_on_exit"] = False
config["trading_mode"] = "spot"
config["margin_mode"] = ""
```

### 加载数据

```python
from freqtrade.data.history import load_pair_history
from freqtrade.resolvers import ExchangeResolver

# 加载数据
exchange = ExchangeResolver.load_exchange(config["exchange"]["name"], config, validate=False)
data = load_pair_history(datadir=config.get("datadir"),
                        timeframe=config["timeframe"],
                        pair="BTC/USDT",
                        data_format = config.get("dataformat_ohlcv", "json"),
                        candle_type=config.get("candle_type_def", CandleType.SPOT)
                        )

# 确认我们有数据
print("从 {} 到 {} 加载了 {} 行数据".format(data.iloc[0]['date'], data.iloc[-1]['date'], len(data)))
print(data.head())
```

### 加载和配置策略

```python
from freqtrade.resolvers import StrategyResolver
from freqtrade.data.dataprovider import DataProvider

# 加载策略 - 这必须与您的策略名称匹配
strategy = StrategyResolver.load_strategy(config)
strategy.dp = DataProvider(config, exchange, None)

# 生成买入/卖出信号
df = strategy.analyze_ticker(data, {'pair': 'BTC/USDT'})
print(df.columns)
```

## 分析策略性能

### 基本统计信息

```python
import pandas as pd

# 计算基本统计信息
print("=== 数据概览 ===")
print(f"数据点数量: {len(df)}")
print(f"时间范围: {df['date'].min()} 到 {df['date'].max()}")
print(f"价格范围: {df['close'].min():.2f} - {df['close'].max():.2f}")

# 检查买入/卖出信号
buy_signals = df[df['enter_long'] == 1]
sell_signals = df[df['exit_long'] == 1]

print(f"\n=== 信号统计 ===")
print(f"买入信号数量: {len(buy_signals)}")
print(f"卖出信号数量: {len(sell_signals)}")
print(f"买入信号频率: {len(buy_signals)/len(df)*100:.2f}%")
print(f"卖出信号频率: {len(sell_signals)/len(df)*100:.2f}%")
```

### 可视化策略信号

```python
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime

# 设置图形大小
plt.figure(figsize=(15, 10))

# 绘制价格数据
plt.subplot(2, 1, 1)
plt.plot(df['date'], df['close'], label='收盘价', linewidth=1)

# 标记买入信号
buy_points = df[df['enter_long'] == 1]
plt.scatter(buy_points['date'], buy_points['close'], 
           color='green', marker='^', s=100, label='买入信号', zorder=5)

# 标记卖出信号
sell_points = df[df['exit_long'] == 1]
plt.scatter(sell_points['date'], sell_points['close'], 
           color='red', marker='v', s=100, label='卖出信号', zorder=5)

plt.title('BTC/USDT 价格和交易信号')
plt.xlabel('日期')
plt.ylabel('价格 (USDT)')
plt.legend()
plt.grid(True, alpha=0.3)

# 绘制成交量
plt.subplot(2, 1, 2)
plt.bar(df['date'], df['volume'], alpha=0.7, label='成交量')
plt.title('成交量')
plt.xlabel('日期')
plt.ylabel('成交量')
plt.legend()
plt.grid(True, alpha=0.3)

plt.tight_layout()
plt.show()
```

### 分析指标

```python
# 分析策略使用的指标
print("=== 可用指标 ===")
indicator_columns = [col for col in df.columns if col not in ['date', 'open', 'high', 'low', 'close', 'volume', 'enter_long', 'exit_long']]
print(f"指标数量: {len(indicator_columns)}")
print("指标列表:")
for col in indicator_columns:
    print(f"  - {col}")

# 绘制主要指标
if 'rsi' in df.columns:
    plt.figure(figsize=(15, 8))
    
    plt.subplot(2, 1, 1)
    plt.plot(df['date'], df['close'], label='收盘价')
    if 'sma' in df.columns:
        plt.plot(df['date'], df['sma'], label='SMA', alpha=0.7)
    if 'ema' in df.columns:
        plt.plot(df['date'], df['ema'], label='EMA', alpha=0.7)
    plt.title('价格和移动平均线')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    plt.subplot(2, 1, 2)
    plt.plot(df['date'], df['rsi'], label='RSI')
    plt.axhline(y=70, color='r', linestyle='--', alpha=0.7, label='超买线 (70)')
    plt.axhline(y=30, color='g', linestyle='--', alpha=0.7, label='超卖线 (30)')
    plt.title('RSI 指标')
    plt.ylabel('RSI')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.show()
```

## 回测结果分析

### 加载回测结果

```python
from freqtrade.data.btanalysis import load_backtest_data, load_backtest_stats

# 加载回测结果（假设您已经运行了回测）
try:
    backtest_dir = "user_data/backtest_results"
    trades = load_backtest_data(backtest_dir)
    stats = load_backtest_stats(backtest_dir)
    
    print("=== 回测结果概览 ===")
    print(f"总交易数: {len(trades)}")
    print(f"盈利交易: {len(trades[trades['profit_ratio'] > 0])}")
    print(f"亏损交易: {len(trades[trades['profit_ratio'] < 0])}")
    print(f"胜率: {len(trades[trades['profit_ratio'] > 0]) / len(trades) * 100:.2f}%")
    print(f"平均利润: {trades['profit_ratio'].mean() * 100:.2f}%")
    print(f"总利润: {trades['profit_abs'].sum():.2f} USDT")
    
except Exception as e:
    print(f"无法加载回测结果: {e}")
    print("请先运行回测以生成结果数据")
```

### 交易分析

```python
if 'trades' in locals():
    # 按时间分析交易
    trades['open_date'] = pd.to_datetime(trades['open_date'])
    trades['close_date'] = pd.to_datetime(trades['close_date'])
    
    # 绘制交易利润分布
    plt.figure(figsize=(15, 10))
    
    plt.subplot(2, 2, 1)
    plt.hist(trades['profit_ratio'] * 100, bins=30, alpha=0.7, edgecolor='black')
    plt.title('利润分布')
    plt.xlabel('利润 (%)')
    plt.ylabel('交易数量')
    plt.grid(True, alpha=0.3)
    
    plt.subplot(2, 2, 2)
    trades['profit_ratio'].cumsum().plot()
    plt.title('累积利润')
    plt.xlabel('交易序号')
    plt.ylabel('累积利润比率')
    plt.grid(True, alpha=0.3)
    
    plt.subplot(2, 2, 3)
    trades.set_index('close_date')['profit_abs'].resample('D').sum().plot()
    plt.title('每日利润')
    plt.xlabel('日期')
    plt.ylabel('利润 (USDT)')
    plt.grid(True, alpha=0.3)
    
    plt.subplot(2, 2, 4)
    trades['trade_duration'].hist(bins=30, alpha=0.7, edgecolor='black')
    plt.title('交易持续时间分布')
    plt.xlabel('持续时间 (分钟)')
    plt.ylabel('交易数量')
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.show()
```

## 高级分析

### 信号质量分析

```python
# 分析买入信号的质量
def analyze_signal_quality(df, signal_col='enter_long', price_col='close', periods=[1, 5, 10, 20]):
    """分析信号后的价格变化"""
    signals = df[df[signal_col] == 1].copy()
    
    for period in periods:
        future_returns = []
        for idx in signals.index:
            if idx + period < len(df):
                current_price = df.loc[idx, price_col]
                future_price = df.loc[idx + period, price_col]
                return_pct = (future_price - current_price) / current_price * 100
                future_returns.append(return_pct)
            else:
                future_returns.append(None)
        
        signals[f'return_{period}p'] = future_returns
    
    return signals

# 分析买入信号质量
signal_analysis = analyze_signal_quality(df)

print("=== 买入信号质量分析 ===")
for period in [1, 5, 10, 20]:
    col = f'return_{period}p'
    if col in signal_analysis.columns:
        returns = signal_analysis[col].dropna()
        if len(returns) > 0:
            print(f"{period} 个周期后:")
            print(f"  平均收益: {returns.mean():.2f}%")
            print(f"  正收益比例: {(returns > 0).mean() * 100:.1f}%")
            print(f"  最大收益: {returns.max():.2f}%")
            print(f"  最大亏损: {returns.min():.2f}%")
```

### 策略参数敏感性分析

```python
# 如果策略有可调参数，可以进行敏感性分析
def parameter_sensitivity_analysis(strategy_class, data, param_name, param_values):
    """分析参数对策略性能的影响"""
    results = []
    
    for value in param_values:
        # 创建策略实例并设置参数
        strategy = strategy_class()
        setattr(strategy, param_name, value)
        
        # 分析数据
        df_test = strategy.analyze_ticker(data, {'pair': 'BTC/USDT'})
        
        # 计算信号数量
        buy_signals = len(df_test[df_test['enter_long'] == 1])
        sell_signals = len(df_test[df_test['exit_long'] == 1])
        
        results.append({
            'parameter_value': value,
            'buy_signals': buy_signals,
            'sell_signals': sell_signals,
            'signal_ratio': buy_signals / len(df_test) if len(df_test) > 0 else 0
        })
    
    return pd.DataFrame(results)

# 示例：如果策略有 RSI 参数
# sensitivity_results = parameter_sensitivity_analysis(SampleStrategy, data, 'rsi_period', range(10, 31, 2))
# print(sensitivity_results)
```

## 总结和建议

### 策略优化建议

```python
print("=== 策略分析总结 ===")
print("\n1. 信号频率分析:")
print(f"   - 买入信号过于频繁可能导致过度交易")
print(f"   - 买入信号过少可能错失机会")
print(f"   - 当前买入信号频率: {len(buy_signals)/len(df)*100:.2f}%")

print("\n2. 信号质量检查:")
print(f"   - 检查买入信号后的短期表现")
print(f"   - 验证卖出信号的及时性")
print(f"   - 考虑添加额外的过滤条件")

print("\n3. 风险管理:")
print(f"   - 确保有适当的止损机制")
print(f"   - 考虑头寸规模管理")
print(f"   - 监控最大回撤")

print("\n4. 进一步优化:")
print(f"   - 使用超参数优化寻找最佳参数")
print(f"   - 在不同市场条件下测试策略")
print(f"   - 考虑添加更多技术指标")
```

这个策略分析示例提供了一个完整的框架来分析和调试您的 Freqtrade 策略。通过这些分析，您可以：

1. **理解策略行为** - 查看信号生成的频率和质量
2. **识别问题** - 发现策略中的潜在问题
3. **优化参数** - 通过敏感性分析找到最佳参数
4. **验证性能** - 通过回测结果验证策略效果

记住，策略分析是一个迭代过程。使用这些工具持续改进您的策略，并始终在实盘部署前进行充分的测试。
