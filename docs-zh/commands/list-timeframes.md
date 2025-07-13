```
用法: freqtrade list-timeframes [-h] [-v] [--no-color] [--logfile FILE] [-V]
                                 [-c PATH] [-d PATH] [--userdir PATH]
                                 [--exchange EXCHANGE] [-1]

选项:
  -h, --help            显示此帮助消息并退出
  --exchange EXCHANGE   交易所名称。仅在未提供配置时有效。
  -1, --one-column      以单列格式打印输出。

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
