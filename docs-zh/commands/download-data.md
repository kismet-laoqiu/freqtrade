```
用法: freqtrade download-data [-h] [-v] [--no-color] [--logfile FILE] [-V]
                               [-c PATH] [-d PATH] [--userdir PATH]
                               [-p PAIRS [PAIRS ...]] [--pairs-file FILE]
                               [--days INT] [--new-pairs-days INT]
                               [--include-inactive-pairs]
                               [--timerange TIMERANGE] [--dl-trades]
                               [--convert] [--exchange EXCHANGE]
                               [-t TIMEFRAMES [TIMEFRAMES ...]] [--erase]
                               [--data-format-ohlcv {json,jsongz,feather,parquet}]
                               [--data-format-trades {json,jsongz,feather,parquet}]
                               [--trading-mode {spot,margin,futures}]
                               [--prepend]

选项:
  -h, --help            显示此帮助信息并退出
  -p PAIRS [PAIRS ...], --pairs PAIRS [PAIRS ...]
                        将命令限制为这些交易对。交易对用空格分隔。
  --pairs-file FILE     包含交易对列表的文件。优先于 --pairs 或配置中
                        配置的交易对。
  --days INT            下载指定天数的数据。
  --new-pairs-days INT  为新交易对下载指定天数的数据。
                        默认: `None`。
  --include-inactive-pairs
                        同时下载非活跃交易对的数据。
  --timerange TIMERANGE
                        指定要使用的数据时间范围。
  --dl-trades           下载交易数据而不是 OHLCV 数据。
  --convert             将下载的交易数据转换为 OHLCV 数据。仅适用于
                        与 `--dl-trades` 结合使用。对于没有历史 OHLCV
                        的交易所（如 Kraken）将自动执行。如果未提供，
                        使用 `trades-to-ohlcv` 将交易数据转换为 OHLCV 数据。
  --exchange EXCHANGE   交易所名称。仅在未提供配置时有效。
  -t TIMEFRAMES [TIMEFRAMES ...], --timeframes TIMEFRAMES [TIMEFRAMES ...]
                        指定要下载的时间框架。空格分隔的列表。
                        默认: `1m 5m`。
  --erase               清除所选交易所/交易对/时间框架的所有现有数据。
  --data-format-ohlcv {json,jsongz,feather,parquet}
                        下载的蜡烛图 (OHLCV) 数据的存储格式。
                        (默认: `feather`)。
  --data-format-trades {json,jsongz,feather,parquet}
                        下载的交易数据的存储格式。(默认: `feather`)。
  --trading-mode {spot,margin,futures}, --tradingmode {spot,margin,futures}
                        选择交易模式
  --prepend             允许数据前置。(数据追加被禁用)
```

## 数据下载命令说明

`freqtrade download-data` 命令用于下载历史市场数据，包括 OHLCV 蜡烛图数据和交易数据。

### 基本用法

```bash
# 下载默认交易对的数据
freqtrade download-data --exchange binance

# 下载指定交易对的数据
freqtrade download-data --exchange binance --pairs BTC/USDT ETH/USDT

# 下载指定天数的数据
freqtrade download-data --exchange binance --days 30

# 下载指定时间框架的数据
freqtrade download-data --exchange binance --timeframes 1m 5m 1h
```

### 高级选项

```bash
# 下载期货数据
freqtrade download-data --exchange binance --trading-mode futures --pairs BTC/USDT:USDT

# 下载交易数据
freqtrade download-data --exchange binance --dl-trades --pairs BTC/USDT

# 指定数据格式
freqtrade download-data --exchange binance --data-format-ohlcv parquet

# 清除现有数据并重新下载
freqtrade download-data --exchange binance --erase --pairs BTC/USDT
```
