```
用法: freqtrade convert-data [-h] [-v] [--no-color] [--logfile FILE] [-V]
                              [-c PATH] [-d PATH] [--userdir PATH]
                              [-p PAIRS [PAIRS ...]] --format-from
                              {json,jsongz,feather,parquet} --format-to
                              {json,jsongz,feather,parquet} [--erase]
                              [--exchange EXCHANGE]
                              [-t TIMEFRAMES [TIMEFRAMES ...]]
                              [--trading-mode {spot,margin,futures}]
                              [--candle-types {spot,futures,mark,index,premiumIndex,funding_rate} [{spot,futures,mark,index,premiumIndex,funding_rate} ...]]

选项:
  -h, --help            显示此帮助消息并退出
  -p PAIRS [PAIRS ...], --pairs PAIRS [PAIRS ...]
                        将命令限制为这些交易对。交易对用空格分隔。
  --format-from {json,jsongz,feather,parquet}
                        数据转换的源格式。
  --format-to {json,jsongz,feather,parquet}
                        数据转换的目标格式。
  --erase               清除所选交易所/交易对/时间框架的所有现有数据。
  --exchange EXCHANGE   交易所名称。仅在未提供配置时有效。
  -t TIMEFRAMES [TIMEFRAMES ...], --timeframes TIMEFRAMES [TIMEFRAMES ...]
                        指定要下载的时间框架。空格分隔的列表。
                        默认: `1m 5m`。
  --trading-mode {spot,margin,futures}, --tradingmode {spot,margin,futures}
                        选择交易模式
  --candle-types {spot,futures,mark,index,premiumIndex,funding_rate} [{spot,futures,mark,index,premiumIndex,funding_rate} ...]
                        选择要转换的蜡烛图类型。默认为所有可用类型。

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
