```
用法: freqtrade list-pairs [-h] [-v] [--no-color] [--logfile FILE] [-V]
                            [-c PATH] [-d PATH] [--userdir PATH]
                            [--exchange EXCHANGE] [--print-list]
                            [--print-json] [-1] [--print-csv]
                            [--base BASE_CURRENCY [BASE_CURRENCY ...]]
                            [--quote QUOTE_CURRENCY [QUOTE_CURRENCY ...]] [-a]
                            [--trading-mode {spot,margin,futures}]

选项:
  -h, --help            显示此帮助消息并退出
  --exchange EXCHANGE   交易所名称。仅在未提供配置时有效。
  --print-list          打印交易对或市场符号列表。默认情况下，数据
                        以表格格式打印。
  --print-json          以 JSON 格式打印交易对或市场符号列表。
  -1, --one-column      以单列格式打印输出。
  --print-csv           以 CSV 格式打印交易所交易对或市场数据。
  --base BASE_CURRENCY [BASE_CURRENCY ...]
                        指定基础货币。空格分隔的列表。
  --quote QUOTE_CURRENCY [QUOTE_CURRENCY ...]
                        指定报价货币。空格分隔的列表。
  -a, --all             打印所有交易对或市场符号。默认情况下只显示
                        活跃的交易对。
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
