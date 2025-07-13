# Freqtrade 策略 101：策略开发快速入门

为了这个快速入门的目的，我们假设您熟悉交易的基础知识，并且已经阅读了 [Freqtrade 基础](bot-basics.md) 页面。

## 必需知识

Freqtrade 中的策略是一个 Python 类，定义了买卖加密货币 `资产` 的逻辑。

资产被定义为 `交易对`，代表 `币种` 和 `基础货币`。币种是您使用另一种货币作为基础货币进行交易的资产。

数据由交易所以 `蜡烛图` 的形式提供，蜡烛图由六个值组成：`日期`、`开盘价`、`最高价`、`最低价`、`收盘价` 和 `成交量`。

`技术分析` 函数使用各种计算和统计公式分析蜡烛图数据，并产生称为 `指标` 的次要值。

指标在资产对蜡烛图上进行分析以生成 `信号`。

信号在加密货币 `交易所` 上转化为 `订单`，即 `交易`。

我们使用术语 `入场` 和 `出场` 而不是 `买入` 和 `卖出`，因为 Freqtrade 支持 `多头` 和 `空头` 交易。

- **多头**：您基于基础货币购买币种，例如使用 USDT 作为基础货币购买币种 BTC，您通过以比您支付的更高的价格出售币种来获利。在多头交易中，通过币种价值相对于基础货币上涨来获利。
- **空头**：您从交易所借入币种形式的资本，稍后偿还币种的基础货币价值。在空头交易中，通过币种价值相对于基础货币下跌来获利（您以较低的价格偿还贷款）。

虽然 Freqtrade 支持某些交易所的现货和期货市场，但为了简单起见，我们将只关注现货（多头）交易。

## 基本策略的结构

### 主数据框

Freqtrade 策略使用称为 `数据框` 的具有行和列的表格数据结构来生成进入和退出交易的信号。

您配置的交易对列表中的每个交易对都有自己的数据框。数据框由 `日期` 列索引，例如 `2024-06-31 12:00`。

接下来的 5 列代表 `开盘价`、`最高价`、`最低价`、`收盘价` 和 `成交量` (OHLCV) 数据。

### 填充指标值

`populate_indicators` 函数向数据框添加代表技术分析指标值的列。

常见指标的示例包括相对强弱指数、布林带、资金流量指数、移动平均线和平均真实范围。

通过调用技术分析函数（例如 ta-lib 的 RSI 函数 `ta.RSI()`）并将它们分配给列名（例如 `rsi`）来向数据框添加列

```python
dataframe['rsi'] = ta.RSI(dataframe)
```

??? Hint "技术分析库"
    不同的库以不同的方式生成指标值。请查看每个库的文档以了解如何使用它们。
    
    常用的技术分析库包括：
    - [TA-Lib](https://ta-lib.github.io/ta-lib-python/) - 最常用的技术分析库
    - [pandas-ta](https://github.com/twopirllc/pandas-ta) - 基于 pandas 的技术分析库
    - [qtpylib](https://github.com/ranaroussi/qtpylib) - 量化交易 Python 库

### 填充入场信号

`populate_entry_trend` 函数向数据框添加一个名为 `enter_long` 的列（对于多头交易）或 `enter_short`（对于空头交易），其中包含布尔值（True/False），指示机器人是否应该在该特定时间点进入交易。

入场信号通常基于指标值的组合。例如：

```python
dataframe.loc[
    (
        (dataframe['rsi'] < 30) &  # RSI 低于 30（超卖）
        (dataframe['close'] > dataframe['sma_20'])  # 价格高于 20 期简单移动平均线
    ),
    'enter_long'] = 1
```

### 填充出场信号

`populate_exit_trend` 函数向数据框添加一个名为 `exit_long` 的列（对于多头交易）或 `exit_short`（对于空头交易），其中包含布尔值，指示机器人是否应该在该特定时间点退出交易。

出场信号的工作方式与入场信号类似：

```python
dataframe.loc[
    (
        (dataframe['rsi'] > 70) &  # RSI 高于 70（超买）
        (dataframe['close'] < dataframe['sma_20'])  # 价格低于 20 期简单移动平均线
    ),
    'exit_long'] = 1
```

## 基本策略示例

以下是一个简单策略的完整示例：

```python
from freqtrade.strategy import IStrategy
import talib.abstract as ta
import pandas as pd

class SimpleRSIStrategy(IStrategy):
    # 策略参数
    minimal_roi = {
        "60": 0.01,
        "30": 0.02,
        "0": 0.04
    }
    
    stoploss = -0.10
    timeframe = '5m'
    
    def populate_indicators(self, dataframe: pd.DataFrame, metadata: dict) -> pd.DataFrame:
        # 添加 RSI 指标
        dataframe['rsi'] = ta.RSI(dataframe, timeperiod=14)
        
        # 添加简单移动平均线
        dataframe['sma_20'] = ta.SMA(dataframe, timeperiod=20)
        
        return dataframe
    
    def populate_entry_trend(self, dataframe: pd.DataFrame, metadata: dict) -> pd.DataFrame:
        dataframe.loc[
            (
                (dataframe['rsi'] < 30) &
                (dataframe['close'] > dataframe['sma_20'])
            ),
            'enter_long'] = 1
        
        return dataframe
    
    def populate_exit_trend(self, dataframe: pd.DataFrame, metadata: dict) -> pd.DataFrame:
        dataframe.loc[
            (
                (dataframe['rsi'] > 70)
            ),
            'exit_long'] = 1
        
        return dataframe
```

## 下一步

现在您已经了解了策略的基本结构，您可以：

1. 阅读[策略自定义](strategy-customization.md)文档以了解更高级的功能
2. 查看[策略仓库](https://github.com/freqtrade/freqtrade-strategies)中的示例策略
3. 学习如何[回测](backtesting.md)您的策略
4. 了解如何[优化](hyperopt.md)您的策略参数

!!! Warning "风险警告"
    在使用真实资金之前，请始终彻底测试您的策略。使用模拟模式运行一段时间，并在历史数据上进行回测。
