# 高级超参数优化

本页面解释了一些高级超参数优化主题，这些主题可能需要比创建普通超参数优化类更高的编码技能和 Python 知识。

## 创建和使用自定义损失函数

要使用自定义损失函数类，请确保在您的自定义超参数优化损失类中定义了函数 `hyperopt_loss_function`。
对于下面的示例，您需要在超参数优化调用中添加命令行参数 `--hyperopt-loss SuperDuperHyperOptLoss`，以便使用此函数。

下面可以找到一个示例，它与默认超参数优化损失实现相同。完整示例可以在 [userdata/hyperopts](https://github.com/freqtrade/freqtrade/blob/develop/freqtrade/templates/sample_hyperopt_loss.py) 中找到。

```python
from datetime import datetime
from typing import Any, Dict

from pandas import DataFrame

from freqtrade.constants import Config
from freqtrade.optimize.hyperopt import IHyperOptLoss

TARGET_TRADES = 600
EXPECTED_MAX_PROFIT = 3.0
MAX_ACCEPTED_TRADE_DURATION = 300

class SuperDuperHyperOptLoss(IHyperOptLoss):
    """
    定义超参数优化的默认损失函数
    """

    @staticmethod
    def hyperopt_loss_function(
        *,
        results: DataFrame,
        trade_count: int,
        min_date: datetime,
        max_date: datetime,
        config: Config,
        processed: dict[str, DataFrame],
        backtest_stats: dict[str, Any],
        starting_balance: float,
        **kwargs,
    ) -> float:
        """
        目标函数，为更好的结果返回更小的数字
        这是传统算法（到目前为止在 freqtrade 中使用）。
        权重分布如下：
        * 0.4 给交易持续时间
        * 0.25：避免交易损失
        * 0.25：避免系统损失
        * 0.1：偏好更多交易
        """
        total_profit = results['profit_ratio'].sum()
        trade_duration = results['trade_duration'].mean()

        trade_loss = 1 - 0.25 * exp(-(trade_count - TARGET_TRADES) ** 2 / 10 ** 5.8)
        profit_loss = max(0, 1 - total_profit / EXPECTED_MAX_PROFIT)
        duration_loss = 0.4 * min(trade_duration / MAX_ACCEPTED_TRADE_DURATION, 1)
        result = trade_loss + profit_loss + duration_loss

        return result
```

目前，以下参数传递给损失函数：

* `results`：包含回测结果的数据框
* `trade_count`：交易数量
* `min_date`：回测开始日期
* `max_date`：回测结束日期  
* `config`：策略配置
* `processed`：包含处理数据的字典
* `backtest_stats`：包含回测统计信息的字典
* `starting_balance`：起始余额

!!! Note
    此结构允许您使用回测期间可用的任何数据。
    `results` 数据框包含所有交易的详细信息，而 `backtest_stats` 包含汇总统计信息。
    有关可用字段的详细信息，请参阅[回测文档](backtesting.md)。

### 损失函数示例

#### 最大化夏普比率

```python
class SharpeHyperOptLoss(IHyperOptLoss):
    
    @staticmethod
    def hyperopt_loss_function(results: DataFrame, **kwargs) -> float:
        """
        使用夏普比率计算损失
        """
        total_profit = results["profit_ratio"]
        days_period = (results["close_date"].max() - results["close_date"].min()).days
        
        # 计算每日收益
        daily_profit = total_profit.sum() / days_period
        profit_std = total_profit.std()
        
        # 避免除零
        if profit_std == 0:
            return -daily_profit
        
        sharp_ratio = daily_profit / profit_std * np.sqrt(365)
        
        # 返回负值，因为我们要最小化损失
        return -sharp_ratio
```

#### 最小化最大回撤

```python
class MaxDrawdownHyperOptLoss(IHyperOptLoss):
    
    @staticmethod
    def hyperopt_loss_function(results: DataFrame, **kwargs) -> float:
        """
        最小化最大回撤
        """
        if len(results) == 0:
            return 1000
        
        # 计算累积利润
        results_sorted = results.sort_values('close_date')
        cumulative_profit = results_sorted['profit_ratio'].cumsum()
        
        # 计算回撤
        running_max = cumulative_profit.expanding().max()
        drawdown = (cumulative_profit - running_max)
        max_drawdown = drawdown.min()
        
        # 返回最大回撤的绝对值
        return abs(max_drawdown)
```

#### 平衡利润和交易数量

```python
class ProfitTradeCountHyperOptLoss(IHyperOptLoss):
    
    @staticmethod
    def hyperopt_loss_function(results: DataFrame, trade_count: int, **kwargs) -> float:
        """
        平衡总利润和交易数量
        """
        total_profit = results['profit_ratio'].sum()
        
        # 目标交易数量
        target_trades = 100
        
        # 利润损失（我们想要最大化利润）
        profit_loss = -total_profit
        
        # 交易数量损失（偏离目标交易数量的惩罚）
        trade_count_loss = abs(trade_count - target_trades) / target_trades
        
        # 组合损失（可以调整权重）
        return profit_loss + 0.1 * trade_count_loss
```

## 覆盖预定义空间

虽然不建议这样做，但您可以覆盖 `roi_space`、`generate_roi_table`、`stoploss_space`、`trailing_space` 方法并实现自己的超参数优化空间。

### 覆盖 ROI 空间

```python
from freqtrade.strategy import IStrategy
from skopt.space import Integer, Real

class MyAwesomeStrategy(IStrategy):
    
    # 您的策略实现...
    
    def roi_space(self) -> List[Dimension]:
        """
        创建 ROI 超参数优化空间
        """
        return [
            Integer(10, 120, name='roi_t1'),
            Integer(10, 60, name='roi_t2'),
            Integer(10, 40, name='roi_t3'),
            Real(0.01, 0.04, name='roi_p1'),
            Real(0.01, 0.07, name='roi_p2'),
            Real(0.01, 0.20, name='roi_p3'),
        ]

    def generate_roi_table(self, params: Dict) -> Dict[int, float]:
        """
        从超参数优化参数生成 ROI 表
        """
        roi_table = {}
        roi_table[0] = params['roi_p1'] + params['roi_p2'] + params['roi_p3']
        roi_table[params['roi_t3']] = params['roi_p1'] + params['roi_p2']
        roi_table[params['roi_t3'] + params['roi_t2']] = params['roi_p1']
        roi_table[params['roi_t3'] + params['roi_t2'] + params['roi_t1']] = 0
        
        return roi_table
```

### 覆盖止损空间

```python
def stoploss_space(self) -> List[Dimension]:
    """
    创建止损超参数优化空间
    """
    return [
        Real(-0.50, -0.01, name='stoploss'),
    ]
```

### 覆盖追踪止损空间

```python
def trailing_space(self) -> List[Dimension]:
    """
    创建追踪止损超参数优化空间
    """
    return [
        # 启用追踪止损
        Categorical([True], name='trailing_stop'),
        # 追踪止损正值
        Real(0.01, 0.35, name='trailing_stop_positive'),
        # 追踪止损正偏移
        Real(0.05, 0.50, name='trailing_stop_positive_offset'),
        # 仅在达到偏移后追踪
        Categorical([True, False], name='trailing_only_offset_is_reached'),
    ]
```

## 高级超参数优化技巧

### 使用条件参数

您可以创建依赖于其他参数的条件参数：

```python
from freqtrade.strategy import IStrategy, CategoricalParameter, DecimalParameter

class ConditionalStrategy(IStrategy):
    
    # 主要参数
    use_rsi = CategoricalParameter([True, False], default=True, space="buy")
    
    # 条件参数 - 仅在 use_rsi 为 True 时使用
    rsi_buy = DecimalParameter(20, 40, default=30, space="buy")
    rsi_sell = DecimalParameter(60, 80, default=70, space="sell")
    
    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        conditions = []
        
        if self.use_rsi.value:
            conditions.append(dataframe['rsi'] < self.rsi_buy.value)
        else:
            # 使用其他指标
            conditions.append(dataframe['macd'] > dataframe['macdsignal'])
        
        if conditions:
            dataframe.loc[
                reduce(lambda x, y: x & y, conditions),
                'enter_long'] = 1
        
        return dataframe
```

### 参数验证

您可以添加参数验证以确保参数组合有效：

```python
def bot_start(self, **kwargs) -> None:
    """
    在机器人启动时验证参数
    """
    # 验证 RSI 参数
    if hasattr(self, 'rsi_buy') and hasattr(self, 'rsi_sell'):
        if self.rsi_buy.value >= self.rsi_sell.value:
            raise ValueError("rsi_buy 必须小于 rsi_sell")
    
    # 验证 ROI 和止损
    if hasattr(self, 'minimal_roi') and hasattr(self, 'stoploss'):
        max_roi = max(self.minimal_roi.values())
        if abs(self.stoploss) < max_roi:
            self.logger.warning("止损可能过于激进相对于 ROI")

### 多目标优化

您可以创建优化多个目标的损失函数：

```python
class MultiObjectiveHyperOptLoss(IHyperOptLoss):

    @staticmethod
    def hyperopt_loss_function(results: DataFrame, **kwargs) -> float:
        """
        多目标优化：利润、夏普比率和最大回撤
        """
        if len(results) == 0:
            return 1000

        # 计算各种指标
        total_profit = results['profit_ratio'].sum()
        profit_std = results['profit_ratio'].std()

        # 夏普比率
        if profit_std > 0:
            sharpe = total_profit / profit_std
        else:
            sharpe = 0

        # 最大回撤
        cumulative = results['profit_ratio'].cumsum()
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max).min()

        # 组合损失（权重可调整）
        profit_loss = -total_profit * 0.4
        sharpe_loss = -sharpe * 0.3
        drawdown_loss = abs(drawdown) * 0.3

        return profit_loss + sharpe_loss + drawdown_loss
```

## 覆盖预定义空间（新方法）

从 Freqtrade 2021.9 开始，推荐使用嵌套的 `HyperOpt` 类来覆盖预定义空间：

```python
from freqtrade.optimize.space import Categorical, Dimension, Integer, SKDecimal

class MyAwesomeStrategy(IStrategy):
    class HyperOpt:
        # 定义自定义止损空间
        def stoploss_space():
            return [SKDecimal(-0.05, -0.01, decimals=3, name='stoploss')]

        # 定义自定义 ROI 空间
        def roi_space() -> List[Dimension]:
            return [
                Integer(10, 120, name='roi_t1'),
                Integer(10, 60, name='roi_t2'),
                Integer(10, 40, name='roi_t3'),
                SKDecimal(0.01, 0.04, decimals=3, name='roi_p1'),
                SKDecimal(0.01, 0.07, decimals=3, name='roi_p2'),
                SKDecimal(0.01, 0.20, decimals=3, name='roi_p3'),
            ]

        def generate_roi_table(params: Dict) -> dict[int, float]:
            roi_table = {}
            roi_table[0] = params['roi_p1'] + params['roi_p2'] + params['roi_p3']
            roi_table[params['roi_t3']] = params['roi_p1'] + params['roi_p2']
            roi_table[params['roi_t3'] + params['roi_t2']] = params['roi_p1']
            roi_table[params['roi_t3'] + params['roi_t2'] + params['roi_t1']] = 0
            return roi_table

        def trailing_space() -> List[Dimension]:
            return [
                Categorical([True], name='trailing_stop'),
                SKDecimal(0.01, 0.35, decimals=3, name='trailing_stop_positive'),
                SKDecimal(0.001, 0.1, decimals=3, name='trailing_stop_positive_offset_p1'),
                Categorical([True, False], name='trailing_only_offset_is_reached'),
            ]

        # 定义自定义 max_open_trades 空间
        def max_open_trades_space() -> List[Dimension]:
            return [
                Integer(-1, 10, name='max_open_trades'),
            ]
```

### 动态参数

参数也可以动态定义，但必须在调用 [`bot_start()` 回调](strategy-callbacks.md#bot-start)后对实例可用：

```python
class MyAwesomeStrategy(IStrategy):

    def bot_start(self, **kwargs) -> None:
        self.buy_adx = IntParameter(20, 30, default=30, optimize=True)

        # 根据交易对动态设置参数
        if 'BTC' in self.config.get('pair_whitelist', []):
            self.btc_rsi = IntParameter(25, 35, default=30, optimize=True)
```

!!! Warning
    以这种方式创建的参数不会显示在 `list-strategies` 参数计数中。

### 覆盖基础估计器

您可以通过在 HyperOpt 子类中实现 `generate_estimator()` 来为超参数优化定义自己的 optuna 采样器：

```python
class MyAwesomeStrategy(IStrategy):
    class HyperOpt:
        def generate_estimator(dimensions: List['Dimension'], **kwargs):
            return "NSGAIIISampler"
```

可能的值包括：
- "NSGAIIISampler"（推荐，最通用）
- "TPESampler"
- "GPSampler"
- "CmaEsSampler"
- "QMCSampler"

或者继承自 `optuna.samplers.BaseSampler` 的类的实例。

## 空间选项

对于附加空间，scikit-optimize（与 Freqtrade 结合）提供以下空间类型：

* `Categorical` - 从类别列表中选择（例如 `Categorical(['a', 'b', 'c'], name="cat")`）
* `Integer` - 从整数范围中选择（例如 `Integer(1, 10, name='rsi')`）
* `SKDecimal` - 从有限精度的小数范围中选择（例如 `SKDecimal(0.1, 0.5, decimals=3, name='adx')`）。*仅在 freqtrade 中可用*。
* `Real` - 从全精度的小数范围中选择（例如 `Real(0.1, 0.5, name='adx')`）

您可以从 `freqtrade.optimize.space` 导入所有这些：

```python
from freqtrade.optimize.space import Categorical, Dimension, Integer, SKDecimal, Real
```

!!! Hint "SKDecimal vs. Real"
    我们建议在几乎所有情况下使用 `SKDecimal` 而不是 `Real` 空间。虽然 Real 空间提供完全精度（最多约 16 位小数），但很少需要这种精度，并且会导致不必要的长超参数优化时间。

## 高级超参数优化策略

### 分阶段优化

您可以分阶段优化不同的参数组：

```bash
# 第一阶段：优化入场和出场信号
freqtrade hyperopt --strategy MyStrategy --spaces buy sell -e 100

# 第二阶段：优化 ROI 和止损
freqtrade hyperopt --strategy MyStrategy --spaces roi stoploss -e 100

# 第三阶段：优化追踪止损
freqtrade hyperopt --strategy MyStrategy --spaces trailing -e 50
```

### 使用不同的时间范围

```bash
# 在较短时间范围内快速测试
freqtrade hyperopt --strategy MyStrategy --timerange 20230101-20230201 -e 200

# 在较长时间范围内验证
freqtrade hyperopt --strategy MyStrategy --timerange 20220101-20231201 -e 100
```

### 并行优化

```bash
# 使用多个进程并行运行
freqtrade hyperopt --strategy MyStrategy -j 4 -e 500
```

## 最佳实践

1. **从小开始**：先用少量时期（50-100）测试您的设置
2. **验证结果**：在不同时间段验证最佳参数
3. **避免过拟合**：不要在同一数据集上过度优化
4. **监控进度**：使用 `--print-all` 查看所有结果
5. **保存结果**：超参数优化结果自动保存在 `user_data/hyperopt_results/`

## 故障排除

### 常见问题

1. **内存不足**：减少时期数或使用较短的时间范围
2. **优化时间过长**：使用 `SKDecimal` 而不是 `Real`，减少参数空间
3. **结果不一致**：使用 `--random-state` 获得可重现的结果
4. **无改进**：检查损失函数是否合适，增加时期数

### 调试技巧

```python
# 在损失函数中添加调试信息
def hyperopt_loss_function(results: DataFrame, **kwargs) -> float:
    print(f"Trade count: {len(results)}")
    print(f"Total profit: {results['profit_ratio'].sum()}")
    # ... 您的损失计算
```

通过遵循这些高级技巧和最佳实践，您可以更有效地优化您的交易策略，获得更好的结果。
```
