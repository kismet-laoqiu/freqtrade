# 超参数优化

本页面解释如何通过找到最优参数来调整您的策略，这个过程称为超参数优化。机器人使用 `optuna` 包中包含的算法来完成此任务。
搜索将消耗您所有的 CPU 核心，让您的笔记本电脑听起来像战斗机，但仍然需要很长时间。

一般来说，搜索最佳参数从一些随机组合开始（有关更多详细信息，请参见[下文](#可重现的结果)），然后使用 optuna 的采样器算法之一（目前是 NSGAIIISampler）在搜索超空间中快速找到最小化[损失函数](#损失函数)值的参数组合。

超参数优化需要历史数据可用，就像回测一样（超参数优化使用不同参数多次运行回测）。
要了解如何获取您感兴趣的交易对和交易所的数据，请转到文档的[数据下载](data-download.md)部分。

!!! Bug
    如[Issue #1133](https://github.com/freqtrade/freqtrade/issues/1133)中发现的，当仅使用 1 个 CPU 核心时，超参数优化可能会崩溃

!!! Note
    自 2021.4 版本发布以来，您不再需要编写单独的超参数优化类，而可以直接在策略中配置参数。
    传统方法支持到 2021.8，并在 2021.9 中被移除。

## 安装超参数优化依赖项

由于超参数优化依赖项不是运行机器人本身所必需的，它们很重，在某些平台（如 Raspberry PI）上无法轻松构建，因此默认情况下不安装。在运行超参数优化之前，您需要安装相应的依赖项，如下面本节所述。

!!! Note
    由于超参数优化是一个资源密集型过程，不建议也不支持在 Raspberry Pi 上运行它。

### Docker

docker 镜像包含超参数优化依赖项，无需进一步操作。

### 简易安装脚本 (setup.sh) / 手动安装

```bash
source .venv/bin/activate
pip install -r requirements-hyperopt.txt
```

## 超参数优化命令参考

--8<-- "commands/hyperopt.md"

### 超参数优化检查清单

超参数优化中所有任务/可能性的检查清单

根据您要优化的空间，只需要以下部分：

* 定义带有 `space='buy'` 的参数 - 用于入场信号优化
* 定义带有 `space='sell'` 的参数 - 用于出场信号优化

!!! Note
    `populate_indicators` 需要创建任何空间可能使用的所有指标，否则超参数优化将不起作用。

很少情况下，您可能还需要创建一个名为 `HyperOpt` 的[嵌套类](advanced-hyperopt.md#overriding-pre-defined-spaces)并实现

* `roi_space` - 用于自定义 ROI 优化（如果您需要优化超空间中 ROI 参数的范围与默认值不同）
* `generate_roi_table` - 用于自定义 ROI 优化（如果您需要 ROI 表中值的范围与默认值不同，或 ROI 表中条目（步骤）的数量与默认的 4 步不同）
* `stoploss_space` - 用于自定义止损优化（如果您需要优化超空间中止损参数的范围与默认值不同）
* `trailing_space` - 用于自定义跟踪止损优化（如果您需要优化超空间中跟踪止损参数的范围与默认值不同）
* `max_open_trades_space` - 用于自定义 max_open_trades 优化（如果您需要优化超空间中 max_open_trades 参数的范围与默认值不同）

!!! Tip "快速优化 ROI、止损和跟踪止损"
    您可以快速优化 `roi`、`stoploss` 和 `trailing` 空间，而无需更改策略中的任何内容。

    ``` bash
    # 准备一个可工作的策略。
    freqtrade hyperopt --hyperopt-loss SharpeHyperOptLossDaily --spaces roi stoploss trailing --strategy MyWorkingStrategy --config config.json -e 100
    ```

### 超参数优化执行逻辑

超参数优化将首先将您的数据加载到内存中，然后为每个交易对运行一次 `populate_indicators()` 以生成所有指标，除非指定了 `--analyze-per-epoch`。

超参数优化然后会分叉到不同的进程（处理器数量，或 `-j <n>`），并一遍又一遍地运行回测，更改属于定义的 `--spaces` 的参数。

对于每组新参数，freqtrade 将首先运行 `populate_entry_trend()`，然后运行 `populate_exit_trend()`，然后运行常规回测过程来模拟交易。

回测后，结果被传递到[损失函数](#损失函数)中，该函数将评估此结果是否比以前的结果更好或更差。
基于损失函数结果，超参数优化将确定在下一轮回测中尝试的下一组参数。

### 配置您的守卫和触发器

您需要在策略文件中更改两个地方来添加新的买入超参数优化进行测试：

* 在类级别定义超参数优化应优化的参数。
* 在 `populate_entry_trend()` 中 - 使用定义的参数值而不是原始常量。

在那里您有两种不同类型的指标：1. `守卫` 和 2. `触发器`。

1. 守卫是像"如果 ADX < 10 则永不买入"或如果当前价格超过 EMA10 则永不买入这样的条件。
2. 触发器是在特定时刻实际触发买入的条件，如"当 EMA5 穿越 EMA10 时买入"或"当收盘价触及布林带下轨时买入"。

!!! Hint "守卫和触发器"
    从技术上讲，守卫和触发器之间没有区别。
    但是，本指南将做出这种区别，以明确信号不应该"粘性"。
    粘性信号是在多个蜡烛图中活跃的信号。这可能导致信号进入较晚（就在信号消失之前 - 这意味着成功的机会比在开始时要低得多）。

超参数优化将在每个时期轮次中选择一个触发器和可能多个守卫。

#### 出场信号优化

出场信号优化与入场信号优化类似，但使用 `space='sell'`。

## 定义超参数优化参数

让我们继续使用我们的示例策略，但这次我们将优化入场和出场信号的参数。

### 入场信号优化

我们将从优化入场信号开始。

在您的策略文件中，您需要添加：

```python
from freqtrade.strategy import IStrategy, DecimalParameter, IntParameter, CategoricalParameter
import talib.abstract as ta
import freqtrade.vendor.qtpylib.indicators as qtpylib

class MyAwesomeStrategy(IStrategy):
    # 策略参数
    buy_adx = DecimalParameter(20, 40, decimals=1, default=30.1, space="buy")
    buy_rsi = IntParameter(20, 40, default=30, space="buy")
    buy_adx_enabled = CategoricalParameter([True, False], default=True, space="buy")
    buy_rsi_enabled = CategoricalParameter([True, False], default=False, space="buy")
    buy_trigger = CategoricalParameter(["bb_lower", "macd_cross_signal"], default="bb_lower", space="buy")

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        # 添加所有可能在超参数优化中使用的指标
        dataframe['adx'] = ta.ADX(dataframe)
        dataframe['rsi'] = ta.RSI(dataframe)

        # 布林带
        bollinger = qtpylib.bollinger_bands(qtpylib.typical_price(dataframe), window=20, stds=2)
        dataframe['bb_lowerband'] = bollinger['lower']
        dataframe['bb_middleband'] = bollinger['mid']
        dataframe['bb_upperband'] = bollinger['upper']

        # MACD
        macd = ta.MACD(dataframe)
        dataframe['macd'] = macd['macd']
        dataframe['macdsignal'] = macd['macdsignal']
        dataframe['macdhist'] = macd['macdhist']

        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        conditions = []

        # 守卫条件
        if self.buy_adx_enabled.value:
            conditions.append(dataframe['adx'] > self.buy_adx.value)

        if self.buy_rsi_enabled.value:
            conditions.append(dataframe['rsi'] < self.buy_rsi.value)

        # 触发条件
        if self.buy_trigger.value == 'bb_lower':
            conditions.append(qtpylib.crossed_above(dataframe['close'], dataframe['bb_lowerband']))
        elif self.buy_trigger.value == 'macd_cross_signal':
            conditions.append(qtpylib.crossed_above(dataframe['macd'], dataframe['macdsignal']))

        # 检查是否有任何条件
        if conditions:
            dataframe.loc[
                reduce(lambda x, y: x & y, conditions),
                'enter_long'] = 1

        return dataframe
```

### 出场信号优化

现在让我们添加出场信号优化：

```python
class MyAwesomeStrategy(IStrategy):
    # 入场参数
    buy_adx = DecimalParameter(20, 40, decimals=1, default=30.1, space="buy")
    buy_rsi = IntParameter(20, 40, default=30, space="buy")
    buy_adx_enabled = CategoricalParameter([True, False], default=True, space="buy")
    buy_rsi_enabled = CategoricalParameter([True, False], default=False, space="buy")
    buy_trigger = CategoricalParameter(["bb_lower", "macd_cross_signal"], default="bb_lower", space="buy")

    # 出场参数
    sell_rsi = IntParameter(60, 80, default=70, space="sell")
    sell_adx = DecimalParameter(60, 80, decimals=1, default=70.1, space="sell")
    sell_adx_enabled = CategoricalParameter([True, False], default=True, space="sell")
    sell_rsi_enabled = CategoricalParameter([True, False], default=False, space="sell")
    sell_trigger = CategoricalParameter(["bb_upper", "macd_cross_signal"], default="bb_upper", space="sell")

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        conditions = []

        # 守卫条件
        if self.sell_adx_enabled.value:
            conditions.append(dataframe['adx'] > self.sell_adx.value)

        if self.sell_rsi_enabled.value:
            conditions.append(dataframe['rsi'] > self.sell_rsi.value)

        # 触发条件
        if self.sell_trigger.value == 'bb_upper':
            conditions.append(qtpylib.crossed_below(dataframe['close'], dataframe['bb_upperband']))
        elif self.sell_trigger.value == 'macd_cross_signal':
            conditions.append(qtpylib.crossed_below(dataframe['macd'], dataframe['macdsignal']))

        # 检查是否有任何条件
        if conditions:
            dataframe.loc[
                reduce(lambda x, y: x & y, conditions),
                'exit_long'] = 1

        return dataframe
```

### 参数类型

Freqtrade 支持以下参数类型：

#### IntParameter

用于整数参数：

```python
# 语法：IntParameter(low, high, default, space, optimize, load)
rsi_period = IntParameter(10, 50, default=14, space="buy")
```

#### DecimalParameter

用于浮点数参数：

```python
# 语法：DecimalParameter(low, high, decimals, default, space, optimize, load)
stoploss_value = DecimalParameter(-0.35, -0.02, decimals=3, default=-0.1, space="sell")
```

#### CategoricalParameter

用于分类参数：

```python
# 语法：CategoricalParameter(categories, default, space, optimize, load)
indicator_type = CategoricalParameter(["sma", "ema", "tema"], default="sma", space="buy")
```

#### BooleanParameter

用于布尔参数：

```python
# 语法：BooleanParameter(default, space, optimize, load)
use_rsi = BooleanParameter(default=True, space="buy")
```

### 参数属性

所有参数类型都支持以下属性：

- `space`: 参数所属的空间（"buy", "sell", "roi", "stoploss", "trailing", "protection"）
- `optimize`: 是否优化此参数（默认为 True）
- `load`: 是否从 JSON 文件加载此参数（默认为 True）

```python
# 不优化此参数，但允许从 JSON 加载
fixed_rsi = IntParameter(10, 50, default=14, space="buy", optimize=False)

# 优化此参数，但不从 JSON 加载
temp_param = IntParameter(10, 50, default=14, space="buy", load=False)
```

## 优化指标参数

您还可以优化指标本身的参数。例如，优化 RSI 周期：

```python
class MyAwesomeStrategy(IStrategy):
    # 指标参数
    rsi_period = IntParameter(10, 50, default=14, space="buy")
    adx_period = IntParameter(10, 50, default=14, space="buy")

    # 信号参数
    buy_rsi = IntParameter(20, 40, default=30, space="buy")

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        # 使用优化的参数计算指标
        for period in self.rsi_period.range:
            dataframe[f'rsi_{period}'] = ta.RSI(dataframe, timeperiod=period)

        for period in self.adx_period.range:
            dataframe[f'adx_{period}'] = ta.ADX(dataframe, timeperiod=period)

        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        # 使用当前优化的参数值
        rsi_col = f'rsi_{self.rsi_period.value}'
        adx_col = f'adx_{self.adx_period.value}'

        dataframe.loc[
            (
                (dataframe[rsi_col] < self.buy_rsi.value) &
                (dataframe[adx_col] > 25) &
                (dataframe['volume'] > 0)
            ),
            'enter_long'] = 1

        return dataframe
```

!!! Warning "指标参数优化的性能影响"
    优化指标参数会显著增加计算时间，因为需要为每个参数组合计算指标。
    建议首先优化信号参数，然后再优化指标参数。

## 优化 ROI 表

您可以优化最小 ROI 表：

```python
class MyAwesomeStrategy(IStrategy):
    # ROI 表将被自动优化
    minimal_roi = {
        "60": 0.01,
        "30": 0.02,
        "0": 0.04
    }
```

运行超参数优化时使用 `--spaces roi`：

```bash
freqtrade hyperopt --strategy MyAwesomeStrategy --spaces roi -e 100
```

## 优化止损

您可以优化止损值：

```python
class MyAwesomeStrategy(IStrategy):
    # 止损将被自动优化
    stoploss = -0.10
```

运行超参数优化时使用 `--spaces stoploss`：

```bash
freqtrade hyperopt --strategy MyAwesomeStrategy --spaces stoploss -e 100
```

## 优化追踪止损

您可以优化追踪止损参数：

```python
class MyAwesomeStrategy(IStrategy):
    # 追踪止损参数将被自动优化
    stoploss = -0.10
    trailing_stop = True
    trailing_stop_positive = 0.01
    trailing_stop_positive_offset = 0.02
    trailing_only_offset_is_reached = True
```

运行超参数优化时使用 `--spaces trailing`：

```bash
freqtrade hyperopt --strategy MyAwesomeStrategy --spaces trailing -e 100
```

## 优化最大开仓数

您可以优化最大开仓交易数：

```python
class MyAwesomeStrategy(IStrategy):
    # 这将被自动优化
    max_open_trades = 3
```

运行超参数优化时使用 `--spaces trades`：

```bash
freqtrade hyperopt --strategy MyAwesomeStrategy --spaces trades -e 100
```

## 优化保护机制

您可以优化保护机制参数：

```python
from freqtrade.strategy import IStrategy, DecimalParameter, IntParameter

class MyAwesomeStrategy(IStrategy):

    # 保护参数
    cooldown_lookback = IntParameter(2, 48, default=5, space="protection", optimize=True)
    stop_duration = IntParameter(12, 200, default=5, space="protection", optimize=True)
    use_stop_protection = BooleanParameter(default=True, space="protection", optimize=True)

    @property
    def protections(self):
        prot = []

        prot.append({
            "method": "CooldownPeriod",
            "stop_duration_candles": self.cooldown_lookback.value
        })
        if self.use_stop_protection.value:
            prot.append({
                "method": "StoplossGuard",
                "lookback_period_candles": 24,
                "trade_limit": 4,
                "stop_duration_candles": self.stop_duration.value,
                "only_per_pair": False
            })

        return prot

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        # ...

```

您可以运行超参数优化如下：
`freqtrade hyperopt --hyperopt-loss SharpeHyperOptLossDaily --strategy MyAwesomeStrategy --spaces protection`

!!! Note
    保护空间不是默认空间的一部分，仅在参数超参数优化接口中可用，而不在传统超参数优化接口中可用（需要单独的超参数优化文件）。
    如果选择了保护空间，Freqtrade 还会自动更改"--enable-protections"标志。

!!! Warning
    如果保护被定义为属性，配置中的条目将被忽略。
    因此建议不要在配置中定义保护。

## 损失函数

损失函数是超参数优化的核心。它定义了什么是"好"的结果。

Freqtrade 包含多个内置损失函数：

### 内置损失函数

* `ShortTradeDurHyperOptLoss` - 优化较短的交易持续时间
* `OnlyProfitHyperOptLoss` - 仅优化利润，忽略交易数量
* `SharpeHyperOptLoss` - 优化夏普比率
* `SharpeHyperOptLossDaily` - 优化每日夏普比率
* `SortinoHyperOptLoss` - 优化索提诺比率
* `SortinoHyperOptLossDaily` - 优化每日索提诺比率
* `MaxDrawDownHyperOptLoss` - 优化最大绝对回撤
* `MaxDrawDownRelativeHyperOptLoss` - 优化最大绝对回撤，同时调整最大相对回撤
* `MaxDrawDownPerPairHyperOptLoss` - 计算每个交易对的利润/回撤比率，返回最差结果作为目标
* `CalmarHyperOptLoss` - 优化基于交易回报相对于最大回撤计算的卡尔玛比率
* `ProfitDrawDownHyperOptLoss` - 通过最大利润和最小回撤目标进行优化
* `MultiMetricHyperOptLoss` - 通过多个关键指标进行优化以实现平衡性能

### 选择损失函数

选择合适的损失函数对于获得好的结果至关重要：

```bash
# 使用夏普比率优化
freqtrade hyperopt --hyperopt-loss SharpeHyperOptLossDaily --strategy MyStrategy

# 使用最大回撤优化
freqtrade hyperopt --hyperopt-loss MaxDrawDownHyperOptLoss --strategy MyStrategy

# 使用多指标优化
freqtrade hyperopt --hyperopt-loss MultiMetricHyperOptLoss --strategy MyStrategy
```

### 自定义损失函数

您可以创建自定义损失函数。创建自定义损失函数在[高级超参数优化](advanced-hyperopt.md)文档部分中有介绍。

## 执行超参数优化

一旦您更新了超参数优化配置，就可以运行它。
由于超参数优化尝试大量组合来找到最佳参数，因此需要时间才能获得好的结果。

我们强烈建议使用 `screen` 或 `tmux` 来防止任何连接丢失。

```bash
freqtrade hyperopt --config config.json --hyperopt-loss <hyperoptlossname> --strategy <strategyname> -e 500 --spaces all
```

使用 `-e`（`--epochs`）参数来控制超参数优化应该执行多少次回测。我们建议运行至少几百次试验，以获得有意义的结果。如果您有更多时间，运行 1000 或更多次试验可能会产生更好的结果。

`--spaces all` 选项确定应该优化所有可能的参数。可能性列出如下。

!!! Note
    超参数优化将使用超参数优化开始时间的时间戳存储超参数优化结果。
    读取命令（`hyperopt-list`、`hyperopt-show`）可以使用 `--hyperopt-filename <filename>` 来读取和显示较旧的超参数优化结果。
    您可以使用 `ls -l user_data/hyperopt_results/` 找到文件名列表。

### 使用不同历史数据源执行超参数优化

如果您想使用磁盘上的备用历史数据集来超参数优化参数，请使用 `--datadir PATH` 选项。默认情况下，超参数优化使用目录 `user_data/data` 中的数据。

### 使用较小测试集运行超参数优化

使用 `--timerange` 参数来更改您想要使用的测试集的大小。
例如，要使用一个月的数据，请将 `--timerange 20210101-20210201`（从 2021 年 1 月 - 2021 年 2 月）传递给超参数优化调用。

完整命令：

```bash
freqtrade hyperopt --strategy <strategyname> --timerange 20210101-20210201
```

### 使用较小搜索空间运行超参数优化

使用 `--spaces` 参数来限制超参数优化搜索空间。

可用空间：

* `all`: 优化所有内容
* `buy`: 仅搜索新的买入策略
* `sell`: 仅搜索新的卖出策略
* `roi`: 仅优化您策略的最小利润表
* `stoploss`: 搜索最佳止损值
* `trailing`: 搜索最佳追踪止损值
* `trades`: 搜索最佳最大开仓交易值
* `protection`: 搜索最佳保护参数（阅读[保护部分](#优化保护机制)了解如何正确定义这些）
* `default`: 除了 `trailing`、`trades` 和 `protection` 之外的 `all`
* 上述任何值的空格分隔列表，例如 `--spaces roi stoploss`

当没有指定 `--space` 命令行选项时使用的默认超参数优化搜索空间不包括 `trailing` 超空间。我们建议您在找到、验证其他超空间的最佳参数并将其粘贴到您的自定义策略中后，单独为 `trailing` 超空间运行优化。

## 理解超参数优化结果

超参数优化完成后，您可以使用结果来更新您的策略。
给定超参数优化的以下结果：

```
Best result:

    44/100:    135 trades. Avg profit  0.57%. Total profit  0.03871918 BTC (0.7722%). Avg duration 180.4 mins. Objective: 1.94367

    # Buy hyperspace params:
    buy_params = {
        'buy_adx': 44,
        'buy_rsi': 29,
        'buy_adx_enabled': False,
        'buy_rsi_enabled': True,
        'buy_trigger': 'bb_lower'
    }

    # Sell hyperspace params:
    sell_params = {
        'sell_adx': 65,
        'sell_rsi': 81,
        'sell_adx_enabled': True,
        'sell_rsi_enabled': True,
        'sell_trigger': 'bb_upper'
    }
```

您应该理解这意味着什么，并将这些参数添加到您的策略中。

### 理解超参数优化 ROI 结果

如果您正在优化 ROI（即如果优化搜索空间包含 'all'、'default' 或 'roi'），您的结果将如下所示并包含 ROI 表：

```
Best result:

    44/100:    135 trades. Avg profit  0.57%. Total profit  0.03871918 BTC (0.7722%). Avg duration 180.4 mins. Objective: 1.94367

    # ROI table:
    minimal_roi = {
        0: 0.10674,
        21: 0.09158,
        78: 0.03634,
        118: 0
    }
```

这个 ROI 表的含义：

- 如果交易运行了 118 分钟或更长时间：以任何利润出场（0%）
- 如果交易运行了 78-117 分钟：如果利润至少为 3.634% 则出场
- 如果交易运行了 21-77 分钟：如果利润至少为 9.158% 则出场
- 如果交易运行了 0-20 分钟：如果利润至少为 10.674% 则出场

如注释中所述，您也可以将其用作配置文件中 `minimal_roi` 设置的值。

#### 默认 ROI 搜索空间

如果您正在优化 ROI，Freqtrade 会为您创建 'roi' 优化超空间 - 它是 ROI 表组件的超空间。默认情况下，Freqtrade 生成的每个 ROI 表由 4 行（步骤）组成。超参数优化为 ROI 表实现自适应范围，ROI 步骤中值的范围取决于使用的时间框架。

!!! Note "减少的搜索空间"
    为了进一步限制搜索空间，小数被限制为 3 位小数（精度为 0.001）。这通常是足够的，任何比这更精确的值通常会导致过拟合结果。但是，您可以[覆盖预定义空间](advanced-hyperopt.md#overriding-pre-defined-spaces)来根据您的需要更改此设置。

### 理解超参数优化止损结果

如果您正在优化止损值（即如果优化搜索空间包含 'all'、'default' 或 'stoploss'），您的结果将如下所示并包含止损：

```
Best result:

    44/100:    135 trades. Avg profit  0.57%. Total profit  0.03871918 BTC (0.7722%). Avg duration 180.4 mins. Objective: 1.94367

    # Buy hyperspace params:
    buy_params = {
        'buy_adx': 44,
        'buy_rsi': 29,
        'buy_adx_enabled': False,
        'buy_rsi_enabled': True,
        'buy_trigger': 'bb_lower'
    }

    stoploss: -0.27996
```

在这种情况下，您应该在策略中设置 `stoploss = -0.27996`，或者在配置文件中使用 `--stoploss -0.27996`。

如注释中所述，您也可以将其用作配置文件中 `stoploss` 设置的值。

#### 默认止损搜索空间

如果您正在优化止损值，Freqtrade 会为您创建 'stoploss' 优化超空间。默认情况下，该超空间中的止损值在 -0.35...-0.02 范围内变化，这在大多数情况下是足够的。

如果您在自定义超参数优化文件中有 `stoploss_space()` 方法，请删除它以便利用 Freqtrade 默认生成的止损超参数优化空间。

如果您需要止损值在超参数优化期间在其他范围内变化，请覆盖 `stoploss_space()` 方法并在其中定义所需的范围。此方法的示例可以在[覆盖预定义空间部分](advanced-hyperopt.md#overriding-pre-defined-spaces)中找到。

!!! Note "减少的搜索空间"
    为了进一步限制搜索空间，小数被限制为 3 位小数（精度为 0.001）。这通常是足够的，任何比这更精确的值通常会导致过拟合结果。但是，您可以[覆盖预定义空间](advanced-hyperopt.md#overriding-pre-defined-spaces)来根据您的需要更改此设置。

### 理解超参数优化追踪止损结果

如果您正在优化追踪止损值（即如果优化搜索空间包含 'all' 或 'trailing'），您的结果将如下所示并包含追踪止损参数：

```
Best result:

    45/100:    606 trades. Avg profit  1.04%. Total profit  0.31555614 BTC ( 630.48%). Avg duration 150.3 mins. Objective: -1.10161

    # Trailing stop:
    trailing_stop = True
    trailing_stop_positive = 0.02001
    trailing_stop_positive_offset = 0.06038
    trailing_only_offset_is_reached = True
```

为了使用这些参数，请将它们应用到您的策略中，如注释中所述，或者在配置文件中添加它们。

#### 默认追踪止损搜索空间

如果您正在优化追踪止损值，Freqtrade 会为您创建 'trailing' 优化超空间。

### 可重现的结果

搜索最优参数从超参数空间中的一些（目前是 30 个）随机组合开始，随机超参数优化时期。这些随机时期在超参数优化输出的第一列中用星号字符（`*`）标记。

生成这些随机值的初始状态（随机状态）由 `--random-state` 命令行选项的值控制。您可以将其设置为您选择的某个任意值以获得可重现的结果。

如果您没有设置此值，它将被随机化，您将无法重现结果。

```bash
freqtrade hyperopt --config config.json --hyperopt-loss SharpeHyperOptLossDaily --strategy MyAwesomeStrategy -e 500 --random-state 42
```

## 超参数优化结果分析

运行超参数优化所需的时期数后，您可以稍后列出所有结果进行分析，仅选择最佳或盈利的结果，并显示之前评估的任何时期的详细信息。这可以通过 `hyperopt-list` 和 `hyperopt-show` 子命令完成。这些子命令的用法在[实用工具](utils.md#list-hyperopt-results)章节中描述。

## 从您的策略输出调试消息

如果您想从策略中输出调试消息，可以使用 `logging` 模块。默认情况下，Freqtrade 将输出级别为 `INFO` 或更高的所有消息。

```python
import logging

logger = logging.getLogger(__name__)

class MyAwesomeStrategy(IStrategy):

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        # 记录调试信息
        logger.info(f"Processing {metadata['pair']}")

        # 您的入场逻辑
        dataframe.loc[
            (
                # 您的条件
            ),
            'enter_long'] = 1

        # 记录找到的信号数量
        signals = dataframe['enter_long'].sum()
        logger.info(f"Found {signals} entry signals for {metadata['pair']}")

        return dataframe
```

## 验证回测结果

一旦优化的策略已实施到您的策略中，您应该回测此策略以确保一切按预期工作。

为了获得与超参数优化期间相同的结果（交易数量、持续时间、利润等），请使用与超参数优化相同的配置和参数（时间范围、时间框架等）进行回测。

### 为什么我的回测结果与超参数优化结果不匹配？

如果结果不匹配，请检查以下因素：

* 您可能在 `populate_indicators()` 中添加了超参数优化参数，在那里它们将仅为所有时期计算一次。如果您正在尝试优化多个 SMA 时间周期值，超参数优化时间周期参数应该放在 `populate_entry_trend()` 中，该函数在每个时期都会计算。请参见[优化指标参数](#优化指标参数)。
* 如果您已禁用超参数优化参数自动导出到 JSON 参数文件，请仔细检查以确保您正确地将所有超参数优化值转移到您的策略中。
* 检查日志以验证正在设置什么参数以及正在使用什么值。
* 特别注意止损、max_open_trades 和追踪止损参数，因为这些通常在配置文件中设置，这会覆盖对策略的更改。检查您的回测日志以确保没有配置无意中设置的参数（如 `stoploss`、`max_open_trades` 或 `trailing_stop`）。
* 验证您没有意外的参数 JSON 文件覆盖参数或策略中的默认超参数优化设置。
* 验证在回测中启用的任何保护在超参数优化时也启用，反之亦然。使用 `--space protection` 时，保护会自动启用以进行超参数优化。

## 下一步

您现在已经了解了如何优化策略参数。接下来您可能想要：

- 了解更多关于[高级超参数优化](advanced-hyperopt.md)的信息
- 查看[回测](backtesting.md)文档以验证您的结果
- 了解如何[分析](data-analysis.md)您的策略性能
- 查看[策略高级功能](strategy-advanced.md)以获得更多功能
