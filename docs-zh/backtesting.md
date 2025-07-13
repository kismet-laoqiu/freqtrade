# 回测

本页面解释如何使用回测来验证您的策略性能。

回测需要历史数据可用。
要了解如何获取您感兴趣的交易对和交易所的数据，请转到文档的[数据下载](data-download.md)部分。

回测也可在[网络服务器模式](freq-ui.md#回测)中使用，允许您通过 Web 界面运行回测。

## 回测命令参考

--8<-- "commands/backtesting.md"

## 使用回测测试您的策略

现在您有了良好的入场和出场策略以及一些历史数据，您想要针对真实数据进行测试。这就是我们所说的[回测](https://en.wikipedia.org/wiki/Backtesting)。

回测将使用配置文件中的加密货币（交易对），默认从 `user_data/data/<exchange>` 加载历史蜡烛图 (OHLCV) 数据。
如果交易所/交易对/时间框架组合没有可用数据，回测将要求您首先使用 `freqtrade download-data` 下载它们。
有关下载的详细信息，请参阅文档中的[数据下载](data-download.md)部分。

回测的结果将确认您的机器人是否比亏损有更好的盈利机会。

所有利润计算都包括费用，freqtrade 将使用交易所的默认费用进行计算。

!!! Warning "使用动态交易对列表进行回测"
    可以使用动态交易对列表（并非所有处理程序都允许在回测模式下使用），但它依赖于当前市场条件 - 这不会反映交易对列表的历史状态。
    此外，当使用 StaticPairlist 以外的交易对列表时，无法保证回测结果的可重现性。
    请阅读[交易对列表文档](plugins.md#pairlists)以获取更多信息。

    要获得可重现的结果，最好通过 [`test-pairlist`](utils.md#test-pairlist) 命令生成交易对列表，并将其用作静态交易对列表。

!!! Note
    默认情况下，Freqtrade 将回测结果导出到 `user_data/backtest_results`。
    导出的交易可用于[进一步的回测结果分析](#进一步的回测结果分析)或可由脚本目录中的[绘图子命令](plotting.md#绘制价格和指标)（`freqtrade plot-dataframe`）使用。

### 起始余额

回测需要起始余额，可以作为 `--dry-run-wallet <balance>` 或 `--starting-balance <balance>` 命令行参数提供，或通过 `dry_run_wallet` 配置设置提供。
此金额必须高于 `stake_amount`，否则机器人将无法模拟任何交易。

### 动态投注金额

回测通过将 `stake_amount` 配置为 `"unlimited"` 来支持[动态投注金额](configuration.md#动态投注金额)，这将把起始余额分成 `max_open_trades` 份。
早期交易的利润将导致后续更高的投注金额，从而在回测期间实现利润复合。

### 回测命令示例

使用 5 分钟蜡烛图 (OHLCV) 数据（默认）

```bash
freqtrade backtesting --strategy AwesomeStrategy
```

其中 `--strategy AwesomeStrategy` / `-s AwesomeStrategy` 指的是策略的类名，该类位于 `user_data/strategies` 目录中的 python 文件中。

---

使用 1 分钟蜡烛图 (OHLCV) 数据

```bash
freqtrade backtesting --strategy AwesomeStrategy --timeframe 1m
```

---

提供 1000 的自定义起始余额（以基础货币计）

```bash
freqtrade backtesting --strategy AwesomeStrategy --dry-run-wallet 1000
```

---

使用不同的磁盘历史蜡烛图 (OHLCV) 数据源

假设您从 Binance 交易所下载了历史数据并将其保存在 `user_data/data/binance-20180101` 目录中。
然后您可以使用此数据进行回测，如下所示：

```bash
freqtrade backtesting --strategy AwesomeStrategy --datadir user_data/data/binance-20180101 
```

---

比较多个策略

```bash
freqtrade backtesting --strategy-list SampleStrategy1 AwesomeStrategy --timeframe 5m
```

其中 `SampleStrategy1` 和 `AwesomeStrategy` 指的是策略的类名。

---

防止将交易导出到文件

```bash
freqtrade backtesting --strategy AwesomeStrategy --no-trades
```

---

指定自定义费用

```bash
freqtrade backtesting --strategy AwesomeStrategy --fee 0.001
```

---

运行回测并将结果存储在特定文件中

```bash
freqtrade backtesting --strategy AwesomeStrategy --export trades --export-filename user_data/backtest_results/my_backtest.json
```

## 理解回测结果

回测将显示一个包含许多指标的表格，帮助您了解策略的性能。以下是主要指标的解释：

### 关键指标

- **总交易数**：策略执行的交易总数
- **起始余额**：回测开始时的余额
- **最终余额**：回测结束时的余额
- **绝对利润**：以基础货币计算的总利润
- **总利润 %**：总利润百分比
- **年化利润**：年化利润百分比
- **年化夏普比率**：风险调整后的回报指标
- **最大回撤**：从峰值到谷值的最大损失
- **平均交易**：每笔交易的平均利润
- **中位数交易**：交易利润的中位数

### 交易统计

- **盈利交易**：盈利交易的数量和百分比
- **亏损交易**：亏损交易的数量和百分比
- **最佳交易**：单笔最佳交易的利润
- **最差交易**：单笔最差交易的损失
- **平均持仓时间**：交易的平均持续时间

## 回测最佳实践

1. **使用足够的历史数据**：至少使用几个月的数据来获得可靠的结果
2. **考虑不同的市场条件**：在牛市、熊市和横盘市场中测试您的策略
3. **验证数据质量**：确保您的历史数据完整且准确
4. **考虑滑点和费用**：回测应该包括现实的交易成本
5. **避免过度拟合**：不要过度优化您的策略以适应历史数据

!!! Warning "回测限制"
    回测基于历史数据，过去的表现不能保证未来的结果。回测不能完全模拟实际交易条件，如滑点、流动性问题或极端市场事件。

### 使用时间范围运行较小测试集的回测

使用 `--timerange` 参数更改您想要使用的测试集的大小。

例如，使用 `--timerange=20190501-` 选项运行回测将使用从 2019 年 5 月 1 日开始的所有可用数据。

```bash
freqtrade backtesting --timerange=20190501-
```

您还可以指定特定的日期范围。

完整的时间范围规范：

- 使用数据直到 2018/01/31：`--timerange=-20180131`
- 使用自 2018/01/31 以来的数据：`--timerange=20180131-`
- 使用从 2018/01/31 到 2018/03/01 的数据：`--timerange=20180131-20180301`
- 使用 POSIX / epoch 时间戳 1527595200 1527618600 之间的数据：`--timerange=1527595200-1527618600`

### 详细的回测结果表格

回测完成后，您将看到类似以下的详细结果：

```
============================================================= BACKTESTING REPORT =============================================================
|         Pair |   Entries |   Avg Profit % |   Cum Profit % |   Tot Profit USDT |   Tot Profit % |   Avg Duration |   Win  Draw  Loss  Win% |
|--------------+-----------+----------------+----------------+--------------------+----------------+----------------+-------------------------|
|     ADA/USDT |        35 |           0.56 |          19.54 |          19.54000  |           1.95 |        2:17:00 |    15     0    20  42.9 |
|     BTC/USDT |        37 |           0.64 |          23.68 |          23.68000  |           2.37 |        2:34:00 |    17     0    20  45.9 |
|     ETH/USDT |        42 |           0.73 |          30.66 |          30.66000  |           3.07 |        2:19:00 |    26     0    16  61.9 |
|        TOTAL |       114 |           0.65 |          73.88 |          73.88000  |           7.39 |        2:22:00 |    58     0    56  50.9 |
```

### 摘要指标

```
================== SUMMARY METRICS ==================
| Metric                      | Value               |
|-----------------------------+---------------------|
| Backtesting from            | 2019-01-01 00:00:00 |
| Backtesting to              | 2019-05-01 00:00:00 |
| Trading Mode                | Spot                |
| Max open trades             | 3                   |
|                             |                     |
| Total/Daily Avg Trades      | 429 / 3.575         |
| Starting balance            | 0.01000000 BTC      |
| Final balance               | 0.01762792 BTC      |
| Absolute profit             | 0.00762792 BTC      |
| Total profit %              | 76.2%               |
| CAGR %                      | 460.87%             |
| Profit factor               | 1.11                |
| Expectancy (Ratio)          | 5.87 (1.56)         |
| Sharpe                      | 1.78                |
| Sortino                     | 2.97                |
| Calmar                      | 17.51               |
| Max Drawdown                | 4.36%               |
| Avg. Drawdown               | 1.75%               |
| Max Drawdown Duration       | 2 days, 13:45:00    |
| Avg. Drawdown Duration      | 0 days, 4:57:00     |
|                             |                     |
| Best Pair                   | LSK/BTC 26.31%      |
| Worst Pair                  | ZEC/BTC -10.18%     |
| Best Trade                  | LSK/BTC 4.25%       |
| Worst Trade                 | ZEC/BTC -1.15%      |
|                             |                     |
| Best day                    | 0.00076 BTC 7.6%    |
| Worst day                   | -0.00036 BTC -4.0%  |
| Days win/draw/lose          | 12 / 82 / 25        |
| Avg. Duration Winners       | 4:23:00             |
| Avg. Duration Loser         | 6:55:00             |
| Rejected Entry signals      | 3089                |
| Entry/Exit Timeouts         | 0 / 0               |
|                             |                     |
| Min balance                 | 0.00945123 BTC      |
| Max balance                 | 0.01846651 BTC      |
| Market change               | -5.88%              |
```

### 指标详细解释

**基本信息：**
- `Backtesting from/to`：回测的时间范围
- `Trading Mode`：交易模式（现货或期货）
- `Max open trades`：最大同时开仓交易数
- `Total/Daily Avg Trades`：总交易数和每日平均交易数

**财务指标：**
- `Starting/Final balance`：起始和最终余额
- `Absolute profit`：绝对利润（以质押货币计）
- `Total profit %`：总利润百分比
- `CAGR %`：复合年增长率

**风险指标：**
- `Profit factor`：总盈利与总亏损的比率
- `Expectancy`：每笔交易的期望收益
- `Sharpe`：夏普比率（风险调整后收益）
- `Sortino`：索提诺比率（下行风险调整后收益）
- `Calmar`：卡尔玛比率（年化收益与最大回撤的比率）
- `Max Drawdown`：最大回撤百分比
- `Max Drawdown Duration`：最大回撤持续时间

**交易分析：**
- `Best/Worst Pair`：表现最好和最差的交易对
- `Best/Worst Trade`：最佳和最差的单笔交易
- `Days win/draw/lose`：盈利、平局和亏损的天数
- `Avg. Duration Winners/Loser`：盈利和亏损交易的平均持续时间
- `Rejected Entry signals`：被拒绝的入场信号数量

### 每日/每周/每月分解

您可以使用 `--breakdown` 参数获得更详细的时间分解：

```bash
freqtrade backtesting --strategy AwesomeStrategy --breakdown day week month
```

这将显示每日、每周和每月的利润分布，帮助您了解策略在不同时间段的表现。

### 回测结果缓存

为了节省时间，默认情况下，当回测的策略和配置与之前的回测匹配时，回测将重用最近一天内的缓存结果。要强制进行新的回测，尽管存在相同运行的现有结果，请指定 `--cache none` 参数。

```bash
# 强制重新运行回测，不使用缓存
freqtrade backtesting --strategy AwesomeStrategy --cache none

# 使用缓存（默认）
freqtrade backtesting --strategy AwesomeStrategy --cache day
```

### 进一步的回测结果分析

要进一步分析您的回测结果，freqtrade 默认会将交易导出到文件。
然后您可以加载交易以执行进一步分析，如[数据分析](strategy_analysis_example.md#load-backtest-results-to-pandas-dataframe)回测部分所示。

此外，您可以在[网络服务器模式](freq-ui.md#backtesting)下使用 freqtrade 在网络界面中可视化回测结果。
此模式还允许您加载现有的回测结果，因此您可以在不重新运行回测的情况下分析它们。
对于此模式 - `--notes "<notes>"` 可用于向回测结果添加注释，这些注释将在网络界面中显示。

### 回测输出文件

freqtrade 生成的输出文件是一个包含以下文件的 zip 文件：

- JSON 格式的回测报告
- feather 格式的市场变化数据
- 策略文件的副本
- 策略参数的副本（如果使用了参数文件）
- 配置文件的清理副本

这将确保结果是可重现的 - 假设相同的数据可用。

只有策略文件和配置文件包含在 zip 文件中，最终的依赖项不包括在内。

## 回测假设

由于回测缺乏关于蜡烛图内发生情况的一些详细信息，它需要做出一些假设：

- 遵守交易所[交易限制](#回测中的交易限制)
- 除非指定了自定义价格逻辑，否则入场发生在开盘价
- 所有订单都以请求的价格成交（无滑点），只要价格在蜡烛图的高/低范围内
- 出场信号出场发生在连续蜡烛图的开盘价
- 出场释放其交易槽位供不同交易对的新交易使用
- 出场信号优于止损，因为出场信号假设在蜡烛图开盘时触发
- ROI
  - 出场与高点比较 - 但使用 ROI 值（例如 ROI = 2%，高点 = 5% - 因此出场将在 2%）
  - 出场永远不会"低于蜡烛图"，因此如果低点在 2.4% 利润，2% 的 ROI 可能导致在 2.4% 出场
- 止损
  - 如果止损被触发，它将在止损价格出场（假设没有滑点）
  - 止损永远不会"高于蜡烛图"，因此止损可能比配置的止损更差
- 费用在每笔交易中计算，并从利润中扣除

考虑到这些假设，回测试图尽可能接近地镜像真实交易。但是，回测**永远不会**替代在模拟模式下运行策略。
此外，请记住过去的结果不能保证未来的成功。

除了上述假设外，策略作者应该仔细阅读[常见错误](strategy-customization.md#开发策略时的常见错误)部分，以避免在回测中使用在真实市场条件下不可用的数据。

### 回测中的交易限制

交易所有某些交易限制，如最小（和最大）基础货币，或最小/最大质押（报价）货币。
这些限制通常在交易所文档中列为"交易规则"或类似内容，在不同交易对之间可能相当不同。

回测（以及实盘和模拟运行）确实遵守这些限制，并将确保可以在此值以下放置止损 - 因此该值将略高于交易所指定的值。
但是，Freqtrade 没有关于历史限制的信息。

这可能导致通过使用历史价格夸大交易限制的情况，导致最小金额 > 50$。

例如：
如果 `BTC/USDT` 的最小交易金额是 0.001 BTC - 并且 BTC 的当前价格是 50,000$ - 那么最小交易金额是 50$。
如果回测期间 BTC 的价格是 100,000$ - 那么最小交易金额将是 100$ - 这可能导致一些交易被跳过。

这些精度值基于当前交易所限制（如[上述部分](#回测中的交易限制)中所述），因为历史精度限制不可用。

## 改进的回测准确性

回测的一个大限制是它无法知道价格如何在蜡烛图内移动（高点在收盘前，还是相反？）。
因此，假设您使用 1 小时时间框架运行回测，该蜡烛图将有 4 个价格（开盘、高点、低点、收盘）。

虽然回测确实对此做出了一些假设（阅读上文） - 这永远不可能是完美的，并且总是会以某种方式偏向。
为了缓解这种情况，freqtrade 可以使用更低（更快）的时间框架来模拟蜡烛图内的移动。

要利用这一点，您可以在常规回测命令中附加 `--timeframe-detail 5m`。

```bash
freqtrade backtesting --strategy AwesomeStrategy --timeframe 1h --timeframe-detail 5m
```

这将加载 1 小时数据（主时间框架）以及所选时间范围的 5 分钟数据（详细时间框架）。
策略将使用 1 小时时间框架进行分析。
可能发生活动的蜡烛图（有活跃信号，交易对在交易中）将在 5 分钟时间框架上进行评估。
这将允许更准确地模拟蜡烛图内的移动 - 并可能导致不同的结果，特别是在更高的时间框架上。

!!! Warning "详细时间框架要求"
    详细时间框架必须是主时间框架的子集。
    因此，如果您的主时间框架是 1 小时，详细时间框架可以是 1m、5m、15m 或 30m - 但不能是 2h。

!!! Note "性能影响"
    使用详细时间框架会显著增加回测时间，因为需要处理更多数据。
    建议首先在没有详细时间框架的情况下测试您的策略，然后使用详细时间框架进行最终验证。

## 回测多个策略

要比较多个策略，可以向回测提供策略列表。

这限制为每次运行 1 个时间框架值。但是，数据只从磁盘加载一次，因此如果您有多个想要比较的策略，这将提供良好的运行时提升。

所有列出的策略都需要在同一目录中，除非还指定了 `--recursive-strategy-search`，其中策略目录内的子目录也会被考虑。

```bash
freqtrade backtesting --timerange 20180401-20180410 --timeframe 5m --strategy-list Strategy001 Strategy002 --export trades
```

这将运行两个策略（`Strategy001` 和 `Strategy002`）的回测，并为每个策略生成单独的结果。

## 回测和实盘交易的差异

虽然回测试图模拟真实交易，但存在一些重要差异：

### 市场影响
- **回测**：假设您的订单不影响市场价格
- **实盘**：大订单可能会移动市场价格

### 滑点
- **回测**：假设订单以确切的请求价格执行
- **实盘**：可能存在滑点，特别是在波动的市场中

### 流动性
- **回测**：假设总是有足够的流动性
- **实盘**：可能遇到流动性问题，特别是在小市值币种上

### 延迟
- **回测**：即时执行
- **实盘**：网络延迟和交易所处理时间

### 费用
- **回测**：使用静态费用率
- **实盘**：费用可能因交易量、VIP 等级等而变化

## 回测最佳实践

### 1. 数据质量
- 使用高质量、完整的历史数据
- 验证数据的准确性和完整性
- 考虑数据源的可靠性

### 2. 时间范围选择
- 使用足够长的时间范围（至少几个月）
- 包括不同的市场条件（牛市、熊市、横盘）
- 考虑季节性因素

### 3. 样本外测试
- 保留一部分数据用于最终验证
- 在不同时间段测试策略
- 避免在同一数据集上过度优化

### 4. 现实的期望
- 考虑回测的限制
- 保守估计实际表现
- 计划额外的安全边际

### 5. 渐进式验证
```bash
# 1. 快速测试
freqtrade backtesting --strategy MyStrategy --timerange=-30

# 2. 详细测试
freqtrade backtesting --strategy MyStrategy --timerange=-365 --timeframe-detail 1m

# 3. 多策略比较
freqtrade backtesting --strategy-list Strategy1 Strategy2 Strategy3 --timerange=-180

# 4. 模拟运行
freqtrade trade --strategy MyStrategy --dry-run

# 5. 小额实盘测试
freqtrade trade --strategy MyStrategy --starting-balance 100
```

## 故障排除

### 常见问题

1. **数据不足**
   ```
   No data found for pair XYZ/USDT
   ```
   解决方案：使用 `freqtrade download-data` 下载数据

2. **内存不足**
   ```
   MemoryError: Unable to allocate array
   ```
   解决方案：减少时间范围或使用较少的交易对

3. **策略错误**
   ```
   Strategy contains errors
   ```
   解决方案：检查策略语法和逻辑

4. **配置问题**
   ```
   Configuration error
   ```
   解决方案：验证配置文件格式和内容

### 性能优化

1. **使用缓存**：让 Freqtrade 缓存计算结果
2. **限制数据**：使用较短的时间范围进行初始测试
3. **减少交易对**：先用少数交易对测试
4. **优化策略**：避免复杂的计算

## 总结

回测是验证交易策略的重要工具，但需要理解其限制并正确使用。通过遵循最佳实践和理解回测假设，您可以更好地评估策略的潜在表现，并为实盘交易做好准备。

记住：回测只是策略开发过程的一部分。在投入真实资金之前，始终要进行模拟交易和小额实盘测试。
