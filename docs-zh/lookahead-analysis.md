# 前瞻性分析

本页面解释如何验证您的策略是否存在前瞻性偏差。

前瞻性偏差是任何策略的祸根，因为有时很容易引入这种偏差，但很难检测到。

回测初始化所有时间戳（将整个数据框加载到内存中）并一次性计算所有指标。
这意味着如果您的指标或入场/出场信号查看未来蜡烛图，这将使您的回测结果失真。

`lookahead-analysis` 命令需要历史数据可用。
要了解如何获取您感兴趣的交易对和交易所的数据，
请转到文档的[数据下载](data-download.md)部分。
`lookahead-analysis` 也支持 freqai 策略。

此命令内部链接回测并戳策略以激发它显示前瞻性偏差。
这不是通过查看策略代码本身来完成的，而是通过与完整回测相比的更改指标值和移动的入场/出场来完成的。

`lookahead-analysis` 可以使用[回测](backtesting.md)的典型选项，但强制以下选项：

- `--cache` 被强制为 "none"。
- `--max-open-trades` 被强制至少等于交易对数量。
- `--dry-run-wallet` 被强制为基本无限（10 亿）。
- `--stake-amount` 被强制为静态 10000（10k）。
- `--enable-protections` 被强制关闭。

这些设置是为了避免用户意外生成误报。

## 前瞻性分析命令参考

--8<-- "commands/lookahead-analysis.md"

!!! Note
    上述输出减少到 `lookahead-analysis` 在常规回测命令之上添加的选项。

### 介绍

许多策略在程序员不知情的情况下已经成为前瞻性偏差的受害者。
这通常使策略回测看起来有利可图，有时达到极端，但这是不现实的，因为策略通过查看在模拟或实盘模式下不会有的数据来"作弊"。

策略可以"作弊"的原因是 freqtrade 回测过程在开始时填充完整的数据框，包括所有蜡烛图时间戳。
如果程序员不小心或不知道内部工作原理
（有时这真的很难找出来），那么策略将查看未来。

此命令旨在尝试验证上述前瞻性偏差形式的有效性。

### 命令如何工作？

它将从所有交易对的回测开始，为指标和入场/出场生成基线。
在此初始回测运行后，它将查看是否满足 `minimum-trade-amount`，如果不满足，则取消此策略的前瞻性分析。
如果发生这种情况，请使用更宽的时间范围来获得更多交易进行分析，或使用发生更多交易的时间范围。

设置基线后，它将为每个入场和出场分别进行额外的回测运行。
当这些验证回测完成时，它将比较信号蜡烛图（入场或出场）的指标
并报告偏差。
在所有信号都被验证或证伪后，将为用户生成结果表。

### 如何找到和消除偏差？如何挽救有偏差的策略？

如果您在网上找到了一个有偏差的策略并希望获得相同的结果，只是没有偏差，
那么大多数时候您会失望的。
通常策略中的偏差是"好得令人难以置信"利润的驱动因素。
删除由于偏差而推高利润的条件或指标通常会使策略显著变差。
如果有偏差的指标或条件不是策略的核心，或者
有其他没有偏差的入场和出场信号，您可能能够部分挽救它。

### 前瞻性偏差的示例

- `shift(-10)` 查看未来 10 根蜡烛图。
- 在 populate_* 函数中使用 `iloc[]` 访问数据框中的特定行。
- For 循环容易引入前瞻性偏差，如果您不严格控制循环的数字。
- 聚合函数如 `.mean()`、`.min()` 和 `.max()`，没有滚动窗口，
  将计算**整个**数据框的值，因此信号蜡烛图将"看到"包括未来蜡烛图的值。
  一个无偏差的例子是使用 `rolling()` 回看蜡烛图：
  例如 `dataframe['volume_mean_12'] = dataframe['volume'].rolling(12).mean()`
- `ta.MACD(dataframe, 12, 26, 1)` 将引入信号周期为 1 的偏差。

### 结果表中的列是什么意思？

- `filename`: 检查的策略文件名
- `strategy`: 检查的策略类名
- `has_bias`: 前瞻性分析的结果。`No` 是好的，`Yes` 是坏的。
- `total_signals`: 检查的信号数量（默认为 20）
- `biased_entry_signals`: 在那么多入场中发现偏差
- `biased_exit_signals`: 在那么多出场中发现偏差
- `biased_indicators`: 显示在 populate_indicators 中定义的指标本身

如果您有与这些出场配对的有偏差的入场信号，您可能会在 `biased_exit_signals` 中得到误报。
但是，有偏差的入场通常也会导致有偏差的出场，
即使出场本身不产生偏差 -
特别是如果您的入场和出场条件使用相同的有偏差指标。

**首先解决入场中的偏差，然后解决出场。**

### 注意事项

- `lookahead-analysis` 只能验证/证伪它计算和验证的交易。
如果策略有许多不同的信号/信号类型，您需要选择适当的参数以确保所有信号至少触发一次。未触发的信号将不会被验证。
这将导致假阴性，即策略将被报告为无偏差。
- `lookahead-analysis` 可以访问相同的回测选项，这可能会引入问题。
请不要使用任何选项，如启用头寸堆叠，因为这会扭曲检查信号的数量。

## 使用示例

### 基本用法

```bash
# 分析策略的前瞻性偏差
freqtrade lookahead-analysis --strategy MyStrategy --timerange 20230101-20231231
```

### 高级选项

```bash
# 指定最小交易数量和信号数量
freqtrade lookahead-analysis --strategy MyStrategy --minimum-trade-amount 10 --targeted-trade-amount 20
```

### 分析结果解读

当分析完成后，您将看到类似以下的结果表：

```
| filename        | strategy    | has_bias | total_signals | biased_entry_signals | biased_exit_signals | biased_indicators |
|-----------------|-------------|----------|---------------|---------------------|--------------------|--------------------|
| MyStrategy.py   | MyStrategy  | Yes      | 20            | 5                   | 3                  | ['rsi', 'macd']   |
```

这表明策略存在前瞻性偏差，需要修复 RSI 和 MACD 指标的计算。

## 常见偏差模式

### 1. 未来数据泄露

```python
# 错误：使用未来数据
dataframe['future_high'] = dataframe['high'].shift(-1)

# 正确：只使用历史数据
dataframe['prev_high'] = dataframe['high'].shift(1)
```

### 2. 全局聚合函数

```python
# 错误：计算整个数据框的平均值
dataframe['global_mean'] = dataframe['close'].mean()

# 正确：使用滚动窗口
dataframe['rolling_mean'] = dataframe['close'].rolling(20).mean()
```

### 3. 不当的循环使用

```python
# 错误：循环可能访问未来数据
for i in range(len(dataframe)):
    dataframe.loc[i, 'signal'] = dataframe['close'].iloc[i:i+10].max()

# 正确：使用向量化操作
dataframe['signal'] = dataframe['close'].rolling(10).max()
```

## 修复偏差的步骤

1. **识别偏差源**：查看分析结果中的 `biased_indicators`
2. **检查指标计算**：确保不使用未来数据
3. **修复代码**：使用适当的滚动窗口或历史数据
4. **重新测试**：再次运行前瞻性分析验证修复
5. **验证性能**：确保修复后策略仍然有效

## 最佳实践

- 始终使用 `rolling()` 而不是全局聚合
- 避免使用负数的 `shift()`
- 小心使用 `iloc[]` 和循环
- 定期运行前瞻性分析
- 在策略开发早期就进行偏差检查
