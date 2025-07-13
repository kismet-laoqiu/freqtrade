# 交易对象

## 交易

freqtrade 进入的头寸存储在 `Trade` 对象中 - 该对象持久化到数据库。
这是 freqtrade 的核心概念 - 您会在文档的许多部分遇到它，这些部分很可能会指向此位置。

它将在许多[策略回调](strategy-callbacks.md)中传递给策略。传递给策略的对象不能直接修改。可能会根据回调结果发生间接修改。

## 交易 - 可用属性

以下属性/属性可用于每个单独的交易 - 可以使用 `trade.<property>` 使用（例如 `trade.pair`）。

|  属性 | 数据类型 | 描述 |
|------------|-------------|-------------|
| `pair` | string | 此交易的交易对。 |
| `is_open` | boolean | 交易当前是否开放，或已经结束。 |
| `open_rate` | float | 此交易的入场价格（在交易调整情况下为平均入场价格）。 |
| `close_rate` | float | 收盘价格 - 仅在 is_open = False 时设置。 |
| `stake_amount` | float | 投注（或报价）货币的金额。 |
| `amount` | float | 当前拥有的资产/基础货币金额。在初始订单成交之前将为 0.0。 |
| `open_date` | datetime | 交易开放时的时间戳 **请使用 `open_date_utc` 代替** |
| `open_date_utc` | datetime | 交易开放时的时间戳 - UTC 时间。 |
| `close_date` | datetime | 交易关闭时的时间戳 **请使用 `close_date_utc` 代替** |
| `close_date_utc` | datetime | 交易关闭时的时间戳 - UTC 时间。 |
| `close_profit` | float | 交易关闭时的相对利润。`0.01` == 1% |
| `close_profit_abs` | float | 交易关闭时的绝对利润（以投注货币计）。 |
| `realized_profit` | float | 交易仍然开放时已实现的绝对利润（以投注货币计）。 |
| `leverage` | float | 此交易使用的杠杆 - 在现货市场中默认为 1.0。 |
| `enter_tag` | string | 通过数据框中的 `enter_tag` 列在入场时提供的标签。 |
| `is_short` | boolean | 空头交易为 True，否则为 False。 |
| `orders` | Order[] | 附加到此交易的订单对象列表（包括已成交和已取消的订单）。 |
| `date_last_filled_utc` | datetime | 最后成交订单的时间。 |
| `entry_side` | "buy" / "sell" | 交易入场的订单方向。 |
| `exit_side` | "buy" / "sell" | 将导致交易退出/头寸减少的订单方向。 |
| `trade_direction` | "long" / "short" | 文本形式的交易方向 - 多头或空头。 |
| `nr_of_successful_entries` | int | 成功（已成交）入场订单的数量。 |
| `nr_of_successful_exits` | int | 成功（已成交）出场订单的数量。 |
| `has_open_orders` | boolean | 交易是否有开放订单（不包括止损订单）。 |

## 类方法

以下是类方法 - 返回通用信息，通常导致对数据库的显式查询。
它们可以用作 `Trade.<method>` - 例如 `open_trades = Trade.get_open_trade_count()`

!!! Warning "回测/超参数优化"
    大多数方法在回测/超参数优化和实盘/模拟模式下都能工作。
    在回测期间，它仅限于在[策略回调](strategy-callbacks.md)中使用。在 `populate_*()` 方法中使用不受支持，会导致错误结果。

### get_trades_proxy

当您的策略需要有关现有（开放或关闭）交易的一些信息时 - 最好使用 `Trade.get_trades_proxy()`。

用法：

``` python
from freqtrade.persistence import Trade
from datetime import timedelta

# ...
trade_hist = Trade.get_trades_proxy(pair='ETH/USDT', is_open=False, open_date=current_date - timedelta(days=2))

```

`get_trades_proxy()` 支持以下关键字参数。所有参数都是可选的 - 不带参数调用 `get_trades_proxy()` 将返回数据库中所有交易的列表。

* `pair` 例如 `pair='ETH/USDT'`
* `is_open` 例如 `is_open=False`
* `open_date` 例如 `open_date=current_date - timedelta(days=2)`
* `close_date` 例如 `close_date=current_date - timedelta(days=5)`

### get_open_trade_count

获取当前开放交易的数量

``` python
from freqtrade.persistence import Trade
# ...
open_trades = Trade.get_open_trade_count()
```

### get_total_closed_profit

检索机器人迄今为止产生的总利润。
聚合所有已关闭交易的 `close_profit_abs`。

``` python
from freqtrade.persistence import Trade

# ...
profit = Trade.get_total_closed_profit()
```

### total_open_trades_stakes

检索当前在交易中的总 stake_amount。

``` python
from freqtrade.persistence import Trade

# ...
stakes = Trade.total_open_trades_stakes()
```

## 实例方法

以下方法可用于单个交易对象。

### select_filled_orders

选择已成交的订单。

``` python
# 获取所有已成交的入场订单
filled_entries = trade.select_filled_orders(trade.entry_side)

# 获取所有已成交的出场订单  
filled_exits = trade.select_filled_orders(trade.exit_side)
```

### select_order

根据订单 ID 或订单类型选择订单。

``` python
# 根据订单 ID 选择订单
order = trade.select_order('1234567890')

# 选择入场订单
entry_orders = trade.select_order(trade.entry_side)
```

### update

更新交易对象（通常在订单更新后调用）。

``` python
trade.update(order)
```

### close

关闭交易。

``` python
trade.close(rate=close_rate, show_msg=True)
```

### get_custom_data / set_custom_data

获取或设置与交易相关的自定义数据。

``` python
# 设置自定义数据
trade.set_custom_data(key='my_key', value='my_value')

# 获取自定义数据
value = trade.get_custom_data(key='my_key')
```

!!! Note "自定义数据"
    自定义数据功能允许您存储与特定交易相关的任意信息。这对于在策略回调之间传递信息很有用。

## 订单对象

每个交易包含一个订单列表。订单对象包含有关单个订单的信息。

### 订单属性

|  属性 | 数据类型 | 描述 |
|------------|-------------|-------------|
| `id` | string | 订单 ID。 |
| `ft_order_side` | string | 订单方向（'buy' 或 'sell'）。 |
| `ft_pair` | string | 此订单的交易对。 |
| `ft_is_open` | boolean | 订单是否仍然开放。 |
| `order_type` | string | 订单类型（'market'、'limit' 等）。 |
| `status` | string | 订单状态。 |
| `amount` | float | 订单数量。 |
| `filled` | float | 已成交数量。 |
| `remaining` | float | 剩余数量。 |
| `cost` | float | 订单成本。 |
| `average` | float | 平均成交价格。 |
| `order_date` | datetime | 订单创建日期。 |
| `order_filled_date` | datetime | 订单成交日期。 |
| `order_update_date` | datetime | 订单最后更新日期。 |

!!! Note "使用交易对象"
    交易对象是 freqtrade 的核心，理解其结构和可用方法对于开发高级策略至关重要。在策略回调中，您可以访问当前交易的所有信息，并根据需要做出决策。
