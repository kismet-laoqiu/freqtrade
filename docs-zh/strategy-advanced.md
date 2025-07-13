# 高级策略

本页面解释了策略可用的一些高级概念。
如果您刚开始，请先熟悉 [Freqtrade 基础](bot-basics.md) 和 [策略自定义](strategy-customization.md) 中描述的方法。

这里描述的方法的调用顺序在[机器人执行逻辑](bot-basics.md#机器人执行逻辑)中有所涵盖。这些文档也有助于决定哪种方法最适合您的自定义需求。

!!! Note
    回调方法*只有*在策略使用它们时才应该实现。

!!! Tip
    通过运行 `freqtrade new-strategy --strategy MyAwesomeStrategy --template advanced` 开始使用包含所有可用回调方法的策略模板

## 存储信息（持久化）

Freqtrade 允许在数据库中存储/检索与特定交易相关的用户自定义信息。

使用交易对象，可以使用 `trade.set_custom_data(key='my_key', value=my_value)` 存储信息，使用 `trade.get_custom_data(key='my_key')` 检索信息。每个数据条目都与一个交易和一个用户提供的键（类型为 `string`）相关联。这意味着这只能在也提供交易对象的回调中使用。

为了能够将数据存储在数据库中，freqtrade 必须序列化数据。这是通过将数据转换为 JSON 格式的字符串来完成的。
Freqtrade 将尝试在检索时反转此操作，因此从策略角度来看，这应该不相关。

```python
from freqtrade.persistence import Trade
from datetime import timedelta

class AwesomeStrategy(IStrategy):

    def bot_loop_start(self, **kwargs) -> None:
        for trade in Trade.get_open_order_trades():
            fills = trade.select_filled_orders(trade.entry_side)
            if trade.pair == 'ETH/USDT':
                trade_entry_type = trade.get_custom_data(key='entry_type')
                if trade_entry_type is None:
                    trade_entry_type = 'breakout' if 'entry_1' in trade.enter_tag else 'dip'
                elif fills > 1:
                    trade_entry_type = 'buy_up'
                trade.set_custom_data(key='entry_type', value=trade_entry_type)
        return super().bot_loop_start(**kwargs)

    def adjust_entry_price(self, trade: Trade, order: Order | None, pair: str,
                           current_time: datetime, proposed_rate: float, current_order_rate: float,
                           entry_tag: str | None, side: str, **kwargs) -> float:
        # 对于 BTC/USDT 交易对，在入场触发后的前 10 分钟内，限价订单使用并跟随 SMA200 作为价格目标。
        if (
            pair == 'BTC/USDT'
            and entry_tag == 'long_sma200'
            and side == 'long'
            and (current_time - timedelta(minutes=10)) > trade.open_date_utc
            and order.filled == 0.0
        ):
            dataframe, _ = self.dp.get_analyzed_dataframe(pair=pair, timeframe=self.timeframe)
            current_candle = dataframe.iloc[-1].squeeze()
            # 存储关于入场调整的信息
            existing_count = trade.get_custom_data('num_entry_adjustments', default=0)
            if not existing_count:
                existing_count = 1
            else:
                existing_count += 1
            trade.set_custom_data(key='num_entry_adjustments', value=existing_count)

            # 调整订单价格
            return current_candle['sma_200']

        # 默认：维持现有订单
        return current_order_rate

    def custom_exit(self, pair: str, trade: Trade, current_time: datetime, current_rate: float, current_profit: float, **kwargs):

        entry_adjustment_count = trade.get_custom_data(key='num_entry_adjustments')
        trade_entry_type = trade.get_custom_data(key='entry_type')
        if entry_adjustment_count is None:
            if current_profit > 0.01 and (current_time - timedelta(minutes=100) > trade.open_date_utc):
                return True, 'exit_1'
        else:
            if entry_adjustment_count > 0 and current_profit > 0.05:
                return True, 'exit_2'
            if trade_entry_type == 'breakout' and current_profit > 0.1:
                return True, 'exit_3'

        return False, None
```

上面是一个简单的例子 - 有更简单的方法来检索交易数据，如入场调整。

!!! Note
    建议使用简单的数据类型 `[bool, int, float, str]` 以确保序列化需要存储的数据时没有问题。
    存储大块数据可能导致意外的副作用，如数据库变大（因此也变慢）。

!!! Warning "不可序列化的数据"
    如果提供的数据无法序列化，将记录警告，指定 `key` 的条目将包含 `None` 作为数据。

??? Note "所有属性"
    自定义数据通过 Trade 对象（下面假设为 `trade`）具有以下访问器：

    * `trade.get_custom_data(key='something', default=0)` - 返回以提供的类型给出的实际值。
    * `trade.get_custom_data_entry(key='something')` - 返回条目 - 包括元数据。值可通过 `.value` 属性访问。
    * `trade.set_custom_data(key='something', value={'some': 'value'})` - 为此交易设置或更新相应的键。值必须是可序列化的 - 我们建议保持存储的数据相对较小。

    "value" 可以是任何类型（在设置和接收时） - 但必须是 json 可序列化的。

## 存储信息（非持久化）

!!! Warning "已弃用"
    这种存储信息的方法已被弃用，我们建议不要使用非持久化存储。
    请改用[持久化存储](#存储信息持久化)。

    因此其内容已被折叠。

??? Abstract "存储信息"
    存储信息可以通过在策略类中创建新字典来完成。

    变量的名称可以任意选择，但应该以 `custom_` 为前缀，以避免与预定义的策略变量发生命名冲突。

    ```python
    class AwesomeStrategy(IStrategy):
        # 创建自定义字典
        custom_info = {}

        def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
            # 检查条目是否已存在
            if not metadata["pair"] in self.custom_info:
                # 为此交易对创建空条目
                self.custom_info[metadata["pair"]] = {}

            if "crosstime" in self.custom_info[metadata["pair"]]:
                self.custom_info[metadata["pair"]]["crosstime"] += 1
            else:
                self.custom_info[metadata["pair"]]["crosstime"] = 1
    ```

    !!! Warning
        数据在机器人重启（或配置重新加载）后不会持久化。此外，数据量应该保持较小（没有 DataFrames 等），否则机器人将开始消耗大量内存，最终内存不足并崩溃。

## 确认交易出场

`confirm_trade_exit()` 方法可用于在最后一刻中止出场交易。

```python
class AwesomeStrategy(IStrategy):
    def confirm_trade_exit(self, pair: str, trade: 'Trade', order_type: str, amount: float,
                           rate: float, time_in_force: str, exit_reason: str,
                           current_time: 'datetime', **kwargs) -> bool:
        # 获取交易对数据框。
        dataframe, _ = self.dp.get_analyzed_dataframe(pair, self.timeframe)

        # 获取最后可用的蜡烛图。不要使用 current_time 查找最新蜡烛图，因为
        # current_time 指向当前不完整的蜡烛图，其数据不可用。
        last_candle = dataframe.iloc[-1].squeeze()

        # 在某些条件下阻止出场
        if exit_reason == 'roi' and last_candle['rsi'] < 30:
            # 如果 RSI 显示超卖，不要因为 ROI 而出场
            return False

        # 允许出场
        return True
```

## 入场标签

入场标签是一个可选功能，允许您为每个入场信号分配一个标签。这些标签可以在后续的回调中使用，以实现不同的逻辑。

```python
def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
    dataframe["enter_tag"] = ""
    signal_rsi = (qtpylib.crossed_above(dataframe["rsi"], 35))
    signal_bblower = (dataframe["bb_lowerband"] < dataframe["close"])
    # 附加条件
    dataframe.loc[
        (
            signal_rsi
            | signal_bblower
            # ... 进入多头头寸的附加信号
        )
        & (dataframe["volume"] > 0)
            , "enter_long"
        ] = 1
    # 连接标签，以便保留所有信号
    dataframe.loc[signal_rsi, "enter_tag"] += "long_signal_rsi "
    dataframe.loc[signal_bblower, "enter_tag"] += "long_signal_bblower "

    return dataframe

def custom_exit(self, pair: str, trade: Trade, current_time: datetime, current_rate: float,
                current_profit: float, **kwargs):
    dataframe, _ = self.dp.get_analyzed_dataframe(pair, self.timeframe)
    last_candle = dataframe.iloc[-1].squeeze()
    if "long_signal_rsi" in trade.enter_tag and last_candle["rsi"] > 80:
        return "exit_signal_rsi"
    if "long_signal_bblower" in trade.enter_tag and last_candle["high"] > last_candle["bb_upperband"]:
        return "exit_signal_bblower"
    # ...
    return None
```

!!! Note
    `enter_tag` 限制为 255 个字符，剩余数据将被截断。

!!! Warning
    只有一个 `enter_tag` 列，用于多头和空头交易。
    因此，此列必须被视为"最后写入获胜"（毕竟它只是一个数据框列）。
    在复杂情况下，多个信号冲突（或者如果信号基于不同条件再次停用），这可能导致应用错误标签到入场信号的奇怪结果。
    这些结果是策略覆盖先前标签的结果 - 最后一个标签将"粘住"并且将是 freqtrade 将使用的标签。

## 出场标签

与入场标签类似，您也可以为出场信号分配标签。

```python
def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
    dataframe.loc[
        (
            (dataframe['rsi'] > 80) &
            (dataframe['volume'] > 0)
        ),
        ['exit_long', 'exit_tag']] = (1, 'rsi_overbought')

    dataframe.loc[
        (
            (dataframe['macd'] < dataframe['macdsignal']) &
            (dataframe['volume'] > 0)
        ),
        ['exit_long', 'exit_tag']] = (1, 'macd_cross_down')

    return dataframe
```

提供的出场标签然后用作出场原因 - 并在回测结果中显示。

!!! Note
    `exit_reason` 限制为 100 个字符，剩余数据将被截断。

## 策略版本

您可以通过使用 "version" 方法实现自定义策略版本控制，并返回您希望此策略具有的版本。

```python
def version(self) -> str:
    """
    返回策略的版本。
    """
    return "1.1"
```

!!! Note
    您应该确保实现适当的版本控制（如 git 仓库），因为 freqtrade 不会保留策略的历史版本，所以用户需要能够最终回滚到策略的先前版本。

## 派生策略

策略可以从其他策略派生。这避免了自定义策略代码的重复。您可以使用此技术覆盖主策略的小部分，保持其余部分不变：

```python title="user_data/strategies/myawesomestrategy.py"
class MyAwesomeStrategy(IStrategy):
    ...
    stoploss = 0.13
    trailing_stop = False
    # 所有其他属性和方法都在这里，就像
    # 在任何自定义策略中一样...
    ...
```

```python title="user_data/strategies/MyAwesomeStrategy2.py"
from myawesomestrategy import MyAwesomeStrategy
class MyAwesomeStrategy2(MyAwesomeStrategy):
    # 覆盖某些内容
    stoploss = 0.08
    trailing_stop = True
```

属性和方法都可以被覆盖，以您需要的方式改变原始策略的行为。

虽然在同一文件中保留子类在技术上是可能的，但这可能导致超参数优化参数文件的一些问题，因此我们建议使用单独的策略文件，并如上所示导入父策略。

## 嵌入策略

Freqtrade 为您提供了一种将策略嵌入到配置文件中的简单方法。
这是通过利用 BASE64 编码并在您选择的配置文件中的策略配置字段提供此字符串来完成的。

### 将字符串编码为 BASE64

这是一个快速示例，如何在 python 中生成 BASE64 字符串

```python
from base64 import urlsafe_b64encode

with open(file, 'r') as f:
    content = f.read()
content = urlsafe_b64encode(content.encode('utf-8'))
```

变量 'content' 将包含 BASE64 编码形式的策略文件。现在可以在您的配置文件中设置如下

```json
"strategy": "NameOfStrategy:BASE64String"
```

请确保 'NameOfStrategy' 与策略名称相同！

## 性能警告

在执行策略时，有时可能会在日志中看到以下内容

> PerformanceWarning: DataFrame is highly fragmented.

这通常发生在策略多次修改数据框时（例如在多个 `.loc` 调用中）。
虽然这不会破坏任何东西，但可能会影响性能。
这可以通过在策略末尾调用 `dataframe.copy()` 来解决，这将去碎片化数据框。

```python
def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
    # 您的指标计算
    dataframe['sma'] = ta.SMA(dataframe, 20)
    dataframe['rsi'] = ta.RSI(dataframe, 14)

    # 多个条件赋值可能导致碎片化
    dataframe.loc[dataframe['rsi'] > 70, 'signal'] = 1
    dataframe.loc[dataframe['rsi'] < 30, 'signal'] = -1

    # 去碎片化数据框
    return dataframe.copy()
```

## 最佳实践

### 1. 保持回调简单
回调应该快速执行，避免复杂的计算。

### 2. 使用持久化存储
对于需要在重启后保留的数据，使用 `trade.set_custom_data()` 而不是实例变量。

### 3. 验证数据可用性
在使用数据框数据之前，始终检查数据是否可用。

### 4. 错误处理
在回调中实现适当的错误处理，以防止策略崩溃。

```python
def custom_exit(self, pair: str, trade: Trade, current_time: datetime,
                current_rate: float, current_profit: float, **kwargs):
    try:
        dataframe, _ = self.dp.get_analyzed_dataframe(pair, self.timeframe)
        if len(dataframe) == 0:
            return None

        last_candle = dataframe.iloc[-1].squeeze()
        # 您的出场逻辑

    except Exception as e:
        self.logger.error(f"Error in custom_exit for {pair}: {e}")
        return None
```

### 5. 文档化您的策略
为复杂的逻辑添加注释和文档字符串。

通过遵循这些高级概念和最佳实践，您可以创建更强大、更灵活的交易策略。
