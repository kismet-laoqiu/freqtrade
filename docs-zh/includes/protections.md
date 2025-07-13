## 保护机制

保护机制将通过暂时停止一个交易对或所有交易对的交易，来保护您的策略免受意外事件和市场条件的影响。
所有保护结束时间都会向上舍入到下一个蜡烛图，以避免突然的、意外的蜡烛图内买入。

!!! Tip "使用技巧"
    并非所有保护机制都适用于所有策略，需要为您的策略调整参数以提高性能。
    
    每个保护机制都可以使用不同的参数配置多次，以允许不同级别的保护（短期/长期）。

!!! Note "回测"
    保护机制受回测和超参数优化支持，但必须通过使用 `--enable-protections` 标志明确启用。

### 可用的保护机制

* [`StoplossGuard`](#stoploss-guard) 如果在特定时间窗口内发生一定数量的止损，则停止交易。
* [`MaxDrawdown`](#maxdrawdown) 如果达到最大回撤，则停止交易。
* [`LowProfitPairs`](#low-profit-pairs) 锁定低利润交易对
* [`CooldownPeriod`](#cooldown-period) 在卖出交易后不要立即进入交易。

### 所有保护机制的通用设置

|  参数| 描述 |
|------------|-------------|
| `method` | 要使用的保护名称。 <br> **数据类型：** 字符串，从[可用保护机制](#available-protections)中选择
| `stop_duration_candles` | 锁定应该设置多少个蜡烛图？ <br> **数据类型：** 正整数（以蜡烛图为单位）
| `stop_duration` | 保护应该锁定多少分钟。 <br>不能与 `stop_duration_candles` 一起使用。 <br> **数据类型：** 浮点数（以分钟为单位）
| `lookback_period_candles` | 只考虑在最后 `lookback_period_candles` 个蜡烛图内完成的交易。某些保护机制可能会忽略此设置。 <br> **数据类型：** 正整数（以蜡烛图为单位）。
| `lookback_period` | 只考虑在 `current_time - lookback_period` 之后完成的交易。 <br>不能与 `lookback_period_candles` 一起使用。 <br>某些保护机制可能会忽略此设置。 <br> **数据类型：**  浮点数（以分钟为单位）
| `trade_limit` | 最少需要的交易数量（并非所有保护机制都使用）。 <br> **数据类型：** 正整数
| `unlock_at` | 定期解锁交易的时间（并非所有保护机制都使用）。 <br> **数据类型：** 字符串 <br>**输入格式：** "HH:MM"（24小时制）

!!! Note "持续时间"
    持续时间（`stop_duration*` 和 `lookback_period*` 可以用分钟或蜡烛图定义）。
    为了在测试不同时间框架时获得更大的灵活性，下面的所有示例都将使用"蜡烛图"定义。

#### 止损保护

`StoplossGuard` 选择 `lookback_period` 分钟内的所有交易（或使用 `lookback_period_candles` 时以蜡烛图为单位）。
如果 `trade_limit` 或更多交易导致止损，交易将停止 `stop_duration` 分钟（或使用 `stop_duration_candles` 时以蜡烛图为单位，或使用 `unlock_at` 时直到设定时间）。

这适用于所有交易对，除非 `only_per_pair` 设置为 true，这将只查看一次一个交易对。

同样，此保护默认情况下将查看所有交易（多头和空头）。对于期货机器人，设置 `only_per_side` 将使机器人只考虑一侧，然后只锁定这一侧，例如允许空头在一系列多头止损后继续。

`required_profit` 将确定止损考虑所需的相对利润（或损失）。这通常不应设置，默认为 0.0 - 这意味着所有亏损止损都将触发阻止。

下面的示例在机器人在最后 24 个蜡烛图内触发 4 次止损后，在最后一次交易后停止所有交易对的交易 4 个蜡烛图。

``` python
{
    "method": "StoplossGuard",
    "lookback_period_candles": 24,
    "trade_limit": 4,
    "stop_duration_candles": 4,
    "only_per_pair": false
},
```

!!! Note
    `StoplossGuard` 只考虑实际的止损。不考虑通过 `custom_exit`、`custom_stoploss` 或类似方法退出的交易，即使它们以亏损结束。

#### 最大回撤

`MaxDrawdown` 使用所有已完成的交易（在 `lookback_period` 内）来确定最大回撤。如果回撤超过 `max_allowed_drawdown`，交易将停止 `stop_duration`（以分钟或蜡烛图为单位）。

`max_allowed_drawdown` 应该以比率提供（例如 `0.2` 表示 20%）。

可选地，可以使用 `trade_limit` 来仅在一定数量的交易后应用此保护。

``` python
{
    "method": "MaxDrawdown",
    "lookback_period_candles": 200,
    "trade_limit": 20,
    "stop_duration_candles": 10,
    "max_allowed_drawdown": 0.2
},
```

#### 低利润交易对

`LowProfitPairs` 使用所有已完成的交易（在 `lookback_period` 内）来确定任何交易对的利润。如果该交易对的利润低于 `required_profit`，该交易对将被锁定 `stop_duration`（以分钟或蜡烛图为单位）。

可选地，可以使用 `trade_limit` 来仅在一定数量的交易后应用此保护。

``` python
{
    "method": "LowProfitPairs",
    "lookback_period_candles": 20,
    "trade_limit": 2,
    "stop_duration_candles": 60,
    "required_profit": 0.02
},
```

#### 冷却期

`CooldownPeriod` 将在卖出后锁定一个交易对 `stop_duration`（以分钟或蜡烛图为单位）。

可选地，可以使用 `trade_limit` 来仅在一定数量的交易后应用此保护。

``` python
{
    "method": "CooldownPeriod",
    "stop_duration_candles": 20,
    "trade_limit": 1
},
```

!!! Note
    这将应用于成功的交易，以及止损或任何其他退出原因。

### 完整示例

所有保护机制都可以在同一配置中使用。

``` python
"protections": [
    {
        "method": "CooldownPeriod",
        "stop_duration_candles": 5,
        "trade_limit": 1
    },
    {
        "method": "MaxDrawdown",
        "lookback_period_candles": 200,
        "trade_limit": 20,
        "stop_duration_candles": 10,
        "max_allowed_drawdown": 0.2
    },
    {
        "method": "StoplossGuard",
        "lookback_period_candles": 60,
        "trade_limit": 2,
        "stop_duration_candles": 60,
        "only_per_pair": false
    },
    {
        "method": "LowProfitPairs",
        "lookback_period_candles": 20,
        "trade_limit": 2,
        "stop_duration_candles": 60,
        "required_profit": 0.02
    }
],
```
