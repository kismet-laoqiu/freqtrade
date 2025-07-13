# Freqtrade 基础

本页面为您提供 Freqtrade 如何工作和运行的一些基本概念。

## Freqtrade 术语

* **策略 (Strategy)**：您的交易策略，告诉机器人要做什么。
* **交易 (Trade)**：开放头寸。
* **开放订单 (Open Order)**：当前在交易所下达但尚未完成的订单。
* **交易对 (Pair)**：可交易的货币对，通常格式为 基础货币/报价货币（例如现货的 `XRP/USDT`，期货的 `XRP/USDT:USDT`）。
* **时间框架 (Timeframe)**：要使用的蜡烛图长度（例如 `"5m"`、`"1h"`、...）。
* **指标 (Indicators)**：技术指标（SMA、EMA、RSI、...）。
* **限价订单 (Limit order)**：以定义的限价或更好价格执行的限价订单。
* **市价订单 (Market order)**：保证成交，可能会根据订单大小影响价格。
* **当前利润 (Current Profit)**：此交易当前待定（未实现）的利润。这主要在整个机器人和 UI 中使用。
* **已实现利润 (Realized Profit)**：已经实现的利润。仅与[部分退出](strategy-callbacks.md#adjust-trade-position)结合使用时相关 - 这也解释了此计算逻辑。
* **总利润 (Total Profit)**：已实现和未实现利润的组合。相对数字（%）是根据此交易的总投资计算的。

## 费用处理

Freqtrade 的所有利润计算都包括费用。对于回测/超参数优化/模拟运行模式，使用交易所默认费用（交易所的最低层级）。对于实盘操作，使用交易所应用的费用（这包括 BNB 返利等）。

## 交易对命名

Freqtrade 遵循 [ccxt 命名约定](https://docs.ccxt.com/#/README?id=consistency-of-base-and-quote-currencies) 来命名货币。
在错误的市场中使用错误的命名约定通常会导致机器人无法识别交易对，通常会出现"此交易对不可用"等错误。

### 现货交易对命名

对于现货交易对，命名将是 `基础货币/报价货币`（例如 `ETH/USDT`）。

### 期货交易对命名

对于期货交易对，命名将是 `基础货币/报价货币:结算货币`（例如 `ETH/USDT:USDT`）。

## 机器人执行逻辑

在模拟运行或实盘模式下启动 freqtrade（使用 `freqtrade trade`）将启动机器人并开始机器人迭代循环。
这也将运行 `bot_start()` 回调。

默认情况下，机器人循环每隔几秒钟运行一次（`internals.process_throttle_secs`）并执行以下操作：

* 从持久化存储中获取开放交易。
* 计算当前可交易交易对列表。
* 下载交易对列表的 OHLCV 数据，包括所有[信息性交易对](strategy-customization.md#get-data-for-non-tradeable-pairs)
  此步骤每个蜡烛图只执行一次，以避免不必要的网络流量。
* 调用 `bot_loop_start()` 策略回调。
* 分析每个交易对的策略。
  * 调用 `populate_indicators()`
  * 调用 `populate_entry_trend()`
  * 调用 `populate_exit_trend()`
* 从交易所更新交易开放订单状态。
  * 为已成交订单调用 `order_filled()` 策略回调。
  * 检查开放订单的超时。
    * 为开放入场订单调用 `check_entry_timeout()` 策略回调。
    * 为开放出场订单调用 `check_exit_timeout()` 策略回调。
    * 为开放订单调用 `adjust_order_price()` 策略回调。
      * 为开放入场订单调用 `adjust_entry_price()` 策略回调。*仅在未实现 `adjust_order_price()` 时调用*
      * 为开放出场订单调用 `adjust_exit_price()` 策略回调。*仅在未实现 `adjust_order_price()` 时调用*
* 验证现有头寸并最终下达出场订单。
  * 考虑止损、ROI 和出场信号、`custom_exit()` 和 `custom_stoploss()`。
  * 根据 `exit_pricing` 配置设置或使用 `custom_exit_price()` 回调确定出场价格。
  * 在下达出场订单之前，调用 `confirm_trade_exit()` 策略回调。
* 如果启用，通过调用 `adjust_trade_position()` 检查开放交易的头寸调整，如果需要则下达额外订单。
* 检查交易槽位是否仍然可用（如果达到 `max_open_trades`）。
* 验证入场信号尝试进入新头寸。
  * 根据 `entry_pricing` 配置设置或使用 `custom_entry_price()` 回调确定入场价格。
  * 在保证金和期货模式下，调用 `leverage()` 策略回调来确定所需的杠杆。
  * 通过调用 `custom_stake_amount()` 回调确定投注大小。
  * 在下达入场订单之前，调用 `confirm_trade_entry()` 策略回调。

此循环将一遍又一遍地重复，直到机器人停止。

## 回测/超参数优化执行逻辑

[回测](backtesting.md) 或 [超参数优化](hyperopt.md) 只执行上述逻辑的一部分，因为大多数交易操作都是完全模拟的。

* 为配置的交易对列表加载历史数据。
* 调用一次 `bot_start()`。
* 计算指标（每个交易对调用一次 `populate_indicators()`）。
* 计算入场/出场信号（每个交易对调用一次 `populate_entry_trend()` 和 `populate_exit_trend()`）。
* 循环每个蜡烛图模拟入场和出场点。
  * 调用 `bot_loop_start()` 策略回调。
  * 检查订单超时，通过 `unfilledtimeout` 配置或通过 `check_entry_timeout()` / `check_exit_timeout()` 策略回调。
  * 为开放订单调用 `adjust_order_price()` 策略回调。
    * 为开放入场订单调用 `adjust_entry_price()` 策略回调。*仅在未实现 `adjust_order_price()` 时调用！*
    * 为开放出场订单调用 `adjust_exit_price()` 策略回调。*仅在未实现 `adjust_order_price()` 时调用！*
  * 检查交易入场信号（`enter_long` / `enter_short` 列）。
  * 确认交易入场/出场（如果在策略中实现，调用 `confirm_trade_entry()` 和 `confirm_trade_exit()`）。
  * 调用 `custom_entry_price()`（如果在策略中实现）来确定入场价格（价格被移动到开盘蜡烛图内）。
  * 在保证金和期货模式下，调用 `leverage()` 策略回调来确定所需的杠杆。
  * 通过调用 `custom_stake_amount()` 回调确定投注大小。
  * 如果启用，检查开放交易的头寸调整并调用 `adjust_trade_position()` 来确定是否需要额外订单。
  * 为已成交入场订单调用 `order_filled()` 策略回调。
  * 调用 `custom_stoploss()` 和 `custom_exit()` 来找到自定义出场点。
  * 对于基于出场信号、自定义出场和部分出场的出场：调用 `custom_exit_price()` 来确定出场价格（价格被移动到收盘蜡烛图内）。
  * 为已成交出场订单调用 `order_filled()` 策略回调。
* 生成回测报告输出

!!! Note
    回测和超参数优化包括验证，确保前瞻性偏差不会影响结果。
    要了解更多信息，请参阅[前瞻性偏差页面](lookahead-analysis.md)。
