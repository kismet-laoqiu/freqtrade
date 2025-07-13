# 绘图

本页面解释如何绘制价格、指标和利润。

!!! Warning "已弃用"
    本页面中描述的命令（`plot-dataframe`、`plot-profit`）应被视为已弃用，处于维护模式。
    这主要是因为即使中等大小的图表也可能导致性能问题，也因为"存储文件并在浏览器中打开"从 UI 角度来看不是很直观。

    虽然没有立即移除它们的计划，但它们没有得到积极维护 - 如果需要重大更改来保持它们工作，可能会在短期内被移除。

    请使用 [FreqUI](freq-ui.md) 来满足绘图需求，它不会遇到相同的性能问题。

## 安装 / 设置

绘图模块使用 Plotly 库。您可以通过运行以下命令来安装/升级：

``` bash
pip install -U -r requirements-plot.txt
```

## 绘制价格和指标

`freqtrade plot-dataframe` 子命令显示一个包含三个子图的交互式图表：

* 带有蜡烛图和跟随价格的指标（sma/ema）的主图
* 成交量柱状图
* 由 `--indicators2` 指定的其他指标

![plot-dataframe](../docs/assets/plot-dataframe.png)

可能的参数：

--8<-- "commands/plot-dataframe.md"

示例：

``` bash
freqtrade plot-dataframe -p BTC/ETH --strategy AwesomeStrategy
```

`-p/--pairs` 参数可用于指定您想要绘制的交易对。

!!! Note
    `freqtrade plot-dataframe` 子命令为每个交易对生成一个绘图文件。

指定自定义指标。
使用 `--indicators1` 用于主图，使用 `--indicators2` 用于下面的子图（如果值的范围与价格不同）。

``` bash
freqtrade plot-dataframe --strategy AwesomeStrategy -p BTC/ETH --indicators1 sma ema --indicators2 macd
```

### 进一步使用示例

要绘制多个交易对，用空格分隔它们：

``` bash
freqtrade plot-dataframe --strategy AwesomeStrategy -p BTC/ETH XRP/ETH
```

要绘制时间范围（放大）

``` bash
freqtrade plot-dataframe --strategy AwesomeStrategy -p BTC/ETH --timerange=20180801-20180805
```

要绘制存储在数据库中的交易，请结合使用 `--db-url` 和 `--trade-source DB`：

``` bash
freqtrade plot-dataframe --strategy AwesomeStrategy --db-url sqlite:///tradesv3.dry_run.sqlite -p BTC/ETH --trade-source DB
```

要绘制回测结果中的交易，请使用 `--export-filename <filename>`

``` bash
freqtrade plot-dataframe --strategy AwesomeStrategy --export-filename user_data/backtest_results/backtest-result.json -p BTC/ETH
```

### 绘制数据框基础

![plot-dataframe2](../docs/assets/plot-dataframe2.png)

`plot-dataframe` 子命令需要回测数据、策略以及包含与策略对应的交易的回测结果文件或数据库。

生成的图表将包含以下元素：

* 绿色三角形：来自策略的买入信号。（注意：不是每个买入信号都会产生交易，与青色圆圈比较。）
* 红色三角形：来自策略的卖出信号。（同样，不是每个卖出信号都会终止交易，与红色和绿色方块比较。）
* 青色圆圈：交易入场点。
* 红色方块：亏损或 0% 利润交易的出场点。
* 绿色方块：盈利交易的出场点。
* 具有与蜡烛图比例对应的值的指标（例如 SMA/EMA），由 `--indicators1` 指定。
* 成交量（主图底部的柱状图）。
* 具有不同比例值的指标（例如 MACD、RSI）在成交量柱下方，由 `--indicators2` 指定。

!!! Note "布林带"
    如果存在列 `bb_lowerband` 和 `bb_upperband`，布林带会自动添加到图表中，并绘制为从下轨到上轨的浅蓝色区域。

#### 高级绘图配置

可以在策略的 `plot_config` 参数中指定高级绘图配置。

使用 `plot_config` 时的附加功能包括：

* 为每个指标指定颜色
* 指定附加子图
* 指定指标对以填充之间的区域

下面的示例绘图配置为指标指定了固定颜色。否则，连续的绘图每次可能产生不同的颜色方案，使比较变得困难。
它还允许多个子图同时显示 MACD 和 RSI。

可以使用 `type` 键配置绘图类型。可能的类型有：

* `scatter` 对应 `plotly.graph_objects.Scatter` 类（默认）。
* `bar` 对应 `plotly.graph_objects.Bar` 类。

可以在 `plotly` 字典中指定 `plotly.graph_objects.*` 构造函数的额外参数。

带有内联注释解释过程的示例配置：

```python
@property
def plot_config(self):
    """
        有很多解决方案如何构建返回字典。
        唯一重要的是返回值。
        示例：
            plot_config = {'main_plot': {}, 'subplots': {}}

    """
    plot_config = {}
    plot_config['main_plot'] = {
        # 主图指标的配置。
        # 假设指定了 2 个参数，emashort 和 emalong。
        f'ema_{self.emashort.value}': {'color': 'red'},
        f'ema_{self.emalong.value}': {'color': '#CCCCCC'},
        # 通过省略颜色，选择随机颜色。
        'sar': {},
        # 填充 senkou_a 和 senkou_b 之间的区域
        'senkou_a': {
            'color': 'green', #可选
            'fill_to': 'senkou_b',
            'fill_label': 'Ichimoku Cloud', #可选
            'fill_color': 'rgba(255,76,46,0.2)', #可选
        },
        # 也绘制 senkou_b。不仅仅是到它的区域。
        'senkou_b': {}
    }
    plot_config['subplots'] = {
         # 创建子图 MACD
        "MACD": {
            'macd': {'color': 'blue', 'fill_to': 'macdhist'},
            'macdsignal': {'color': 'orange'},
            'macdhist': {'type': 'bar', 'plotly': {'opacity': 0.9}}
        },
        # 附加子图 RSI
        "RSI": {
            'rsi': {'color': 'red'}
        }
    }

    return plot_config
```

??? Note "作为属性（以前的方法）"
    也可以将 plot_config 分配为属性（这曾经是默认方式）。
    这有一个缺点，即策略参数不可用，阻止某些配置工作。

    ```python
        plot_config = {
            'main_plot': {
                # 主图指标的配置。
                # 指定 `ema10` 为红色，`ema50` 为灰色阴影
                'ema10': {'color': 'red'},
                'ema50': {'color': '#CCCCCC'},
                # 通过省略颜色，选择随机颜色。
                'sar': {},
            # 填充 senkou_a 和 senkou_b 之间的区域
            'senkou_a': {
                'color': 'green', #可选
                'fill_to': 'senkou_b',
                'fill_label': 'Ichimoku Cloud', #可选
                'fill_color': 'rgba(255,76,46,0.2)', #可选
            },
            # 也绘制 senkou_b。不仅仅是到它的区域。
            'senkou_b': {}
            },
            'subplots': {
                # 创建子图 MACD
                "MACD": {
                    'macd': {'color': 'blue', 'fill_to': 'macdhist'},
                    'macdsignal': {'color': 'orange'},
                    'macdhist': {'type': 'bar', 'plotly': {'opacity': 0.9}}
                },
                # 附加子图 RSI
                "RSI": {
                    'rsi': {'color': 'red'}
                }
            }
        }

    ```

!!! Note
    上述配置假设 `ema10`、`ema50`、`senkou_a`、`senkou_b`、
    `macd`、`macdsignal`、`macdhist` 和 `rsi` 是策略创建的 DataFrame 中的列。

!!! Warning
    `plotly` 参数仅在 plotly 库中受支持，不适用于 freq-ui。

!!! Note "交易位置调整"
    如果使用 `position_adjustment_enable` / `adjust_trade_position()`，交易初始买入价格在多个订单上平均，交易开始价格很可能出现在蜡烛图范围之外。

## 绘制利润

![plot-profit](../docs/assets/plot-profit.png)

`plot-profit` 子命令显示一个包含三个图的交互式图表：

* 所有交易对的平均收盘价。
* 回测产生的汇总利润。
注意这不是真实世界的利润，而更像是一个估计。
* 每个单独交易对的利润。
* 交易的并行性。
* 水下（回撤期间）。

第一个图表有助于了解整体市场的进展情况。

第二个图表将显示您的算法是否有效。
也许您想要一个稳定产生小利润的算法，或者一个行动较少但产生大波动的算法。
此图表还将突出显示最大回撤期间的开始（和结束）。

第三个图表可用于发现异常值，导致利润峰值的交易对事件。

第四个图表可以帮助您分析交易并行性，显示 max_open_trades 被最大化的频率。

`freqtrade plot-profit` 子命令的可能选项：

--8<-- "commands/plot-profit.md"

`-p/--pairs` 参数可用于限制此计算考虑的交易对。

示例：

使用自定义回测导出文件

```bash
freqtrade plot-profit  -p LTC/BTC --export-filename user_data/backtest_results/backtest-result.json
```

使用自定义数据库

```bash
freqtrade plot-profit  -p LTC/BTC --db-url sqlite:///tradesv3.sqlite --trade-source DB
```

```bash
freqtrade --datadir user_data/data/binance_save/ plot-profit -p LTC/BTC
```
