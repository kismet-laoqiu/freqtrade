# 实用工具子命令

除了实盘交易和模拟运行模式、`backtesting` 和 `hyperopt` 优化子命令，以及准备历史数据的 `download-data` 子命令外，机器人还包含许多实用工具子命令。本节将对它们进行描述。

## 创建用户目录

创建目录结构来保存您的 freqtrade 文件。
还将为您创建策略和超参数优化示例以便开始使用。
可以多次使用 - 使用 `--reset` 将重置示例策略和超参数优化文件到默认状态。

--8<-- "commands/create-userdir.md"

!!! Warning
    使用 `--reset` 可能导致数据丢失，因为这将覆盖所有示例文件而不再次询问。

```
├── backtest_results
├── data
├── hyperopt_results
├── hyperopts
│   ├── sample_hyperopt_loss.py
├── notebooks
│   └── strategy_analysis_example.ipynb
├── plot
└── strategies
    └── sample_strategy.py
```

## 创建新配置

创建新的配置文件，询问一些对配置很重要的选择问题。

--8<-- "commands/new-config.md"

!!! Warning
    只询问重要问题。Freqtrade 提供了更多配置可能性，这些在[配置文档](configuration.md#configuration-parameters)中列出

### 创建配置示例

```
$ freqtrade new-config --config user_data/config_binance.json

? Do you want to enable Dry-run (simulated trades)?  Yes
? Please insert your stake currency: BTC
? Please insert your stake amount: 0.05
? Please insert max_open_trades (Integer or -1 for unlimited open trades): 3
? Please insert your desired timeframe (e.g. 5m): 5m
? Please insert your display Currency (for reporting): USD
? Select exchange  binance
? Do you want to enable Telegram?  No
```

## 显示配置

显示配置文件（默认情况下敏感值被隐藏）。
特别适用于[分割配置文件](configuration.md#multiple-configuration-files)或[环境变量](configuration.md#environment-variables)，此命令将显示合并的配置。

![显示配置输出](../docs/assets/show-config-output.png)

--8<-- "commands/show-config.md"

``` output
Your combined configuration is:
{
  "exit_pricing": {
    "price_side": "other",
    "use_order_book": true,
    "order_book_top": 1
  },
  "stake_currency": "USDT",
  "exchange": {
    "name": "binance",
    "key": "REDACTED",
    "secret": "REDACTED",
    "ccxt_config": {},
    "ccxt_async_config": {},
  }
  // ...
}
```

!!! Warning "分享此命令提供的信息"
    我们尝试从默认输出中删除所有已知的敏感信息（不使用 `--show-sensitive`）。
    但是，请仔细检查输出中的敏感值，确保您不会意外暴露一些私人信息。

## 创建新策略

从类似于 SampleStrategy 的模板创建新策略。
文件将根据您的类名命名，不会覆盖现有文件。

结果将位于 `user_data/strategies/<strategyclassname>.py`。

--8<-- "commands/new-strategy.md"

### new-strategy 的示例用法

```bash
freqtrade new-strategy --strategy AwesomeStrategy
```

使用自定义用户目录

```bash
freqtrade new-strategy --userdir ~/.freqtrade/ --strategy AwesomeStrategy
```

使用高级模板（填充所有可选函数和方法）

```bash
freqtrade new-strategy --strategy AwesomeStrategy --template advanced
```

## 列出策略

使用 `list-strategies` 子命令查看所有可用策略。

它提供了您环境中所有可用策略的快速列表。

此子命令对于查找环境中加载策略的问题很有用：包含错误且加载失败的策略模块以红色打印（LOAD FAILED），而具有重复名称的策略以黄色打印（DUPLICATE NAME）。

--8<-- "commands/list-strategies.md"

示例：搜索默认策略目录（在默认用户目录内）。

```bash
freqtrade list-strategies
```

示例：搜索用户目录内的策略目录。

```bash
freqtrade list-strategies --userdir ~/.freqtrade/
```

示例：搜索专用策略路径。

```bash
freqtrade list-strategies --strategy-path ~/.freqtrade/strategies/
```

## 列出超参数优化损失函数

使用 `list-hyperoptloss` 子命令查看所有可用的超参数优化损失函数。

它提供了您环境中所有可用损失函数的快速列表。

此子命令对于查找环境中加载损失函数的问题很有用：包含错误且加载失败的超参数优化损失函数模块以红色打印（LOAD FAILED），而具有重复名称的超参数优化损失函数以黄色打印（DUPLICATE NAME）。

--8<-- "commands/list-hyperoptloss.md"

## 列出 freqAI 模型

使用 `list-freqaimodels` 子命令查看所有可用的 freqAI 模型。

此子命令对于查找环境中加载 freqAI 模型的问题很有用：包含错误且加载失败的模型模块以红色打印（LOAD FAILED），而具有重复名称的模型以黄色打印（DUPLICATE NAME）。

--8<-- "commands/list-freqaimodels.md"

## 列出交易所

使用 `list-exchanges` 子命令查看 Freqtrade 支持的交易所。

--8<-- "commands/list-exchanges.md"

```
$ freqtrade list-exchanges
Exchanges available for Freqtrade:
Exchange name       Supported    Markets                 Reason
------------------  -----------  ----------------------  ------------------------------------------------------------------------
binance             Official     spot, isolated futures
bitmart             Official     spot
bybit                            spot, isolated futures
gate                Official     spot, isolated futures
htx                 Official     spot
huobi                            spot
kraken              Official     spot
okx                 Official     spot, isolated futures
```

!!! info ""
    为了清晰起见，输出已减少 - 支持的和可用的交易所可能会随时间变化。

!!! Note "缺少可选交易所"
    带有"missing opt:"的值可能需要特殊配置（例如，如果缺少 `fetchTickers` 则使用订单簿） - 但理论上应该可以工作（尽管我们不能保证它们会工作）。

示例：查看 ccxt 库支持的所有交易所（包括"坏"的交易所，即已知不能与 Freqtrade 一起工作的交易所）

```
$ freqtrade list-exchanges -a
All exchanges supported by the ccxt library:
Exchange name       Valid    Supported    Markets                 Reason
------------------  -------  -----------  ----------------------  ---------------------------------------------------------------------------------
binance             True     Official     spot, isolated futures
bitflyer            False                 spot                    missing: fetchOrder. missing opt: fetchTickers.
bitmart             True     Official     spot
bybit               True                  spot, isolated futures
gate                True     Official     spot, isolated futures
htx                 True     Official     spot
kraken              True     Official     spot
okx                 True     Official     spot, isolated futures
```

!!! info ""
    减少的输出 - 支持的和可用的交易所可能会随时间变化。

## 列出时间框架

使用 `list-timeframes` 子命令查看交易所可用的时间框架列表。

--8<-- "commands/list-timeframes.md"

* 示例：查看配置文件中设置的 'binance' 交易所的时间框架：

```
$ freqtrade list-timeframes -c config_binance.json
...
Timeframes available for the exchange `binance`: 1m, 3m, 5m, 15m, 30m, 1h, 2h, 4h, 6h, 8h, 12h, 1d, 3d, 1w, 1M
```

* 示例：枚举 Freqtrade 可用的交易所并打印每个交易所支持的时间框架：
```
$ for i in `freqtrade list-exchanges -1`; do freqtrade list-timeframes --exchange $i; done
```

## 列出交易对/列出市场

`list-pairs` 和 `list-markets` 子命令允许查看交易所上可用的交易对/市场。

交易对是市场符号中基础货币部分和报价货币部分之间带有 '/' 字符的市场。
例如，在 'ETH/BTC' 交易对中，'ETH' 是基础货币，而 'BTC' 是报价货币。

对于 Freqtrade 交易的交易对，交易对报价货币由 `stake_currency` 配置设置的值定义。

您可以使用这些子命令打印任何交易对/市场的信息 - 您可以使用 `--quote BTC` 按报价货币过滤输出，或使用 `--base ETH` 选项按基础货币过滤输出。

这些子命令具有相同的用法和相同的可用选项集：

--8<-- "commands/list-pairs.md"

* 示例：列出 Binance 交易所上所有可用的交易对：

```
$ freqtrade list-pairs --exchange binance

Pairs available on exchange Binance: 1565
['ETHBTC', 'LTCBTC', 'BNBBTC', 'NEOBTC', ...]
```

* 示例：列出 Binance 交易所上所有可用的 USDT 交易对：

```
$ freqtrade list-pairs --exchange binance --quote USDT --print-list

Pairs available on exchange Binance: 384
ETHUSDT LTCUSDT BNBUSDT NEOUSDT QTUMOUSDT EOSUSDT SNTUSDT BNTUSDT GASUSDT BNBUSDT HSRUSDT OAXUSDT DNTUSDT MCOUSDT ICNUSDT WTCUSDT LRCUSDT YOYOUSDT OMGUSDT ZRXUSDT STRATUSDT SNGLSUSDT BQXUSDT KNCUSDT FUNUSDT SNMUSDT NEOUSUSDT IOTAUSDT LINKUSDT XVGUSDT CTRUSUSDT SALTUSDT MDAUSDT MTLUSDT SUBUSDT EOSUSDT NEOUSUSDT GASUSDT POWRUSDT SLSUSDT STORJUSDT ADAUSDT
```

## 测试交易对列表

使用 `test-pairlist` 子命令测试您的交易对列表配置。

--8<-- "commands/test-pairlist.md"

### 示例

使用[动态交易对列表](plugins.md#pairlists)时显示白名单。

```
freqtrade test-pairlist --config config.json --quote USDT BTC
```

## 转换数据库

`freqtrade convert-db` 可用于将您的数据库从一个系统转换到另一个系统（sqlite -> postgres，postgres -> 其他 postgres），迁移所有交易、订单和交易对锁定。

请参考[相应的文档](advanced-setup.md#use-a-different-database-system)了解不同数据库系统的要求。

--8<-- "commands/convert-db.md"

!!! Warning
    请确保仅在空的目标数据库上使用此功能。Freqtrade 将执行常规迁移，但如果条目已存在可能会失败。

## Web 服务器模式

!!! Warning "实验性"
    Web 服务器模式是一种实验性模式，用于提高回测和策略开发的生产力。
    可能仍然存在错误 - 如果您碰巧遇到这些错误，请将它们报告为 github 问题，谢谢。

以 Web 服务器模式运行 freqtrade。
Freqtrade 将启动 Web 服务器并允许 FreqUI 启动和控制回测过程。
这样做的优势是数据不会在回测运行之间重新加载（只要时间框架和时间范围保持相同）。
FreqUI 还将显示回测结果。

--8<-- "commands/webserver.md"

### Web 服务器模式 - docker

您也可以通过 docker 使用 Web 服务器模式。
启动一次性容器需要明确配置端口，因为默认情况下不暴露端口。
您可以使用 `docker compose run --rm -p 127.0.0.1:8080:8080 freqtrade webserver` 启动一个一次性容器，一旦停止就会被删除。这假设端口 8080 仍然可用且没有其他机器人在该端口上运行。

或者，您可以重新配置 docker-compose 文件以更新命令：

```yml
    command: >
      webserver
      --config /freqtrade/user_data/config.json
```

您现在可以使用 `docker compose up` 启动 Web 服务器。
这假设配置已启用 Web 服务器并为 docker 配置（监听端口 = `0.0.0.0`）。

!!! Tip
    如果您想启动实盘或模拟机器人，不要忘记将命令重置回交易命令。

## 显示以前的回测结果

允许您显示以前的回测结果。
添加 `--show-pair-list` 输出一个排序的交易对列表，您可以轻松复制/粘贴到您的配置中（省略坏的交易对）。

??? Warning "策略过拟合"
    仅使用获胜的交易对可能导致过拟合的策略，这在未来数据上不会很好地工作。在冒真钱风险之前，确保在模拟运行中广泛测试您的策略。

--8<-- "commands/backtesting-show.md"

## 详细回测分析

高级回测结果分析。

更多详情请参见[回测分析](advanced-backtesting.md#analyze-the-buyentry-and-sellexit-tags)部分。

--8<-- "commands/backtesting-analysis.md"

## 列出超参数优化结果

您可以使用 `hyperopt-list` 子命令列出超参数优化模块之前评估的超参数优化时期。

--8<-- "commands/hyperopt-list.md"

!!! Note
    `hyperopt-list` 将自动使用最新可用的超参数优化结果文件。
    您可以使用 `--hyperopt-filename` 参数覆盖此设置，并指定另一个可用的文件名（不带路径！）。

### 示例

列出所有结果，最后打印最佳结果的详细信息：
```
freqtrade hyperopt-list
```

仅列出具有正利润的时期。不打印最佳时期的详细信息，以便可以在脚本中迭代列表：
```
freqtrade hyperopt-list --profitable --no-details
```

## 显示超参数优化结果详细信息

您可以使用 `hyperopt-show` 子命令显示超参数优化模块之前评估的任何超参数优化时期的详细信息。

--8<-- "commands/hyperopt-show.md"

!!! Note
    `hyperopt-show` 将自动使用最新可用的超参数优化结果文件。
    您可以使用 `--hyperopt-filename` 参数覆盖此设置，并指定另一个可用的文件名（不带路径！）。

### 示例

打印时期 168 的详细信息（时期编号由 `hyperopt-list` 子命令或超参数优化本身在超参数优化运行期间显示）：

```
freqtrade hyperopt-show -n 168
```

打印最后最佳时期的详细信息的 JSON 数据（即所有时期中的最佳）：

```
freqtrade hyperopt-show --best -n -1 --print-json --no-header
```

## 显示交易

将选定的（或所有）交易从数据库打印到屏幕。

--8<-- "commands/show-trades.md"

### 示例

将 id 为 2 和 3 的交易打印为 json

```bash
freqtrade show-trades --db-url sqlite:///tradesv3.sqlite --trade-ids 2 3 --print-json
```

## 策略更新器

将列出的策略或策略文件夹内的所有策略更新为 v3 兼容。
如果命令在没有 --strategy-list 的情况下运行，则策略文件夹内的所有策略都将被转换。
您的原始策略将保留在 `user_data/strategies_orig_updater/` 目录中。

!!! Warning "转换结果"
    策略更新器将采用"尽力而为"的方法。请进行尽职调查并验证转换结果。
    我们还建议运行 python 格式化程序（例如 `black`）以合理的方式格式化结果。

--8<-- "commands/strategy-updater.md"

### 示例

更新单个策略：

```bash
freqtrade strategy-updater --strategy-list AwesomeStrategy
```

更新所有策略：

```bash
freqtrade strategy-updater
```

## 前瞻性分析

检查策略中的潜在前瞻性偏差。

前瞻性偏差是指策略使用未来信息来做出当前决策的情况。这在回测中可能导致不现实的好结果，但在实盘交易中会失败。

--8<-- "commands/lookahead-analysis.md"

### 示例

```bash
freqtrade lookahead-analysis --strategy AwesomeStrategy --timerange 20210101-20210201
```

## 递归分析

检查策略中的潜在递归公式问题。

递归分析检查指标计算中的递归依赖关系，这可能导致不稳定或不正确的结果。

--8<-- "commands/recursive-analysis.md"

### 示例

```bash
freqtrade recursive-analysis --strategy AwesomeStrategy --timerange 20210101-20210201
```

## 安装 FreqUI

安装和设置 FreqUI（Freqtrade 的 Web 界面）。

```bash
freqtrade install-ui
```

这将下载并安装最新版本的 FreqUI 到您的 Freqtrade 安装中。

## 绘图命令

Freqtrade 还提供了几个绘图命令来可视化您的数据和结果：

### 绘制数据框

绘制带有指标的蜡烛图。

--8<-- "commands/plot-dataframe.md"

### 绘制利润

生成显示利润的图表。

--8<-- "commands/plot-profit.md"

更多关于绘图的详细信息，请参见[绘图文档](plotting.md)。

## 总结

这些实用工具子命令为 Freqtrade 用户提供了强大的工具集，用于：

- 管理策略和配置
- 分析回测和超参数优化结果
- 检查数据质量和策略问题
- 可视化交易结果
- 维护和更新策略

定期使用这些工具可以帮助您更好地理解和改进您的交易策略。
