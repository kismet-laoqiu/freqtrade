# V2 和 V3 之间的策略迁移

为了支持新市场和交易类型（即做空交易/杠杆交易），接口中的一些内容必须更改。
如果您打算使用现货市场以外的市场，请将您的策略迁移到新格式。

我们已经付出了巨大努力来保持与现有策略的兼容性，因此如果您只想继续在__现货市场__中使用 freqtrade，现在应该不需要进行任何更改。

您可以使用快速摘要作为检查清单。请参考下面的详细部分以获取完整的迁移详情。

## 快速摘要 / 迁移检查清单

注意：`forcesell`、`forcebuy`、`emergencysell` 分别更改为 `force_exit`、`force_enter`、`emergency_exit`。

* 策略方法：
  * [`populate_buy_trend()` -> `populate_entry_trend()`](#populate_buy_trend)
  * [`populate_sell_trend()` -> `populate_exit_trend()`](#populate_sell_trend)
  * [`custom_sell()` -> `custom_exit()`](#custom_sell)
  * [`check_buy_timeout()` -> `check_entry_timeout()`](#custom_entry_timeout)
  * [`check_sell_timeout()` -> `check_exit_timeout()`](#custom_entry_timeout)
  * 没有交易对象的回调的新 `side` 参数
    * [`custom_stake_amount`](#custom_stake_amount)
    * [`confirm_trade_entry`](#confirm_trade_entry)
    * [`custom_entry_price`](#custom_entry_price)
  * [`confirm_trade_exit` 中更改的参数名称](#confirm_trade_exit)
* 数据框列：
  * [`buy` -> `enter_long`](#populate_buy_trend)
  * [`sell` -> `exit_long`](#populate_sell_trend)
  * [`buy_tag` -> `enter_tag`（用于做多和做空交易）](#populate_buy_trend)
  * [新列 `enter_short` 和相应的新列 `exit_short`](#populate_sell_trend)
* 交易对象现在具有以下新属性：
  * `is_short`
  * `entry_side`
  * `exit_side`
  * `trade_direction`
  * 重命名：`sell_reason` -> `exit_reason`
* [重命名 `trade.nr_of_successful_buys` 为 `trade.nr_of_successful_entries`（主要与 `adjust_trade_position()` 相关）](#adjust-trade-position-changes)
* 引入了新的 [`leverage` 回调](strategy-callbacks.md#leverage-callback)。
* 信息对现在可以在元组中传递第三个元素，定义蜡烛图类型。
* `@informative` 装饰器现在接受可选的 `candle_type` 参数。
* [辅助方法](#helper-methods) `stoploss_from_open` 和 `stoploss_from_absolute` 现在接受 `is_short` 作为附加参数。
* `INTERFACE_VERSION` 应设置为 3。
* [策略/配置设置](#strategyconfiguration-settings)。
  * `order_time_in_force` buy -> entry，sell -> exit。
  * `order_types` buy -> entry，sell -> exit。
  * `unfilledtimeout` buy -> entry，sell -> exit。
  * `ignore_buying_expired_candle_after` -> 移动到根级别而不是 "ask_strategy/exit_pricing"
* 术语更改
  * 卖出原因更改以反映新的"出场"命名而不是卖出。如果您在策略中使用 `exit_reason` 检查，请小心并最终更新您的策略。
    * `sell_signal` -> `exit_signal`
    * `custom_sell` -> `custom_exit`
    * `roi` -> `roi`
    * `stop_loss` -> `stop_loss`
    * `stoploss_on_exchange` -> `stoploss_on_exchange`
    * `trailing_stop_loss` -> `trailing_stop_loss`
    * `sell_signal` -> `exit_signal`
    * `force_sell` -> `force_exit`
    * `emergency_sell` -> `emergency_exit`

!!! Note "策略接口版本"
    为了使用新功能，您需要将 `INTERFACE_VERSION = 3` 迁移到您的策略中。
    这将启用所有新功能，并要求您使用新的方法名称。
    您可以通过运行 `freqtrade strategy-updater` 来自动迁移您的策略。

## 详细迁移指南

### populate_buy_trend

`populate_buy_trend()` 方法已重命名为 `populate_entry_trend()`。

`buy` 列已重命名为 `enter_long`。
`buy_tag` 列已重命名为 `enter_tag`。

```python
def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
    dataframe.loc[
        (
            (dataframe['rsi'] < 35) &
            (dataframe['volume'] > 0)
        ),
        ['enter_long', 'enter_tag']] = (1, 'rsi_oversold')

    return dataframe
```

请参阅[策略自定义文档](strategy-customization.md)以获取有关如何迁移策略的更多详细信息。

### populate_sell_trend

`populate_sell_trend()` 方法已重命名为 `populate_exit_trend()`。

`sell` 列已重命名为 `exit_long`。

```python
def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
    dataframe.loc[
        (
            (dataframe['rsi'] > 70) &
            (dataframe['volume'] > 0)
        ),
        'exit_long'] = 1

    return dataframe
```

### 做空支持

为了支持做空，引入了新的列：

* `enter_short` - 做空入场信号
* `exit_short` - 做空出场信号

```python
def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
    # 做多入场
    dataframe.loc[
        (
            (dataframe['rsi'] < 35) &
            (dataframe['volume'] > 0)
        ),
        ['enter_long', 'enter_tag']] = (1, 'rsi_oversold')

    # 做空入场
    dataframe.loc[
        (
            (dataframe['rsi'] > 65) &
            (dataframe['volume'] > 0)
        ),
        ['enter_short', 'enter_tag']] = (1, 'rsi_overbought')

    return dataframe

def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
    # 做多出场
    dataframe.loc[
        (
            (dataframe['rsi'] > 70) &
            (dataframe['volume'] > 0)
        ),
        'exit_long'] = 1

    # 做空出场
    dataframe.loc[
        (
            (dataframe['rsi'] < 30) &
            (dataframe['volume'] > 0)
        ),
        'exit_short'] = 1

    return dataframe
```

### custom_sell

`custom_sell()` 方法已重命名为 `custom_exit()`。

```python
def custom_exit(self, pair: str, trade: 'Trade', current_time: 'datetime', current_rate: float,
                current_profit: float, **kwargs):
    """
    自定义出场逻辑，在每个蜡烛图上为每个开放交易调用。
    """
    if current_profit < -0.10:
        return 'stop_loss'

    if current_profit > 0.20:
        return 'take_profit'

    return None
```

### 超时回调

超时回调已重命名：

* `check_buy_timeout()` -> `check_entry_timeout()`
* `check_sell_timeout()` -> `check_exit_timeout()`

```python
def check_entry_timeout(self, pair: str, trade: 'Trade', order: dict,
                       current_time: datetime, **kwargs) -> bool:
    """
    检查入场订单是否应该超时。
    """
    return False

def check_exit_timeout(self, pair: str, trade: 'Trade', order: dict,
                      current_time: datetime, **kwargs) -> bool:
    """
    检查出场订单是否应该超时。
    """
    return False
```

### 带有 side 参数的回调

一些回调现在接收 `side` 参数以区分做多和做空交易：

#### custom_stake_amount

```python
def custom_stake_amount(self, pair: str, current_time: datetime, current_rate: float,
                       proposed_stake: float, min_stake: float, max_stake: float,
                       leverage: float, entry_tag: Optional[str], side: str,
                       **kwargs) -> float:
    """
    自定义质押金额逻辑。
    """
    if side == 'long':
        return proposed_stake * 1.5
    else:  # short
        return proposed_stake * 0.75
```

#### confirm_trade_entry

```python
def confirm_trade_entry(self, pair: str, order_type: str, amount: float, rate: float,
                       time_in_force: str, current_time: datetime, entry_tag: Optional[str],
                       side: str, **kwargs) -> bool:
    """
    确认交易入场。
    """
    if side == 'long':
        return True
    else:  # short
        # 只在特定条件下允许做空
        return self.dp.get_pair_dataframe(pair, self.timeframe)['rsi'].iloc[-1] > 70
```

#### custom_entry_price

```python
def custom_entry_price(self, pair: str, current_time: datetime, proposed_rate: float,
                      entry_tag: Optional[str], side: str, **kwargs) -> float:
    """
    自定义入场价格逻辑。
    """
    if side == 'long':
        return proposed_rate * 0.995  # 稍微低一点买入
    else:  # short
        return proposed_rate * 1.005  # 稍微高一点卖出
```

### confirm_trade_exit

`confirm_trade_exit` 中的参数名称已更改：

```python
def confirm_trade_exit(self, pair: str, trade: Trade, order_type: str, amount: float,
                      rate: float, time_in_force: str, exit_reason: str,
                      current_time: datetime, **kwargs) -> bool:
    """
    确认交易出场。
    注意：exit_reason 参数（以前是 sell_reason）
    """
    return True
```

### 交易对象更改

交易对象现在具有新的属性来支持做空交易：

```python
# 新属性
trade.is_short          # 布尔值，指示这是否是做空交易
trade.entry_side        # 'buy' 或 'sell'
trade.exit_side         # 'sell' 或 'buy'
trade.trade_direction   # 'long' 或 'short'
trade.exit_reason       # 以前是 sell_reason
```

### adjust_trade_position 更改

`trade.nr_of_successful_buys` 已重命名为 `trade.nr_of_successful_entries`：

```python
def adjust_trade_position(self, trade: Trade, current_time: datetime,
                         current_rate: float, current_profit: float,
                         min_stake: Optional[float], max_stake: float,
                         current_entry_rate: float, current_exit_rate: float,
                         current_entry_profit: float, current_exit_profit: float,
                         **kwargs) -> Optional[float]:
    """
    调整交易头寸。
    """
    if trade.nr_of_successful_entries == 1:
        # 第一次入场后的逻辑
        if current_profit > 0.05:
            return trade.stake_amount * 0.5

    return None
```

### 杠杆回调

引入了新的杠杆回调：

```python
def leverage(self, pair: str, current_time: datetime, current_rate: float,
            proposed_leverage: float, max_leverage: float, entry_tag: Optional[str],
            side: str, **kwargs) -> float:
    """
    自定义杠杆逻辑。
    """
    if side == 'long':
        return min(proposed_leverage, 3.0)
    else:  # short
        return min(proposed_leverage, 2.0)
```

### 信息对更改

信息对现在可以指定蜡烛图类型：

```python
def informative_pairs(self):
    """
    定义信息对。
    """
    return [
        ('BTC/USDT', '1h'),           # 默认蜡烛图类型
        ('ETH/USDT', '4h', 'spot'),   # 明确指定现货
        ('BTC/USDT', '1d', 'mark'),   # 标记价格蜡烛图
    ]
```

`@informative` 装饰器也支持蜡烛图类型：

```python
@informative('1h', 'BTC/USDT', 'mark')
def populate_indicators_btc_1h(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
    dataframe['rsi'] = ta.RSI(dataframe, 14)
    return dataframe
```

### 辅助方法

辅助方法现在接受 `is_short` 参数：

```python
# 计算止损价格
stop_price = self.stoploss_from_open(
    open_rate=trade.open_rate,
    current_profit=current_profit,
    is_short=trade.is_short
)

# 从绝对价格计算止损
stop_price = self.stoploss_from_absolute(
    stop_rate=stop_rate,
    current_rate=current_rate,
    is_short=trade.is_short
)
```

### 策略/配置设置

#### order_time_in_force

```json
// 之前
{
    "order_time_in_force": {
        "buy": "GTC",
        "sell": "GTC"
    }
}

// 之后
{
    "order_time_in_force": {
        "entry": "GTC",
        "exit": "GTC"
    }
}
```

#### order_types

```json
// 之前
{
    "order_types": {
        "buy": "limit",
        "sell": "limit",
        "stoploss": "market",
        "stoploss_on_exchange": false
    }
}

// 之后
{
    "order_types": {
        "entry": "limit",
        "exit": "limit",
        "stoploss": "market",
        "stoploss_on_exchange": false
    }
}
```

#### unfilledtimeout

```json
// 之前
{
    "unfilledtimeout": {
        "buy": 10,
        "sell": 30
    }
}

// 之后
{
    "unfilledtimeout": {
        "entry": 10,
        "exit": 30
    }
}
```

#### 订单定价

订单定价配置也发生了更改：

```json
// 之前
{
    "bid_strategy": {
        "price_side": "bid",
        "use_order_book": true,
        "order_book_top": 1,
        "ask_last_balance": 0.0
    },
    "ask_strategy": {
        "price_side": "ask",
        "use_order_book": true,
        "order_book_top": 1,
        "bid_last_balance": 0.0,
        "ignore_buying_expired_candle_after": 120
    }
}

// 之后
{
    "entry_pricing": {
        "price_side": "same",
        "use_order_book": true,
        "order_book_top": 1,
        "price_last_balance": 0.0
    },
    "exit_pricing": {
        "price_side": "same",
        "use_order_book": true,
        "order_book_top": 1,
        "price_last_balance": 0.0
    },
    "ignore_buying_expired_candle_after": 120
}
```

### Webhook 术语更改

Webhook 配置中的术语也发生了更改：

```json
// 之前
{
    "webhook": {
        "webhookbuy": "entry",
        "webhookbuyfill": "entry_fill",
        "webhookbuycancel": "entry_cancel",
        "webhooksell": "exit",
        "webhooksellfill": "exit_fill",
        "webhooksellcancel": "exit_cancel"
    }
}

// 之后
{
    "webhook": {
        "entry": "entry",
        "entry_fill": "entry_fill",
        "entry_cancel": "entry_cancel",
        "exit": "exit",
        "exit_fill": "exit_fill",
        "exit_cancel": "exit_cancel"
    }
}
```

### Telegram 通知设置

Telegram 通知设置也需要更新：

```json
// 之前
{
    "telegram": {
        "notification_settings": {
            "buy": "on",
            "buy_fill": "on",
            "buy_cancel": "on",
            "sell": "on",
            "sell_fill": "on",
            "sell_cancel": "on"
        }
    }
}

// 之后
{
    "telegram": {
        "notification_settings": {
            "entry": "on",
            "entry_fill": "on",
            "entry_cancel": "on",
            "exit": "on",
            "exit_fill": "on",
            "exit_cancel": "on"
        }
    }
}
```

## FreqAI 策略迁移

FreqAI 策略也需要进行重大更改。`populate_any_indicators()` 方法已被拆分为多个新方法：

### 新的 FreqAI 方法

1. `feature_engineering_expand_all()` - 自动扩展的特征
2. `feature_engineering_expand_basic()` - 基本扩展特征
3. `feature_engineering_standard()` - 标准特征
4. `set_freqai_targets()` - 设置目标

### feature_engineering_expand_all

```python
def feature_engineering_expand_all(self, dataframe: DataFrame, period: int, **kwargs) -> DataFrame:
    """
    此函数将自动在配置定义的 indicator_periods_candles、include_timeframes、
    include_shifted_candles 和 include_corr_pairs 上扩展定义的特征。
    """
    dataframe[f"%rsi-period"] = ta.RSI(dataframe, timeperiod=period)
    dataframe[f"%mfi-period"] = ta.MFI(dataframe, timeperiod=period)
    dataframe[f"%adx-period"] = ta.ADX(dataframe, timeperiod=period)

    return dataframe
```

### feature_engineering_expand_basic

```python
def feature_engineering_expand_basic(self, dataframe: DataFrame, **kwargs) -> DataFrame:
    """
    此函数将自动在配置定义的 include_timeframes、include_shifted_candles
    和 include_corr_pairs 上扩展定义的特征。
    """
    dataframe["%pct-change"] = dataframe["close"].pct_change()
    dataframe["%raw_volume"] = dataframe["volume"]
    dataframe["%raw_price"] = dataframe["close"]

    return dataframe
```

### feature_engineering_standard

```python
def feature_engineering_standard(self, dataframe: DataFrame, **kwargs) -> DataFrame:
    """
    此可选函数将使用基础时间框架的数据框调用一次。
    这是最后调用的函数，这意味着进入此函数的数据框将包含
    所有其他 freqai_feature_engineering_* 函数创建的所有特征和列。
    """
    dataframe["%day_of_week"] = dataframe["date"].dt.dayofweek
    dataframe["%hour_of_day"] = dataframe["date"].dt.hour

    return dataframe
```

### set_freqai_targets

```python
def set_freqai_targets(self, dataframe: DataFrame, **kwargs) -> DataFrame:
    """
    设置 FreqAI 目标（标签）。
    """
    dataframe["&-target"] = (
        dataframe["close"].shift(-self.freqai_info["feature_parameters"]["label_period_candles"])
        / dataframe["close"]
        - 1
    )

    return dataframe
```

## 自动迁移工具

Freqtrade 提供了自动迁移工具来帮助您更新策略：

```bash
# 迁移单个策略
freqtrade strategy-updater --strategy-list MyStrategy

# 迁移所有策略
freqtrade strategy-updater

# 迁移特定目录中的策略
freqtrade strategy-updater --strategy-path /path/to/strategies
```

!!! Warning "迁移工具限制"
    自动迁移工具会尽力迁移您的策略，但可能无法处理所有复杂情况。
    迁移后请仔细检查您的策略，并进行必要的手动调整。

## 迁移后的验证

迁移策略后，建议进行以下验证：

1. **语法检查**：确保策略文件没有语法错误
2. **回测验证**：使用相同的数据进行回测，确保结果一致
3. **模拟运行**：在模拟模式下运行策略以验证实时行为
4. **日志检查**：检查日志中是否有警告或错误消息

```bash
# 语法检查
python -m py_compile user_data/strategies/MyStrategy.py

# 回测验证
freqtrade backtesting --strategy MyStrategy --timerange 20230101-20230201

# 模拟运行
freqtrade trade --strategy MyStrategy --dry-run
```

## 常见迁移问题

### 问题 1：方法名称未更新

**错误**：`AttributeError: 'MyStrategy' object has no attribute 'populate_buy_trend'`

**解决方案**：确保所有方法名称都已更新到 V3 格式。

### 问题 2：列名称未更新

**错误**：策略不产生任何交易信号

**解决方案**：检查数据框列名称是否已从 `buy`/`sell` 更新为 `enter_long`/`exit_long`。

### 问题 3：配置设置未更新

**错误**：配置验证失败

**解决方案**：更新配置文件中的所有相关设置，如 `order_types`、`order_time_in_force` 等。

## 总结

V2 到 V3 的迁移主要涉及：

1. **方法重命名**：买入/卖出相关方法重命名为入场/出场
2. **列重命名**：数据框列名称更新
3. **新功能支持**：做空交易和杠杆支持
4. **配置更新**：相关配置设置的术语更改
5. **FreqAI 重构**：特征工程方法的重新组织

通过遵循本指南和使用自动迁移工具，您应该能够成功将策略从 V2 迁移到 V3。如果遇到问题，请参考 Freqtrade 社区论坛或 Discord 频道寻求帮助。
