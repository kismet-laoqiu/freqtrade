# 策略自定义

本页面解释如何自定义您的策略、添加新指标和设置交易规则。

如果您还没有，请先熟悉：

- [Freqtrade 策略 101](strategy-101.md)，它提供了策略开发的快速入门
- [Freqtrade 机器人基础](bot-basics.md)，它提供了机器人如何运作的整体信息

## 开发您自己的策略

机器人包含一个默认策略文件。

此外，[策略仓库](https://github.com/freqtrade/freqtrade-strategies)中还有其他几种策略可用。

但是，您很可能对策略有自己的想法。

本文档旨在帮助您将想法转换为可工作的策略。

### 生成策略模板

要开始，您可以使用命令：

```bash
freqtrade new-strategy --strategy AwesomeStrategy
```

这将从模板创建一个名为 `AwesomeStrategy` 的新策略，该策略将使用文件名 `user_data/strategies/AwesomeStrategy.py` 定位。

!!! Note
    策略的*名称*和文件名之间有区别。在大多数命令中，Freqtrade 使用策略的*名称*，*而不是文件名*。

!!! Note
    `new-strategy` 命令生成的起始示例开箱即用不会盈利。

??? Hint "不同的模板级别"
    `freqtrade new-strategy` 有一个额外的参数 `--template`，它控制您在创建的策略中获得的预构建信息量。使用 `--template minimal` 获得没有任何指标示例的空策略，或使用 `--template advanced` 获得定义了更复杂功能的模板。

### 策略的结构

策略文件包含构建策略逻辑所需的所有信息：

- OHLCV 格式的蜡烛图数据
- 指标
- 入场逻辑
  - 信号
- 出场逻辑
  - 信号
  - 最小 ROI
  - 回调（"自定义函数"）
- 止损
  - 固定/绝对
  - 跟踪
  - 回调（"自定义函数"）
- 定价 [可选]
- 头寸调整 [可选]

机器人包含一个名为 `SampleStrategy` 的示例策略，您可以将其用作基础：`user_data/strategies/sample_strategy.py`。
您可以使用参数 `--strategy SampleStrategy` 测试它。请记住，您使用的是策略类名，而不是文件名。

此外，还有一个名为 `INTERFACE_VERSION` 的属性，它定义了机器人应该使用的策略接口版本。
当前版本是 3 - 这也是在策略中未明确设置时的默认值。

您可能会看到较旧的策略设置为接口版本 2，这些需要更新为 v3 术语，因为未来版本将要求设置此项。

使用 `trade` 命令在模拟或实盘模式下启动机器人：

```bash
freqtrade trade --strategy AwesomeStrategy
```

### 机器人模式

Freqtrade 策略可以由 Freqtrade 机器人在 5 种主要模式下处理：

- 回测
- 超参数优化
- 模拟（"前向测试"）
- 实盘
- FreqAI（此处不涵盖）

查看[配置文档](configuration.md)了解如何将机器人设置为模拟或实盘模式。

**在测试时始终使用模拟模式，因为这让您了解策略在现实中的工作方式，而不会冒资本风险。**

## 深入了解
**对于以下部分，我们将使用 [user_data/strategies/sample_strategy.py](https://github.com/freqtrade/freqtrade/blob/develop/freqtrade/templates/sample_strategy.py) 文件作为参考。**

!!! Note "策略和回测"
    为了避免回测和模拟/实盘模式之间的问题和意外差异，请注意在回测期间，完整的时间范围会一次性传递给 `populate_*()` 方法。
    因此，最好使用向量化操作（跨整个数据框，而不是循环）并避免索引引用（`df.iloc[-1]`），而是使用 `df.shift()` 来获取前一个蜡烛图。

!!! Warning "警告：使用未来数据"
    由于回测将完整的时间范围传递给 `populate_*()` 方法，策略作者需要注意避免策略利用来自未来的数据。
    本文档的[开发策略时的常见错误](#开发策略时的常见错误)部分列出了一些常见的模式。

??? Hint "前瞻性和递归分析"
    Freqtrade 包含两个有用的命令来帮助评估常见的前瞻性（使用未来数据）和递归偏差（指标值的方差）问题。在模拟或实盘模式下运行策略之前，您应该始终首先使用这些命令。请查看[前瞻性](lookahead-analysis.md)和[递归](recursive-analysis.md)分析的相关文档。

### 数据框

Freqtrade 使用 [pandas](https://pandas.pydata.org/) 来存储/提供蜡烛图 (OHLCV) 数据。
Pandas 是一个为处理表格格式的大量数据而开发的优秀库。

数据框中的每一行对应图表上的一个蜡烛图，最新的完整蜡烛图始终是数据框中的最后一个（按日期排序）。

如果我们使用 pandas 的 `head()` 函数查看主数据框的前几行，我们会看到：

```output
> dataframe.head()
                       date      open      high       low     close     volume
0 2021-11-09 23:25:00+00:00  67279.67  67321.84  67255.01  67300.97   44.62253
1 2021-11-09 23:30:00+00:00  67300.97  67301.34  67183.03  67187.01   61.38076
2 2021-11-09 23:35:00+00:00  67187.02  67187.02  67031.93  67123.81  113.42728
3 2021-11-09 23:40:00+00:00  67123.80  67222.40  67080.33  67160.48   78.96008
4 2021-11-09 23:45:00+00:00  67160.48  67160.48  66901.26  66943.37  111.39292
```

数据框是一个表格，其中列不是单个值，而是一系列数据值。因此，像下面这样的简单 python 比较将不起作用：

``` python
    if dataframe['rsi'] > 30:
        dataframe['enter_long'] = 1
```

上述部分将失败并显示 `The truth value of a Series is ambiguous [...]`。

这必须以 pandas 兼容的方式编写，以便在整个数据框上执行操作，即 `向量化`。

``` python
    dataframe.loc[
        (dataframe['rsi'] > 30)
    , 'enter_long'] = 1
```

通过这个部分，您在数据框中有一个新列，每当 RSI 高于 30 时就分配 `1`。

Freqtrade 使用这个新列作为入场信号，假设交易将随后在下一个开盘蜡烛图上开启。

Pandas 提供了计算指标的快速方法，即"向量化"。为了从这种速度中受益，建议不要使用循环，而是使用向量化方法。

向量化操作在整个数据范围内执行计算，因此与循环遍历每一行相比，在计算指标时要快得多。

??? Hint "信号 vs 交易"
    - 信号是在蜡烛图收盘时从指标生成的，是进入交易的意图。
    - 交易是执行的订单（在实盘模式下在交易所），然后交易将尽可能接近下一个蜡烛图开盘时开启。

!!! Warning "交易订单假设"
    在回测中，信号在蜡烛图收盘时生成。然后交易立即在下一个蜡烛图开盘时启动。

    在模拟和实盘中，这可能会延迟，因为需要首先分析所有交易对数据框，然后对每个交易对进行交易处理。这意味着在模拟/实盘中，您需要注意尽可能低的计算延迟，通常通过运行少量交易对并拥有具有良好时钟速度的 CPU。

#### 为什么我看不到"实时"蜡烛图数据？

Freqtrade 不在数据框中存储不完整/未完成的蜡烛图。

使用不完整数据进行策略决策被称为"重绘"，您可能会看到其他平台允许这样做。

Freqtrade 不允许。数据框中只有完整/完成的蜡烛图数据可用。

### 自定义指标

入场和出场信号需要指标。您可以通过扩展策略文件中 `populate_indicators()` 方法包含的列表来添加更多指标。

您应该只添加在 `populate_entry_trend()`、`populate_exit_trend()` 中使用的指标，或用于填充另一个指标的指标，否则性能可能会受到影响。

重要的是始终从这三个函数返回数据框，而不删除/修改列 `"open", "high", "low", "close", "volume"`，否则这些字段将包含意外的内容。

示例：

```python
def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
    """
    向给定的 DataFrame 添加几个不同的 TA 指标

    性能注意：为了获得最佳性能，请节约使用指标的数量。
    只取消注释您在策略或超参数优化配置中使用的指标，
    否则您将浪费内存和 CPU 使用率。
    :param dataframe: 来自交易所的数据的数据框
    :param metadata: 附加信息，如当前交易的交易对
    :return: 包含策略所有必需指标的数据框
    """
    dataframe['sar'] = ta.SAR(dataframe)
    dataframe['adx'] = ta.ADX(dataframe)
    stoch = ta.STOCHF(dataframe)
    dataframe['fastd'] = stoch['fastd']
    dataframe['fastk'] = stoch['fastk']
    dataframe['bb_lower'] = ta.BBANDS(dataframe, nbdevup=2, nbdevdn=2)['lowerband']
    dataframe['sma'] = ta.SMA(dataframe, timeperiod=40)
    dataframe['tema'] = ta.TEMA(dataframe, timeperiod=9)
    dataframe['mfi'] = ta.MFI(dataframe)

    return dataframe
```

!!! Note "指标计算"
    指标应该在 `populate_indicators()` 中计算，而不是在 `populate_entry_trend()` 或 `populate_exit_trend()` 中计算。
    这样可以确保指标只计算一次，并且可以在入场和出场信号中重复使用。

### 入场信号规则

编辑策略文件中的 `populate_entry_trend()` 方法来更新您的入场策略。

重要的是始终返回数据框而不删除/修改列 `"open", "high", "low", "close", "volume"`，否则这些字段将包含意外的内容。策略可能会产生无效值，或完全停止工作。

此方法还将定义一个新列 `"enter_long"`（做空时为 `"enter_short"`），该列需要包含 `1` 表示入场，`0` 表示"无操作"。`enter_long` 是一个必须设置的强制列，即使策略仅做空也是如此。

您可以通过使用 `"enter_tag"` 列来命名您的入场信号，这可以帮助稍后调试和评估您的策略。

来自 `user_data/strategies/sample_strategy.py` 的示例：

```python
def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
    """
    基于技术分析指标，为给定数据框填充买入信号
    :param dataframe: 填充了指标的数据框
    :param metadata: 附加信息，如当前交易的交易对
    :return: 包含买入列的数据框
    """
    dataframe.loc[
        (
            (qtpylib.crossed_above(dataframe['rsi'], 30)) &  # 信号：RSI 上穿 30
            (dataframe['tema'] <= dataframe['bb_middleband']) &  # 守卫条件
            (dataframe['tema'] > dataframe['tema'].shift(1)) &  # 守卫条件
            (dataframe['volume'] > 0)  # 确保成交量不为 0
        ),
        ['enter_long', 'enter_tag']] = (1, 'rsi_cross')

    return dataframe
```

!!! Note "关于 enter_long 和 enter_short"
    在 v3 策略中，`enter_long` 和 `enter_short` 列用于定义入场信号。
    - `enter_long` = 1 将触发做多入场
    - `enter_short` = 1 将触发做空入场（如果启用了做空）

    这些列应该包含 `1` 表示入场信号，`0` 表示无信号。

### 出场信号规则

编辑策略文件中的 `populate_exit_trend()` 方法来更新您的出场策略。

可以通过在配置或策略中将 `use_exit_signal` 设置为 false 来抑制出场信号。

`use_exit_signal` 不会影响[信号冲突规则](#信号冲突) - 这些规则仍然适用并可能阻止入场。

重要的是始终返回数据框而不删除/修改列 `"open", "high", "low", "close", "volume"`，否则这些字段将包含意外的内容。策略可能会产生无效值，或完全停止工作。

此方法将定义新列 `"exit_long"` 和 `"exit_short"`，这些列需要包含 `1` 表示出场，`0` 表示"无操作"。

您还可以设置 `"exit_tag"` 列，类似于 `enter_tag`。

来自 `user_data/strategies/sample_strategy.py` 的示例：

```python
def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
    """
    基于技术分析指标，为给定数据框填充出场信号
    :param dataframe: 填充了指标的数据框
    :param metadata: 附加信息，如当前交易的交易对
    :return: 包含出场列的数据框
    """
    dataframe.loc[
        (
            (qtpylib.crossed_above(dataframe['rsi'], 70)) &  # 信号：RSI 上穿 70
            (dataframe['tema'] > dataframe['bb_middleband']) &  # 守卫条件
            (dataframe['tema'] < dataframe['tema'].shift(1)) &  # 守卫条件
            (dataframe['volume'] > 0)  # 确保成交量不为 0
        ),
        ['exit_long', 'exit_tag']] = (1, 'rsi_too_high')
    return dataframe
```

### 最小 ROI

`minimal_roi` 表是一个可选的策略设置，用于在达到一定利润后出场。

```python
# 最小 ROI 设计为在以下情况下出场：
# 40+ 分钟：0.0%（禁用）
# 30+ 分钟：1.0%
# 20+ 分钟：2.0%
# 0+ 分钟：4.0%
minimal_roi = {
    "40": 0.0,
    "30": 0.01,
    "20": 0.02,
    "0": 0.04
}
```

大多数策略都会有一个最小 ROI 配置。虽然不是必需的，但建议使用它来确保您的机器人在达到一定利润后出场，并且不会无限期地持有交易。

当使用 `minimal_roi` 时，机器人将在达到配置的利润后出场，无论出场信号如何。

!!! Note "ROI 和出场信号"
    如果同时设置了 `minimal_roi` 和出场信号，机器人将在首先触发的条件下出场。

    要禁用 `minimal_roi`，请将其设置为非常高的值：
    ```python
    minimal_roi = {
        "0": 100
    }
    ```

### 止损

设置止损是保护您的资本的重要方法。

```python
# 可选的止损设置
stoploss = -0.10
```

这将在价格下跌 10% 时出场。

!!! Warning "止损和费用"
    请记住，止损是在费用之前计算的。
    因此，如果您的费用是 0.1%，而您的止损是 -0.1%，您的实际损失将是 -0.3%（-0.1% 止损 + 0.1% 入场费用 + 0.1% 出场费用）。

#### 追踪止损

追踪止损是一种动态止损，它会随着价格的有利变动而调整。

```python
# 追踪止损
stoploss = -0.10
trailing_stop = True
trailing_stop_positive = 0.01
trailing_stop_positive_offset = 0.02
trailing_only_offset_is_reached = True
```

这些设置的含义：
- `trailing_stop = True`：启用追踪止损
- `trailing_stop_positive = 0.01`：一旦利润达到 2%，止损将设置为 1%
- `trailing_stop_positive_offset = 0.02`：追踪止损的触发偏移量
- `trailing_only_offset_is_reached = True`：只有在达到偏移量后才开始追踪

### 时间框架（蜡烛图周期）

这是一个重要的策略设置，它定义了策略运行的时间框架。

```python
# 最优时间框架为 5 分钟
# 这个值可以被配置文件中的 "timeframe" 覆盖
timeframe = '5m'
```

有关可用时间框架的更多信息，请参阅[数据下载文档](data-download.md#可用的时间框架)。

### 元数据字典

`metadata` 字典包含有关当前分析的交易对的附加信息。

```python
{
    'pair': 'ETH/USDT',  # 当前交易对
}
```

`metadata` 字典将包含 `pair` 键，该键包含当前分析的交易对。

这可以用于根据交易对调整策略行为：

```python
def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
    if metadata['pair'] in ['BTC/USDT', 'ETH/USDT']:
        # 对主要币种使用不同的逻辑
        dataframe.loc[
            (dataframe['rsi'] < 30),
            'enter_long'] = 1
    else:
        # 对山寨币使用不同的逻辑
        dataframe.loc[
            (dataframe['rsi'] < 25),
            'enter_long'] = 1

    return dataframe
```

### 策略文件加载

默认情况下，freqtrade 将尝试从 `user_data/strategies` 目录加载策略。

要使用不同的目录，您可以使用 `--strategy-path` 参数：

```bash
freqtrade trade --strategy AwesomeStrategy --strategy-path /path/to/strategies
```

### 启动蜡烛图数量

大多数指标都有一个"预热"期，在此期间它们产生不可靠的值。

例如，EMA100 需要 100 个蜡烛图才能产生稳定的值。

为了解决这个问题，策略可以定义 `startup_candle_count` 来定义需要多少个历史蜡烛图：

```python
# 这个策略需要至少 200 个蜡烛图才能产生有效信号
startup_candle_count: int = 200
```

!!! Warning "使用 x 次调用获取 OHLCV"
    如果您收到类似 `WARNING - Using 3 calls to get OHLCV. This can result in slower operations for the bot. Please check if you really need 1500 candles for your strategy` 的警告 - 您应该考虑是否真的需要这么多历史数据来生成信号。
    这将导致 Freqtrade 对同一交易对进行多次调用，这显然比一次网络请求要慢。
    因此，Freqtrade 刷新蜡烛图的时间会更长 - 如果可能的话应该避免这种情况。
    这被限制为最多 5 次调用，以避免过载交易所或使 freqtrade 过于缓慢。

#### 示例

让我们尝试使用上述示例策略回测 1 个月（2019 年 1 月）的 5 分钟蜡烛图，该策略使用 EMA100。

```bash
freqtrade backtesting --timerange 20190101-20190201 --timeframe 5m
```

假设 `startup_candle_count` 设置为 400，回测知道它需要 400 个蜡烛图来生成有效的入场信号。它将从 `20190101 - (400 * 5m)` 加载数据 - 即约 2018-12-30 11:40:00。

如果此数据可用，指标将使用此扩展时间范围计算。然后在进行回测之前，将删除不稳定的启动期（直到 2019-01-01 00:00:00）。

如果数据不可用，回测将从可用数据开始，但前 400 个蜡烛图的信号可能不准确，应该忽略。

### 机器人模式

Freqtrade 策略可以由 Freqtrade 机器人在 5 种主要模式下处理：

- 回测（backtesting）
- 超参数优化（hyperopting）
- 模拟（dry，"前向测试"）
- 实盘（live）
- FreqAI（此处不涵盖）

查看[配置文档](configuration.md)了解如何将机器人设置为模拟或实盘模式。

**在测试时始终使用模拟模式，因为这可以让您了解策略在现实中的表现，而不会冒资本风险。**

### 为什么我看不到"实时"蜡烛图数据？

Freqtrade 不会在数据框中存储不完整/未完成的蜡烛图。

使用不完整数据进行策略决策被称为"重绘"，您可能会看到其他平台允许这样做。

Freqtrade 不允许。数据框中只有完整/完成的蜡烛图数据可用。

### 自定义指标

入场和出场信号需要指标。您可以通过扩展策略文件中 `populate_indicators()` 方法包含的列表来添加更多指标。

您应该只添加在 `populate_entry_trend()`、`populate_exit_trend()` 中使用的指标，或用于填充另一个指标的指标，否则性能可能会受到影响。

```python
def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
    """
    添加几个不同的技术分析指标
    """
    # Momentum 指标
    # ------------------------------------

    # ADX
    dataframe['adx'] = ta.ADX(dataframe)

    # # Plus Directional Indicator / Movement
    # dataframe['plus_dm'] = ta.PLUS_DM(dataframe)
    # dataframe['plus_di'] = ta.PLUS_DI(dataframe)

    # # Minus Directional Indicator / Movement
    # dataframe['minus_dm'] = ta.MINUS_DM(dataframe)
    # dataframe['minus_di'] = ta.MINUS_DI(dataframe)

    # # Aroon, Aroon Oscillator
    # aroon = ta.AROON(dataframe)
    # dataframe['aroonup'] = aroon['aroonup']
    # dataframe['aroondown'] = aroon['aroondown']
    # dataframe['aroonosc'] = ta.AROONOSC(dataframe)

    # # Awesome Oscillator
    # dataframe['ao'] = qtpylib.awesome_oscillator(dataframe)

    # # Keltner Channel
    # keltner = qtpylib.keltner_channel(dataframe)
    # dataframe["kc_upperband"] = keltner["upper"]
    # dataframe["kc_lowerband"] = keltner["lower"]
    # dataframe["kc_middleband"] = keltner["mid"]
    # dataframe["kc_percent"] = (
    #     (dataframe["close"] - dataframe["kc_lowerband"]) /
    #     (dataframe["kc_upperband"] - dataframe["kc_lowerband"])
    # )
    # dataframe["kc_width"] = (
    #     (dataframe["kc_upperband"] - dataframe["kc_lowerband"]) / dataframe["kc_middleband"]
    # )

    # # Ultimate Oscillator
    # dataframe['uo'] = ta.ULTOSC(dataframe)

    # # Commodity Channel Index: values [Oversold:-100, Overbought:100]
    # dataframe['cci'] = ta.CCI(dataframe)

    # RSI
    dataframe['rsi'] = ta.RSI(dataframe)

    # # Inverse Fisher transform on RSI: values [-1.0, 1.0] (https://goo.gl/2JGGoy)
    # rsi = 0.1 * (dataframe['rsi'] - 50)
    # dataframe['fisher_rsi'] = (np.exp(2 * rsi) - 1) / (np.exp(2 * rsi) + 1)

    # # Inverse Fisher transform on RSI normalized: values [0.0, 100.0] (https://goo.gl/2JGGoy)
    # dataframe['fisher_rsi_norma'] = 50 * (dataframe['fisher_rsi'] + 1)

    # # Stochastic Slow
    # stoch = ta.STOCH(dataframe)
    # dataframe['slowd'] = stoch['slowd']
    # dataframe['slowk'] = stoch['slowk']

    # Stochastic Fast
    stoch_fast = ta.STOCHF(dataframe)
    dataframe['fastd'] = stoch_fast['fastd']
    dataframe['fastk'] = stoch_fast['fastk']

    # # Stochastic RSI
    # Please read https://github.com/freqtrade/freqtrade/issues/2961 before using this.
    # STOCHRSI is NOT aligned with tradingview, which may result in non-expected results.
    # stoch_rsi = ta.STOCHRSI(dataframe)
    # dataframe['fastd_rsi'] = stoch_rsi['fastd']
    # dataframe['fastk_rsi'] = stoch_rsi['fastk']

    # MACD
    macd = ta.MACD(dataframe)
    dataframe['macd'] = macd['macd']
    dataframe['macdsignal'] = macd['macdsignal']
    dataframe['macdhist'] = macd['macdhist']

    # MFI
    dataframe['mfi'] = ta.MFI(dataframe)

    # # ROC
    # dataframe['roc'] = ta.ROC(dataframe)

    # 重叠研究
    # ------------------------------------

    # Bollinger Bands
    bollinger = qtpylib.bollinger_bands(qtpylib.typical_price(dataframe), window=20, stds=2)
    dataframe['bb_lowerband'] = bollinger['lower']
    dataframe['bb_middleband'] = bollinger['mid']
    dataframe['bb_upperband'] = bollinger['upper']
    dataframe["bb_percent"] = (
        (dataframe["close"] - dataframe["bb_lowerband"]) /
        (dataframe["bb_upperband"] - dataframe["bb_lowerband"])
    )
    dataframe["bb_width"] = (
        (dataframe["bb_upperband"] - dataframe["bb_lowerband"]) / dataframe["bb_middleband"]
    )

    # Parabolic SAR
    dataframe['sar'] = ta.SAR(dataframe)

    # TEMA - Triple Exponential Moving Average
    dataframe['tema'] = ta.TEMA(dataframe, timeperiod=9)

    # 周期指标
    # ------------------------------------

    # Hilbert Transform Indicator - SineWave
    hilbert = ta.HT_SINE(dataframe)
    dataframe['htsine'] = hilbert['sine']
    dataframe['htleadsine'] = hilbert['leadsine']

    # 图表类型
    # ------------------------------------

    # Heikin Ashi Strategy
    heikinashi = qtpylib.heikinashi(dataframe)
    dataframe['ha_open'] = heikinashi['open']
    dataframe['ha_close'] = heikinashi['close']
    dataframe['ha_high'] = heikinashi['high']
    dataframe['ha_low'] = heikinashi['low']

    return dataframe
```

!!! Note "指标库"
    Freqtrade 支持多个技术分析库：
    - [TA-Lib](https://github.com/mrjbq7/ta-lib) - 通过 `ta` 前缀访问
    - [qtpylib](https://github.com/ranaroussi/qtpylib) - 通过 `qtpylib` 前缀访问
    - [pandas-ta](https://github.com/twopirllc/pandas-ta) - 可选安装

### 信息对（Informative Pairs）

#### 获取其他时间框架的数据

有时您可能希望在策略中使用来自不同时间框架的数据。

例如，您可能希望：
- 在 5 分钟时间框架上交易
- 但使用 1 小时时间框架的信号

为此，您可以使用信息对功能。

```python
from freqtrade.strategy import IStrategy, informative

class AwesomeStrategy(IStrategy):

    # 策略在 5m 时间框架上运行
    timeframe = '5m'

    # 但我们想要 1h 的数据用于信号生成
    @informative('1h')
    def populate_indicators_1h(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe['rsi'] = ta.RSI(dataframe, 14)
        return dataframe

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        # 策略时间框架指标
        dataframe['volume_sma'] = dataframe['volume'].rolling(10).mean()
        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (
                (dataframe['rsi_1h'] < 30) &  # 1h RSI 超卖
                (dataframe['volume'] > dataframe['volume_sma'])  # 5m 成交量高于平均
            ),
            'enter_long'] = 1
        return dataframe
```

在这个例子中：
- 策略在 5 分钟时间框架上运行
- `@informative('1h')` 装饰器告诉 Freqtrade 获取 1 小时数据
- 1 小时数据的指标在 `populate_indicators_1h()` 中计算
- 1 小时指标在主数据框中可用，列名后缀为 `_1h`

#### 获取其他交易对的数据

您还可以获取其他交易对的数据：

```python
from freqtrade.strategy import IStrategy, informative

class AwesomeStrategy(IStrategy):

    timeframe = '5m'

    # 获取 BTC/USDT 的 1h 数据
    @informative('1h', 'BTC/USDT')
    def populate_indicators_btc_1h(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe['rsi'] = ta.RSI(dataframe, 14)
        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (
                (dataframe['rsi_BTC/USDT_1h'] < 30) &  # BTC 1h RSI 超卖
                (dataframe['close'] > dataframe['close'].shift(1))  # 当前对价格上涨
            ),
            'enter_long'] = 1
        return dataframe
```

#### 手动信息对

如果您需要更多控制，可以手动定义信息对：

```python
def informative_pairs(self):
    """
    定义需要的额外信息对
    """
    pairs = self.dp.current_whitelist()
    informative_pairs = []

    # 为每个交易对添加 1h 时间框架
    for pair in pairs:
        informative_pairs.append((pair, '1h'))

    # 添加 BTC 作为信息对
    informative_pairs.append(('BTC/USDT', '1h'))
    informative_pairs.append(('ETH/USDT', '4h'))

    return informative_pairs

def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
    # 获取信息对数据
    inf_1h = self.dp.get_pair_dataframe(pair=metadata['pair'], timeframe='1h')
    inf_btc = self.dp.get_pair_dataframe(pair='BTC/USDT', timeframe='1h')

    # 计算信息对指标
    inf_1h['rsi'] = ta.RSI(inf_1h, 14)
    inf_btc['rsi'] = ta.RSI(inf_btc, 14)

    # 合并到主数据框
    dataframe = merge_informative_pair(dataframe, inf_1h, self.timeframe, '1h', ffill=True)
    dataframe = merge_informative_pair(dataframe, inf_btc, self.timeframe, '1h',
                                     ffill=True, append_timeframe=False, suffix='_btc')

    return dataframe
```

!!! Warning "信息对性能"
    由于这些交易对将作为常规白名单刷新的一部分进行刷新，最好保持此列表简短。
    可以指定所有时间框架和所有交易对，只要它们在使用的交易所上可用（且活跃）。
    但是，最好尽可能使用重采样到更长的时间框架，以避免用太多请求轰炸交易所并面临被阻止的风险。

### 数据提供者

数据提供者是一个中央点，用于获取有关当前白名单、历史数据（OHLCV）、订单簿数据等的信息。

```python
# 在策略中可用的数据提供者方法
if self.dp:
    # 获取当前白名单
    pairs = self.dp.current_whitelist()

    # 获取历史数据
    dataframe_1h = self.dp.get_pair_dataframe('BTC/USDT', '1h')

    # 获取订单簿数据（仅在实盘/模拟模式下）
    if self.dp.runmode.value in ('live', 'dry_run'):
        ob = self.dp.orderbook(metadata['pair'], 1)
        dataframe['best_bid'] = ob['bids'][0][0]
        dataframe['best_ask'] = ob['asks'][0][0]
```

#### 可用方法

- `available_pairs` - 返回可用交易对的列表
- `current_whitelist()` - 返回当前白名单
- `get_pair_dataframe(pair, timeframe)` - 返回指定交易对和时间框架的数据框
- `get_analyzed_dataframe(pair, timeframe)` - 返回分析后的数据框（包含指标）
- `historic_ohlcv(pair, timeframe)` - 返回存储在磁盘上的历史数据
- `market(pair)` - 返回交易对的市场数据：费用、限制、精度、活动标志等
- `ohlcv(pair, timeframe)` - 当前缓存的蜡烛图（OHLCV）数据
- `orderbook(pair, maximum)` - 返回最新的订单簿数据
- `runmode` - 返回当前运行模式（live、dry_run、backtest 等）

### 完整的数据提供者示例

```python
from freqtrade.strategy import IStrategy
import talib.abstract as ta
import pandas as pd

class DataProviderStrategy(IStrategy):

    timeframe = '5m'

    def informative_pairs(self):
        # 添加 BTC 作为信息对
        return [('BTC/USDT', '1h')]

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        # 基本指标
        dataframe['rsi'] = ta.RSI(dataframe, 14)

        # 使用数据提供者获取额外信息
        if self.dp:
            # 获取 BTC 1h 数据
            btc_1h = self.dp.get_pair_dataframe('BTC/USDT', '1h')
            if not btc_1h.empty:
                btc_1h['rsi'] = ta.RSI(btc_1h, 14)
                # 将 BTC RSI 合并到主数据框
                dataframe = pd.merge(dataframe, btc_1h[['date', 'rsi']],
                                   on='date', how='left', suffixes=('', '_btc'))
                dataframe['rsi_btc'].fillna(method='ffill', inplace=True)

            # 在实盘/模拟模式下获取订单簿数据
            if self.dp.runmode.value in ('live', 'dry_run'):
                ob = self.dp.orderbook(metadata['pair'], 1)
                if ob:
                    dataframe['best_bid'] = ob['bids'][0][0]
                    dataframe['best_ask'] = ob['asks'][0][0]
                    dataframe['bid_ask_spread'] = dataframe['best_ask'] - dataframe['best_bid']

        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        conditions = []

        # 基本条件
        conditions.append(dataframe['rsi'] < 30)

        # 如果有 BTC 数据，添加 BTC 条件
        if 'rsi_btc' in dataframe.columns:
            conditions.append(dataframe['rsi_btc'] > 40)

        # 如果有订单簿数据，检查价差
        if 'bid_ask_spread' in dataframe.columns:
            conditions.append(dataframe['bid_ask_spread'] < dataframe['close'] * 0.001)

        if conditions:
            dataframe.loc[
                reduce(lambda x, y: x & y, conditions),
                'enter_long'] = 1

        return dataframe
```

### 阻止特定交易对的交易

Freqtrade 在交易对退出时会自动锁定交易对当前蜡烛图（直到该蜡烛图结束），防止该交易对立即重新入场。

这是为了防止在单个蜡烛图内出现许多频繁交易的"瀑布"。

被锁定的交易对将显示消息 `Pair <pair> is currently locked.`。

#### 从策略内锁定交易对

有时可能希望在某些事件发生后锁定交易对（例如，连续多次亏损交易）。

```python
from freqtrade.persistence import Trade
from datetime import datetime, timedelta, timezone

# 在 populate_indicators 中（或 populate_entry_trend 中）：
if self.config['runmode'].value in ('live', 'dry_run'):
    # 获取过去 2 天的已关闭交易
    trades = Trade.get_trades_proxy(
        pair=metadata['pair'], is_open=False,
        open_date=datetime.now(timezone.utc) - timedelta(days=2))
    # 分析您想要锁定交易对的条件...每个策略可能都不同
    sumprofit = sum(trade.close_profit for trade in trades)
    if sumprofit < 0:
        # 锁定交易对 12 小时
        self.lock_pair(metadata['pair'], until=datetime.now(timezone.utc) + timedelta(hours=12))
```

### 打印主数据框

要检查当前主数据框，您可以在 `populate_entry_trend()` 或 `populate_exit_trend()` 中发出打印语句。
您可能还想打印交易对，以便清楚当前显示的是什么数据。

```python
def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
    dataframe.loc[
        (
            #>> 任何条件 <<<
        ),
        ['enter_long', 'enter_tag']] = (1, 'somestring')

    # 打印分析的交易对
    print(f"result for {metadata['pair']}")

    # 检查最后 5 行
    print(dataframe.tail())

    return dataframe
```

### 开发策略时的常见错误

在开发策略时，有一些常见的陷阱需要避免。

这是一个常见的痛点，可能导致回测和模拟/实盘运行方法之间的巨大差异。查看未来的策略在回测期间表现良好，通常具有令人难以置信的利润或胜率，但在实际条件下会失败或表现不佳。

以下列表包含一些应该避免的常见模式，以防止挫折：

#### 前瞻性偏差

- 不要使用 `dataframe.iloc[-1]` 或任何其他引用"当前"蜡烛图的方法。在回测中，这将引用"未来"数据。
- 不要使用 `.resample('1h')`。这使用周期间隔的左边界，因此将数据从小时边界移动到小时开始。请改用 `.resample('1h', label='right')`。
- 不要使用 `.merge()` 将较长的时间框架合并到较短的时间框架上。相反，使用[信息对](#信息对informative-pairs)助手。（普通合并可能隐式导致前瞻性偏差，因为日期指的是开盘日期，而不是收盘日期）。

#### 其他常见错误

- 不要使用 `dataframe['volume'].mean()` 来计算平均成交量。这将计算整个数据框的平均值，包括未来数据。使用 `dataframe['volume'].rolling(window=X).mean()` 代替。
- 不要在指标计算中使用未来数据。

### 信号冲突

当冲突信号碰撞时（例如，`'enter_long'` 和 `'exit_long'` 都设置为 `1`），freqtrade 将不执行任何操作并忽略入场信号。这将避免立即入场和退出的交易。显然，这可能导致错过入场机会。

以下规则适用，如果设置了 3 个信号中的多个，入场信号将被忽略：

- `enter_long` -> `exit_long`、`enter_short`
- `enter_short` -> `exit_short`、`enter_long`

### 进一步的策略想法

要获得更多策略想法，请前往[策略仓库](https://github.com/freqtrade/freqtrade-strategies)。随意将它们用作示例，但结果将取决于当前市场情况、使用的交易对等。因此，这些策略应该仅被视为学习目的，而不是真实世界的交易。请首先为您的交易所/所需交易对回测策略，然后模拟运行以仔细评估，并自担风险使用。

随意将其中任何一个用作您自己策略的灵感。我们很高兴接受包含新策略的拉取请求到仓库。

### 下一步

您现在已经了解了如何创建自己的策略。接下来您可能想要：

- 了解更多关于[策略回调](strategy-callbacks.md)的信息
- 查看[高级策略](strategy-advanced.md)文档以获得更高级的功能
- 了解如何[回测](backtesting.md)您的策略
- 了解如何[优化](hyperopt.md)您的策略参数

## 策略版本控制

策略可以有版本控制，以确保向后兼容性。

```python
# 策略接口版本 - 允许向后兼容性
# 更改：
# 2 -> 3: 重命名 populate_buy_trend 为 populate_entry_trend
#         重命名 populate_sell_trend 为 populate_exit_trend
INTERFACE_VERSION = 3
```

当前版本是 3 - 当在策略中没有明确设置时，这也是默认值。

您可能会看到较旧的策略设置为接口版本 2，这些需要更新为 v3 术语，因为未来版本将要求设置此项。

### 从 v2 迁移到 v3

主要变化是方法和列名的重命名：

**方法重命名：**
- `populate_buy_trend()` → `populate_entry_trend()`
- `populate_sell_trend()` → `populate_exit_trend()`

**列重命名：**
- `buy` → `enter_long`
- `sell` → `exit_long`
- `buy_tag` → `enter_tag`
- `sell_tag` → `exit_tag`

**新增列（用于做空）：**
- `enter_short` - 做空入场信号
- `exit_short` - 做空出场信号

### 策略模板

Freqtrade 提供了几个策略模板来帮助您开始：

#### 最小模板

```bash
freqtrade new-strategy --strategy MyStrategy --template minimal
```

这将创建一个最小的策略模板，没有任何预定义的指标。

#### 高级模板

```bash
freqtrade new-strategy --strategy MyStrategy --template advanced
```

这将创建一个包含更多高级功能的策略模板，包括：
- 信息对示例
- 自定义止损
- 自定义出场
- 位置调整

### 策略测试

在部署策略之前，强烈建议进行彻底测试：

1. **回测**：使用历史数据测试策略
2. **前瞻性分析**：检查策略是否使用未来数据
3. **递归分析**：检查指标值的方差
4. **模拟交易**：在实时市场条件下测试，但不使用真实资金
5. **小额实盘**：使用少量资金进行实盘测试

```bash
# 回测
freqtrade backtesting --strategy MyStrategy --timerange 20230101-20231201

# 前瞻性分析
freqtrade lookahead-analysis --strategy MyStrategy

# 递归分析
freqtrade recursive-analysis --strategy MyStrategy

# 模拟交易
freqtrade trade --strategy MyStrategy --dry-run
```

这样可以确保您的策略在实际交易中表现如预期。
