# 数据下载

## 获取回测和超参数优化的数据

要下载回测和超参数优化所需的数据（蜡烛图 / OHLCV），请使用 `freqtrade download-data` 命令。

如果未指定其他参数，freqtrade 将下载过去 30 天的 `"1m"` 和 `"5m"` 时间框架数据。
交易所和交易对将来自 `config.json`（如果使用 `-c/--config` 指定）。
如果没有提供配置，`--exchange` 变为必需。

您可以使用相对时间范围（`--days 20`）或绝对起始点（`--timerange 20200101-`）。对于增量下载，应使用相对方法。

!!! Tip "提示：更新现有数据"
    如果您的数据目录中已有回测数据并希望将此数据刷新到今天，freqtrade 将自动计算现有交易对的缺失时间范围，下载将从最新可用点到"现在"进行，不需要 `--days` 或 `--timerange` 参数。Freqtrade 将保留可用数据并仅下载缺失数据。
    如果您在插入没有数据的新交易对后更新现有数据，请使用 `--new-pairs-days xx` 参数。将为新交易对下载指定天数的数据，而旧交易对将仅更新缺失数据。

### 用法

--8<-- "commands/download-data.md"

!!! Tip "下载一种报价货币的所有数据"
    通常，您会想要下载特定报价货币的所有交易对的数据。在这种情况下，您可以使用以下简写：
    `freqtrade download-data --exchange binance --pairs ".*/USDT" <...>`。提供的"pairs"字符串将扩展为包含交易所上的所有活跃交易对。
    要同时下载非活跃（已退市）交易对的数据，请在命令中添加 `--include-inactive-pairs`。

!!! Note "启动期"
    `download-data` 是一个独立于策略的命令。其想法是一次下载大量数据，然后迭代增加存储的数据量。

    因此，`download-data` 不关心策略中定义的"启动期"。如果回测应该从特定时间点开始（同时尊重启动期），用户需要下载额外的天数。

### 开始下载

一个非常简单的命令（假设有可用的 `config.json` 文件）可能如下所示。

```bash
freqtrade download-data --exchange binance
```

这将为配置中定义的所有货币对下载历史蜡烛图（OHLCV）数据。

或者，直接指定交易对

```bash
freqtrade download-data --exchange binance --pairs ETH/USDT XRP/USDT BTC/USDT
```

或作为正则表达式（在这种情况下，下载所有活跃的 USDT 交易对）

```bash
freqtrade download-data --exchange binance --pairs ".*/USDT"
```

### 其他说明

* 要使用与交易所特定默认值不同的目录，请使用 `--datadir user_data/data/some_directory`。
* 要更改用于下载历史数据的交易所，请使用 `--exchange <exchange>` - 或指定不同的配置文件。
* 要使用其他目录中的 `pairs.json`，请使用 `--pairs-file some_other_dir/pairs.json`。
* 要仅下载 10 天的历史蜡烛图（OHLCV）数据，请使用 `--days 10`（默认为 30 天）。
* 要从固定起始点下载历史蜡烛图（OHLCV）数据，请使用 `--timerange 20200101-` - 这将下载从 2020 年 1 月 1 日开始的所有数据。
* 如果数据已经可用，给定的起始点将被忽略，仅下载到今天的缺失数据。
* 使用 `--timeframes` 指定下载历史蜡烛图（OHLCV）数据的时间框架。默认是 `--timeframes 1m 5m`，将下载 1 分钟和 5 分钟数据。
* 要使用配置文件中定义的交易所、时间框架和交易对列表，请使用 `-c/--config` 选项。使用此选项，脚本使用配置中定义的白名单作为要下载数据的货币对列表，不需要 pairs.json 文件。您可以将 `-c/--config` 与大多数其他选项结合使用。

??? Note "权限被拒绝错误"
    如果您的配置目录 `user_data` 是由 docker 创建的，您可能会遇到以下错误：

    ```
    cp: cannot create regular file 'user_data/data/binance/pairs.json': Permission denied
    ```

    您可以按如下方式修复用户数据目录的权限：

    ```
    sudo chown -R $UID:$GID user_data
    ```

### 在当前时间范围之前下载额外数据

假设您从 2022 年下载了所有数据（`--timerange 20220101-`）- 但您现在也想用更早的数据进行回测。
您可以通过使用 `--prepend` 标志结合 `--timerange` - 指定结束日期来做到这一点。

``` bash
freqtrade download-data --exchange binance --pairs ETH/USDT XRP/USDT BTC/USDT --prepend --timerange 20210101-20220101
```

!!! Note
    如果数据可用，Freqtrade 将在此模式下忽略结束日期，将结束日期更新为现有数据起始点。

### 数据格式

Freqtrade 目前支持以下数据格式：

* `feather` - 基于 Apache Arrow 的数据格式
* `json` - 纯"文本"json 文件
* `jsongz` - json 文件的 gzip 压缩版本
* `parquet` - 列式数据存储（仅 OHLCV）

默认情况下，OHLCV 数据和交易数据都以 `feather` 格式存储。

这可以分别通过 `--data-format-ohlcv` 和 `--data-format-trades` 命令行参数更改。
