# 高级回测分析

## 分析买入/入场和卖出/出场标签

了解策略根据用于标记不同买入条件的买入/入场标签的行为可能很有帮助。您可能希望看到关于每个买入和卖出条件的更复杂的统计信息，而不仅仅是默认回测输出提供的信息。您可能还想确定导致交易开启的信号蜡烛图上的指标值。

!!! Note
    以下买入原因分析仅适用于回测，*不适用于超参数优化*。

我们需要运行回测，将 `--export` 选项设置为 `signals` 以启用信号**和**交易的导出：

``` bash
freqtrade backtesting -c <config.json> --timeframe <tf> --strategy <strategy_name> --timerange=<timerange> --export=signals
```

这将告诉 freqtrade 输出一个包含策略、交易对和相应导致入场和出场信号的蜡烛图数据框的 pickled 字典。
根据您的策略进行多少次入场，此文件可能会变得相当大，因此请定期检查您的 `user_data/backtest_results` 文件夹以删除旧的导出。

在运行下一次回测之前，请确保您要么删除旧的回测结果，要么使用 `--cache none` 选项运行回测，以确保不使用缓存的结果。

如果一切顺利，您现在应该在 `user_data/backtest_results` 文件夹中看到 `backtest-result-{timestamp}_signals.pkl` 和 `backtest-result-{timestamp}_exited.pkl` 文件。

要分析入场/出场标签，我们现在需要使用 `freqtrade backtesting-analysis` 命令，并提供 `--analysis-groups` 选项，该选项提供空格分隔的参数：

``` bash
freqtrade backtesting-analysis -c <config.json> --analysis-groups 0 1 2 3 4 5
```

此命令将从最后的回测结果中读取。`--analysis-groups` 选项用于指定显示每个组或交易利润的各种表格输出，从最简单的 (0) 到按交易对、买入和卖出标签最详细的 (4)：

* 0: 按 enter_tag 的总体胜率和利润摘要
* 1: 按 enter_tag 分组的利润摘要
* 2: 按 enter_tag 和 exit_tag 分组的利润摘要
* 3: 按交易对和 enter_tag 分组的利润摘要
* 4: 按交易对、enter_ 和 exit_tag 分组的利润摘要（这可能会变得相当大）
* 5: 按 exit_tag 分组的利润摘要

通过使用 `-h` 选项运行可以获得更多选项。

### 使用 export-filename

通常，`backtesting-analysis` 使用最新的回测结果，但如果您想回到以前的回测输出，您需要提供 `--export-filename` 选项。
您可以向 `backtest-analysis` 提供相同的参数，并使用最终回测输出文件的名称。这允许您保留回测结果的历史版本并在以后重新分析它们：

``` bash
freqtrade backtesting -c <config.json> --timeframe <tf> --strategy <strategy_name> --timerange=<timerange> --export=signals --export-filename=/tmp/mystrat_backtest.json
```

您应该在日志中看到类似下面的输出，其中包含导出的时间戳文件名：

```
2022-06-14 16:28:32,698 - freqtrade.misc - INFO - dumping json to "/tmp/mystrat_backtest-2022-06-14_16-28-32.json"
```

然后您可以在 `backtesting-analysis` 中使用该文件名：

```
freqtrade backtesting-analysis -c <config.json> --export-filename=/tmp/mystrat_backtest-2022-06-14_16-28-32.json
```

### 调整要显示的买入标签和卖出标签

要在显示的输出中仅显示某些买入和卖出标签，请使用以下两个选项：

```
--enter-reason-list : 要分析的入场信号的空格分隔列表。默认："all"
--exit-reason-list : 要分析的出场信号的空格分隔列表。默认："all"
```

例如：

```bash
freqtrade backtesting-analysis -c <config.json> --analysis-groups 0 2 --enter-reason-list enter_tag_a enter_tag_b --exit-reason-list roi custom_exit_tag_a stop_loss
```

### 输出信号蜡烛图指标

`freqtrade backtesting-analysis` 的真正威力来自于能够打印出信号蜡烛图上存在的指标值，以允许对买入信号指标进行细粒度调查和调整。要为给定的指标集打印出一列，请使用 `--indicator-list` 选项：

```bash
freqtrade backtesting-analysis -c <config.json> --analysis-groups 0 2 --enter-reason-list enter_tag_a enter_tag_b --exit-reason-list roi custom_exit_tag_a stop_loss --indicator-list rsi rsi_1h bb_lowerband ema_9 macd macdsignal
```

指标必须存在于您策略的主数据框中（无论是您的主时间框架还是信息时间框架）。

## 回测结果缓存

为了提高回测性能，freqtrade 可以缓存回测结果。这在您想要使用不同的分析选项重新分析相同的回测时特别有用。

### 缓存选项

```bash
# 使用默认缓存（按天）
freqtrade backtesting -c config.json --strategy MyStrategy

# 禁用缓存
freqtrade backtesting -c config.json --strategy MyStrategy --cache none

# 使用不同的缓存级别
freqtrade backtesting -c config.json --strategy MyStrategy --cache week
```

可用的缓存选项：
- `none`: 禁用缓存
- `day`: 按天缓存（默认）
- `week`: 按周缓存
- `month`: 按月缓存

### 缓存位置

缓存文件存储在 `user_data/backtest_results/.bt_cache/` 目录中。

## 多策略回测

您可以同时回测多个策略：

```bash
freqtrade backtesting -c config.json --strategy-list Strategy1 Strategy2 Strategy3
```

这将为每个策略生成单独的结果文件。

## 回测结果比较

### 使用 backtesting-analysis 比较

```bash
# 比较不同策略的结果
freqtrade backtesting-analysis -c config.json --export-filename results1.json --export-filename results2.json
```

### 手动比较

您可以使用 Python 脚本手动比较回测结果：

```python
import json
import pandas as pd

# 加载回测结果
with open('user_data/backtest_results/backtest-result-1.json', 'r') as f:
    results1 = json.load(f)

with open('user_data/backtest_results/backtest-result-2.json', 'r') as f:
    results2 = json.load(f)

# 比较关键指标
print("策略1总利润:", results1['strategy']['TestStrategy']['results_metrics']['profit_total'])
print("策略2总利润:", results2['strategy']['TestStrategy']['results_metrics']['profit_total'])
```

## 高级分析技巧

### 1. 时间段分析

分析不同时间段的表现：

```bash
freqtrade backtesting-analysis -c config.json --timerange 20230101-20230301
freqtrade backtesting-analysis -c config.json --timerange 20230301-20230601
```

### 2. 交易对分析

分析特定交易对的表现：

```bash
freqtrade backtesting-analysis -c config.json --pairs BTC/USDT ETH/USDT
```

### 3. 风险分析

计算最大回撤、夏普比率等风险指标：

```python
import numpy as np
import pandas as pd

def calculate_sharpe_ratio(returns, risk_free_rate=0):
    """计算夏普比率"""
    excess_returns = returns - risk_free_rate
    return np.mean(excess_returns) / np.std(excess_returns) * np.sqrt(252)

def calculate_max_drawdown(equity_curve):
    """计算最大回撤"""
    peak = equity_curve.expanding().max()
    drawdown = (equity_curve - peak) / peak
    return drawdown.min()
```

### 4. 季节性分析

分析策略在不同月份或季节的表现：

```python
# 按月份分组分析
monthly_returns = trades_df.groupby(trades_df['close_date'].dt.month)['profit_ratio'].mean()
print("月度平均收益率:")
print(monthly_returns)
```

## 性能优化

### 1. 并行回测

使用多进程加速回测：

```bash
freqtrade backtesting -c config.json --strategy MyStrategy --jobs 4
```

### 2. 内存优化

对于大数据集，考虑：
- 减少时间范围
- 使用较大的时间框架
- 限制交易对数量

### 3. 数据预处理

预先下载和准备数据：

```bash
freqtrade download-data -c config.json --days 365
```

## 故障排除

### 常见问题

1. **内存不足**
   - 减少回测时间范围
   - 使用较少的交易对
   - 增加系统内存

2. **回测速度慢**
   - 启用缓存
   - 使用并行处理
   - 优化策略代码

3. **结果不一致**
   - 检查数据质量
   - 验证策略逻辑
   - 确保时间同步

### 调试技巧

- 使用 `--log-level debug` 获取详细日志
- 检查策略的 `populate_indicators` 方法
- 验证入场和出场条件
- 使用小数据集进行测试
