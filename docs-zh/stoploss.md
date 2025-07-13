# 止损

`stoploss` 配置参数是应该触发卖出的损失比率。
例如，值 `-0.10` 将在给定交易的利润跌破 -10% 时立即卖出。此参数是可选的。
止损计算包括费用，因此 -10% 的止损正好设置在入场点下方 10%。

大多数策略文件已经包含了最优的 `stoploss` 值。

!!! Info
    本文件中提到的所有止损属性都可以在策略中设置，或在配置中设置。
    <ins>配置值将覆盖策略值。</ins>

## 交易所止损/Freqtrade 止损

这些止损模式可以是*交易所内*或*交易所外*。

这些模式可以通过以下值配置：

``` python
    'emergency_exit': 'market',
    'stoploss_on_exchange': False
    'stoploss_on_exchange_interval': 60,
    'stoploss_on_exchange_limit_ratio': 0.99
```

交易所止损仅支持以下交易所，并非所有交易所都支持止损限价和止损市价。
如果只有一种模式可用，订单类型将被忽略。

| 交易所 | 止损类型 |
|----------|-------------|
| Binance  | limit |
| Binance Futures  | market, limit |
| Bingx    | market, limit |
| HTX      | limit |
| kraken   | market, limit |
| Gate     | limit |
| Okx      | limit |
| Kucoin   | stop-limit, stop-market|
| Hyperliquid (仅期货)   | limit |

!!! Note "紧密止损"
    <ins>使用交易所止损时不要设置过低/过紧的止损值！</ins>
    如果设置过低/过紧，您将面临更大的订单未成交风险，止损将不起作用。

### stoploss_on_exchange 和 stoploss_on_exchange_limit_ratio

启用或禁用交易所止损。
如果止损是*交易所内*的，这意味着在买入订单成交后立即在交易所下达止损限价订单。这将保护您免受市场突然崩盘的影响，因为订单执行完全在交易所内进行，没有潜在的网络开销。

如果 `stoploss_on_exchange` 使用限价订单，交易所需要 2 个价格：止损价格和限价。
`stoploss` 定义了下达限价订单的止损价格 - 限价应该略低于此价格。
如果交易所同时支持限价和市价止损订单，那么 `stoploss` 的值将用于确定止损类型。

计算示例：我们以 100$ 买入资产。
止损价格是 95$，那么限价将是 `95 * 0.99 = 94.05$` - 所以限价订单成交可以在 95$ 和 94.05$ 之间发生。

例如，假设止损在交易所，并且启用了跟踪止损，市场正在上涨，那么机器人会自动取消之前的止损订单，并下达一个止损值高于之前止损订单的新订单。

!!! Note
    如果启用了 `stoploss_on_exchange` 并且止损在交易所被手动取消，那么机器人将创建一个新的止损订单。

### stoploss_on_exchange_interval

在交易所止损的情况下，还有另一个参数叫做 `stoploss_on_exchange_interval`。这配置了机器人检查止损并在必要时更新它的间隔（以秒为单位）。
机器人不能每 5 秒（每次迭代）都这样做，否则会被交易所禁止。
所以这个参数将告诉机器人多久应该更新一次止损订单。默认值是 60（1 分钟）。
如果您意外取消了止损订单，同样的逻辑将在交易所重新应用止损订单。

### stoploss_price_type

!!! Warning "仅适用于期货"
    `stoploss_price_type` 仅适用于期货市场（在支持的交易所上）。
    Freqtrade 将在启动时对此设置进行验证，如果为您的交易所选择了无效设置，将无法启动。
    支持的价格类型在各个交易所之间会有所不同。请与您的交易所确认它支持哪些价格类型。

期货市场上的交易所止损可以在不同的价格类型上触发。
这些价格在交易所术语中的命名通常有所不同，但通常是"last"（或"合约价格"）、"mark"和"index"之类的。

此设置的可接受值是 `"last"`、`"mark"` 和 `"index"` - freqtrade 将自动转换为相应的 API 类型，并相应地下达[交易所止损](#stoploss_on_exchange-和-stoploss_on_exchange_limit_ratio)订单。

### force_exit

`force_exit` 是一个可选值，默认与 `exit` 相同，在从 Telegram 或 Rest API 发送 `/forceexit` 命令时使用。

### force_entry

`force_entry` 是一个可选值，默认与 `entry` 相同，在从 Telegram 或 Rest API 发送 `/forceentry` 命令时使用。

### emergency_exit

`emergency_exit` 是一个可选值，默认为 `market`，在创建交易所止损订单失败时使用。
下面是如果在策略或配置文件中未更改时使用的默认值。

策略文件示例：

``` python
order_types = {
    "entry": "limit",
    "exit": "limit",
    "emergency_exit": "market",
    "stoploss": "market",
    "stoploss_on_exchange": True,
    "stoploss_on_exchange_interval": 60,
    "stoploss_on_exchange_limit_ratio": 0.99
}
```

## 止损类型

在这个阶段，机器人包含以下止损支持模式：

1. 静态止损。
2. 跟踪止损。
3. 跟踪止损，自定义正向损失。
4. 仅在交易达到某个偏移量后的跟踪止损。
5. [自定义止损函数](strategy-callbacks.md#custom-stoploss)

### 静态止损

这非常简单，您定义一个 x 的止损（作为价格的比率，即价格的 x * 100%）。一旦损失超过定义的损失，这将尝试卖出资产。

止损示例：

``` python
    stoploss = -0.10
```

例如，简化数学：

* 机器人以 100$ 的价格买入资产
* 止损定义为 -10%
* 一旦资产跌破 90$，止损将被触发

### 跟踪止损

此值的初始值是 `stoploss`，就像您定义静态止损一样。
要启用跟踪止损：

``` python
    stoploss = -0.10
    trailing_stop = True
```

这将激活一个算法，每当您的资产价格上涨时，它会自动向上移动止损。

例如，简化数学：

* 机器人以 100$ 的价格买入资产
* 止损定义为 -10%
* 一旦资产跌破 90$，止损将被触发
* 假设资产现在增加到 102$
* 止损现在将是 102$ 的 -10% = 91.8$
* 现在资产价值下降到 101$，止损仍将是 91.8$，并将在 91.8$ 触发。

总结：止损将被调整为始终是观察到的最高价格的 -10%。

### 跟踪止损，不同的正向损失

您也可以在买入（买入 - 费用）处于亏损状态时有一个默认止损，但一旦您达到正向结果（或您定义的偏移量），系统将使用具有不同值的新止损。
例如，您的默认止损是 -10%，但一旦您达到盈利（例如 0.1%），将使用不同的跟踪止损。

!!! Note
    如果您希望止损仅在您盈亏平衡或盈利时更改（大多数用户想要的），请参考下一节的[启用偏移量](#仅在交易达到某个偏移量后的跟踪止损)。

两个值都需要将 `trailing_stop` 设置为 true 并设置 `trailing_stop_positive` 值。

``` python
    stoploss = -0.10
    trailing_stop = True
    trailing_stop_positive = 0.02
    trailing_stop_positive_offset = 0.0
    trailing_only_offset_is_reached = False  # 默认 - 此示例不需要
```

例如，简化数学：

* 机器人以 100$ 的价格买入资产
* 止损定义为 -10%
* 一旦资产跌破 90$，止损将被触发
* 假设资产现在增加到 102$
* 止损现在将是 102$ 的 -2% = 99.96$（99.96$ 止损将被锁定，并将跟随资产价格增量 -2%）
* 现在资产价值下降到 101$，止损仍将是 99.96$，并将在 99.96$ 触发

0.02 将转换为 -2% 止损。
在此之前，`stoploss` 用于跟踪止损。

!!! Tip "使用偏移量更改您的止损"
    使用 `trailing_stop_positive_offset` 通过将 `trailing_stop_positive_offset` 设置为高于 `trailing_stop_positive` 来确保您的新跟踪止损将盈利。您的第一个新止损值将已经锁定利润。

    简化数学示例：

    ``` python
        stoploss = -0.10
        trailing_stop = True
        trailing_stop_positive = 0.02
        trailing_stop_positive_offset = 0.03
    ```

    * 机器人以 100$ 的价格买入资产
    * 止损定义为 -10%，所以一旦资产跌破 90$，止损将被触发
    * 假设资产现在增加到 102$
    * 止损现在将是 91.8$ - 观察到的最高价格的 -10%
    * 假设资产现在增加到 103.5$（超过配置的偏移量）
    * 止损现在将是 103.5$ 的 -2% = 101.43$
    * 现在资产价值下降到 102$，止损仍将是 101.43$，并将在价格跌破 101.43$ 时触发

### 仅在交易达到某个偏移量后的跟踪止损

您也可以保持静态止损，直到达到偏移量，然后在市场转向时跟踪交易以获取利润。

如果 `trailing_only_offset_is_reached = True`，则跟踪止损仅在达到偏移量后激活。在此之前，止损保持在配置的 `stoploss` 并且不跟踪。
将此值保留为 `trailing_only_offset_is_reached=False` 将允许跟踪止损在资产价格增加到初始入场价格之上时立即开始跟踪。

此选项可以与 `trailing_stop_positive` 一起使用或不使用，但使用 `trailing_stop_positive_offset` 作为偏移量。

配置（偏移量是买入价格 + 3%）：

```python
    stoploss = -0.10
    trailing_stop = True
    trailing_stop_positive = 0.02
    trailing_stop_positive_offset = 0.03
    trailing_only_offset_is_reached = True
```

例如，简化数学：

* 机器人以 100$ 的价格买入资产
* 止损定义为 -10%
* 一旦资产跌破 90$，止损将被触发
* 止损将保持在 90$，除非资产增加到或超过配置的偏移量
* 假设资产现在增加到 103$（我们配置偏移量的地方）
* 止损现在将是 103$ 的 -2% = 100.94$
* 现在资产价值下降到 101$，止损仍将是 100.94$，并将在 100.94$ 触发

!!! Tip
    确保此值（`trailing_stop_positive_offset`）低于最小 ROI，否则最小 ROI 将首先应用并卖出交易。

## 止损和杠杆

止损应该被认为是"此交易的风险" - 因此在 100$ 交易上 10% 的止损意味着您愿意在此交易上损失 10$（10%） - 如果价格向下移动 10% 将触发。

使用杠杆时，应用相同的原则 - 止损定义交易的风险（您愿意损失的金额）。

因此，在 10x 交易上 10% 的止损将在 1% 的价格移动时触发。
如果您的质押金额（自有资本）是 100$ - 此交易在 10x 时将是 1000$（杠杆后）。
如果价格移动 1% - 您已经损失了 10$ 的自有资本 - 因此在这种情况下止损将触发。

确保意识到这一点，并避免使用过紧的止损（在 10x 杠杆下，10% 的风险可能太小，无法让交易"呼吸"一点）。

## 更改开放交易的止损

可以通过更改配置或策略中的值并使用 `/reload_config` 命令来更改开放交易的止损（或者，完全停止并重新启动机器人也有效）。

新的止损值将应用于开放交易（并将生成相应的日志消息）。

### 限制

如果启用了 `trailing_stop` 并且止损已经调整，则无法更改止损值。
