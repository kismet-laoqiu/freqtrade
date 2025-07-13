```
用法: freqtrade trades-to-ohlcv [-h] [-v] [--no-color] [--logfile FILE] [-V]
                                 [-c PATH] [-d PATH] [--userdir PATH]
                                 [-p PAIRS [PAIRS ...]]
                                 [-t TIMEFRAMES [TIMEFRAMES ...]]
                                 [--exchange EXCHANGE]
                                 [--data-format-ohlcv {json,jsongz,feather,parquet}]
                                 [--data-format-trades {json,jsongz,feather,parquet}]
                                 [--trading-mode {spot,margin,futures}]

选项:
  -h, --help            显示此帮助消息并退出
  -p PAIRS [PAIRS ...], --pairs PAIRS [PAIRS ...]
                        将命令限制为这些交易对。交易对用空格分隔。
  -t TIMEFRAMES [TIMEFRAMES ...], --timeframes TIMEFRAMES [TIMEFRAMES ...]
                        指定要下载的时间框架。空格分隔的列表。
                        默认: `1m 5m`。
  --exchange EXCHANGE   交易所名称。仅在未提供配置时有效。
  --data-format-ohlcv {json,jsongz,feather,parquet}
                        下载的蜡烛图 (OHLCV) 数据的存储格式。
                        (默认: `feather`)。
  --data-format-trades {json,jsongz,feather,parquet}
                        下载的交易数据的存储格式。(默认: `feather`)。
  --trading-mode {spot,margin,futures}, --tradingmode {spot,margin,futures}
                        选择交易模式

通用参数:
  -v, --verbose         详细模式 (-vv 更详细，-vvv 获取所有消息)。
  --no-color            禁用超参数优化结果的颜色化。如果您将输出
                        重定向到文件，这可能很有用。
  --logfile FILE, --log-file FILE
                        记录到指定的文件。特殊值有：'syslog'、'journald'。
                        有关更多详细信息，请参阅文档。
  -V, --version         显示程序的版本号并退出
  -c PATH, --config PATH
                        指定配置文件 (默认: `userdir/config.json` 或
                        `config.json` 中存在的任何一个)。可以使用多个
                        --config 选项。可以设置为 `-` 从 stdin 读取配置。
  -d PATH, --datadir PATH, --data-dir PATH
                        包含历史回测数据的交易所基础目录的路径。
                        要查看期货数据，请额外使用 trading-mode。
  --userdir PATH, --user-data-dir PATH
                        用户数据目录的路径。

```
