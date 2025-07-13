# 策略回调

虽然主要策略函数（`populate_indicators()`、`populate_entry_trend()`、`populate_exit_trend()`）应该以向量化方式使用，并且在回测期间[只调用一次](bot-basics.md#回测超参数优化执行逻辑)，但回调是"在需要时"调用的。

因此，您应该避免在回调中进行繁重的计算，以避免操作期间的延迟。
根据使用的回调，它们可能在进入/退出交易时调用，或在交易持续期间调用。

当前可用的回调：

* [`bot_start()`](#机器人启动)
* [`bot_loop_start()`](#机器人循环启动)
* [`custom_stake_amount()`](#投注大小管理)
* [`custom_exit()`](#自定义出场信号)
* [`custom_stoploss()`](#自定义止损)
* [`custom_roi()`](#自定义-roi)
* [`custom_entry_price()` 和 `custom_exit_price()`](#自定义订单价格规则)
* [`check_entry_timeout()` 和 `check_exit_timeout()`](#自定义订单超时规则)
* [`confirm_trade_entry()`](#交易入场买入订单确认)
* [`confirm_trade_exit()`](#交易出场卖出订单确认)
* [`adjust_trade_position()`](#调整交易头寸)
* [`adjust_entry_price()`](#调整入场价格)
* [`leverage()`](#杠杆回调)
* [`order_filled()`](#订单成交回调)

!!! Tip "回调调用顺序"
    您可以在 [机器人基础](bot-basics.md#机器人执行逻辑) 中找到回调调用顺序

## 机器人启动

一个简单的回调，在策略加载时调用一次。
这可以用于执行只能执行一次的操作，并在数据提供者和钱包设置后运行

``` python
import requests

class AwesomeStrategy(IStrategy):

    # ... populate_* 方法

    def bot_start(self, **kwargs) -> None:
        """
        仅在机器人实例化后调用一次。
        :param **kwargs: 确保保留此参数，以便更新不会破坏您的策略。
        """
        if self.config["runmode"].value in ("live", "dry_run"):
            # 使用 self.* 将此分配给类
            # 然后可以被 populate_* 方法使用
            self.custom_remote_data = requests.get("https://some_remote_source.example.com")

```

在超参数优化期间，这只在启动时运行一次。

## 机器人循环启动

一个简单的回调，在模拟/实盘模式下每次机器人节流迭代开始时调用一次（大约每 5 秒，除非配置不同）或在回测/超参数优化模式下每根蜡烛图调用一次。
这可以用于执行与交易对无关的计算（适用于所有交易对）、加载外部数据等。

``` python
# 默认导入
import requests

class AwesomeStrategy(IStrategy):

    # ... populate_* 方法

    def bot_loop_start(self, current_time: datetime, **kwargs) -> None:
        """
        在机器人迭代开始时调用（一个循环）。
        可能用于执行与交易对无关的任务
        （例如收集一些远程资源进行比较）
        :param current_time: datetime 对象，包含当前日期时间
        :param **kwargs: 确保保留此参数，以便更新不会破坏您的策略。
        """
        if self.config["runmode"].value in ("live", "dry_run"):
            # 使用 self.* 将此分配给类
            # 然后可以被 populate_* 方法使用
            self.remote_data = requests.get("https://some_remote_source.example.com")

```

## 投注大小管理

在进入交易之前调用，使您可以在下新交易时管理您的头寸大小。

```python
# 默认导入

class AwesomeStrategy(IStrategy):
    def custom_stake_amount(self, pair: str, current_time: datetime, current_rate: float,
                            proposed_stake: float, min_stake: float | None, max_stake: float,
                            leverage: float, entry_tag: str | None, side: str,
                            **kwargs) -> float:
        """
        自定义投注金额管理。
        
        :param pair: 当前分析的交易对
        :param current_time: 当前时间
        :param current_rate: 当前价格
        :param proposed_stake: 建议的投注金额
        :param min_stake: 最小投注金额
        :param max_stake: 最大投注金额
        :param leverage: 杠杆倍数
        :param entry_tag: 入场标签
        :param side: 交易方向 ('long' 或 'short')
        :return: 要使用的投注金额
        """
        
        # 示例：根据交易对调整投注大小
        if pair in ['BTC/USDT', 'ETH/USDT']:
            return proposed_stake * 1.5  # 增加主要币种的投注
        elif 'DOGE' in pair:
            return proposed_stake * 0.5  # 减少模因币的投注
        
        return proposed_stake  # 使用默认投注金额
```

## 自定义出场信号

自定义出场信号允许您基于当前利润、交易持续时间或任何其他您可以想到的逻辑来定义额外的出场点。

```python
from datetime import timedelta

class AwesomeStrategy(IStrategy):
    
    def custom_exit(self, pair: str, trade: Trade, current_time: datetime, 
                    current_rate: float, current_profit: float, **kwargs):
        """
        自定义出场逻辑
        
        :param pair: 当前分析的交易对
        :param trade: 当前交易对象
        :param current_time: 当前时间
        :param current_rate: 当前价格
        :param current_profit: 当前利润（作为比率）
        :return: 如果应该出场则返回 (True, '出场原因')，否则返回 (False, None)
        """
        
        # 示例1：在达到5%利润后出场
        if current_profit > 0.05:
            return True, 'profit_target_5_percent'
        
        # 示例2：如果交易超过24小时且有利润则出场
        if (current_time - trade.open_date_utc) > timedelta(hours=24) and current_profit > 0:
            return True, 'time_profit_exit'
        
        # 示例3：如果损失超过3%且交易时间超过1小时则出场
        if current_profit < -0.03 and (current_time - trade.open_date_utc) > timedelta(hours=1):
            return True, 'stop_loss_time'
        
        return False, None
```

## 自定义止损

自定义止损允许您实现动态止损逻辑，可以根据各种条件调整止损水平。

```python
class AwesomeStrategy(IStrategy):
    
    def custom_stoploss(self, pair: str, trade: Trade, current_time: datetime,
                        current_rate: float, current_profit: float, **kwargs) -> float:
        """
        自定义止损逻辑
        
        :param pair: 当前分析的交易对
        :param trade: 当前交易对象
        :param current_time: 当前时间
        :param current_rate: 当前价格
        :param current_profit: 当前利润（作为比率）
        :return: 止损值（负数）
        """
        
        # 示例：基于时间的止损调整
        trade_duration = (current_time - trade.open_date_utc).total_seconds() / 3600  # 小时
        
        if trade_duration < 1:
            return -0.05  # 第一小时：5%止损
        elif trade_duration < 6:
            return -0.03  # 1-6小时：3%止损
        else:
            return -0.02  # 6小时后：2%止损
```

## 杠杆回调

杠杆回调允许您为不同的交易对设置不同的杠杆水平。

```python
class AwesomeStrategy(IStrategy):
    
    def leverage(self, pair: str, current_time: datetime, current_rate: float,
                 proposed_leverage: float, max_leverage: float, entry_tag: str | None,
                 side: str, **kwargs) -> float:
        """
        自定义杠杆逻辑
        
        :param pair: 当前分析的交易对
        :param current_time: 当前时间
        :param current_rate: 当前价格
        :param proposed_leverage: 建议的杠杆
        :param max_leverage: 最大允许杠杆
        :param entry_tag: 入场标签
        :param side: 交易方向
        :return: 要使用的杠杆倍数
        """
        
        # 示例：根据交易对设置不同杠杆
        if pair in ['BTC/USDT', 'ETH/USDT']:
            return min(3.0, max_leverage)  # 主要币种使用3倍杠杆
        elif 'DOGE' in pair:
            return min(2.0, max_leverage)  # 模因币使用2倍杠杆
        else:
            return min(1.0, max_leverage)  # 其他币种不使用杠杆
```

## 订单成交回调

当订单在交易所成交时调用此回调。

```python
class AwesomeStrategy(IStrategy):
    
    def order_filled(self, pair: str, trade: Trade, order: Order, current_time: datetime, **kwargs) -> None:
        """
        订单成交时调用
        
        :param pair: 交易对
        :param trade: 交易对象
        :param order: 成交的订单
        :param current_time: 当前时间
        """
        
        if order.ft_order_side == 'buy':
            # 入场订单成交
            print(f"买入订单成交: {pair} at {order.average}")
        else:
            # 出场订单成交
            print(f"卖出订单成交: {pair} at {order.average}")
```

!!! Note "回调的重要性"
    回调函数为策略提供了极大的灵活性，但应该谨慎使用。过于复杂的回调逻辑可能会影响机器人的性能，特别是在实盘交易中。始终在回测中彻底测试您的回调逻辑。
