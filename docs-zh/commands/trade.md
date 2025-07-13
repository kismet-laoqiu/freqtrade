```
用法: freqtrade trade [-h] [-v] [--no-color] [--logfile FILE] [-V] [-c PATH]
                       [-d PATH] [--userdir PATH] [-s NAME]
                       [--strategy-path PATH] [--recursive-strategy-search]
                       [--freqaimodel NAME] [--freqaimodel-path PATH]
                       [--db-url PATH] [--sd-notify] [--dry-run]
                       [--dry-run-wallet DRY_RUN_WALLET] [--fee FLOAT]

选项:
  -h, --help            显示此帮助信息并退出
  --db-url PATH         覆盖交易数据库 URL，这在自定义部署中很有用
                        (默认: 实盘运行模式为 `sqlite:///tradesv3.sqlite`，
                        模拟运行为 `sqlite:///tradesv3.dryrun.sqlite`)。
  --sd-notify           通知 systemd 服务管理器。
  --dry-run             强制模拟交易（移除交易所密钥并模拟交易）。
  --dry-run-wallet DRY_RUN_WALLET, --starting-balance DRY_RUN_WALLET
                        起始余额，用于回测/超参数优化和模拟运行。
  --fee FLOAT           指定费率比例。将应用两次（交易入场和出场）。

通用参数:
  -v, --verbose         详细模式（-vv 获取更多信息，-vvv 获取所有消息）。
  --no-color            禁用超参数优化结果的颜色化。如果您将输出重定向到
                        文件，这可能很有用。
  --logfile FILE, --log-file FILE
                        记录到指定的文件。特殊值有：'syslog'、'journald'。
                        有关更多详细信息，请参阅文档。
  -V, --version         显示程序版本号并退出
  -c PATH, --config PATH
                        指定配置文件（默认：`userdir/config.json` 或
                        `config.json` 中存在的任何一个）。可以使用多个
                        --config 选项。可以设置为 `-` 从 stdin 读取配置。
  -d PATH, --datadir PATH, --data-dir PATH
                        包含历史回测数据的交易所基础目录路径。要查看期货
                        数据，请额外使用 trading-mode。
  --userdir PATH, --user-data-dir PATH
                        用户数据目录路径。

策略参数:
  -s NAME, --strategy NAME
                        指定机器人将使用的策略类名。
  --strategy-path PATH  指定额外的策略查找路径。
  --recursive-strategy-search
                        递归搜索策略目录中的策略。
  --freqaimodel NAME    指定 FreqAI 模型类名。
  --freqaimodel-path PATH
                        指定额外的 FreqAI 模型查找路径。
```

## 交易命令说明

`freqtrade trade` 命令用于启动 Freqtrade 机器人进行实际交易或模拟交易。

### 基本用法

#### 启动模拟交易
```bash
freqtrade trade --strategy MyStrategy --dry-run
```

#### 启动实盘交易
```bash
freqtrade trade --strategy MyStrategy
```

!!! Warning "实盘交易风险"
    在启动实盘交易之前，请确保：
    1. 您已经充分测试了您的策略
    2. 您了解可能的风险和损失
    3. 您的配置文件正确设置了交易所 API 密钥
    4. 您已经在模拟模式下运行了足够长的时间

### 常用选项

#### 指定策略
```bash
freqtrade trade --strategy MyAwesomeStrategy
```

#### 设置起始余额（模拟交易）
```bash
freqtrade trade --strategy MyStrategy --dry-run --dry-run-wallet 1000
```

#### 使用自定义配置文件
```bash
freqtrade trade --config my_config.json --strategy MyStrategy
```

#### 指定数据目录
```bash
freqtrade trade --strategy MyStrategy --datadir user_data/data/binance
```

#### 详细日志输出
```bash
freqtrade trade --strategy MyStrategy --verbose
```

### 高级选项

#### 使用 FreqAI 模型
```bash
freqtrade trade --strategy MyStrategy --freqaimodel MyAIModel
```

#### 自定义数据库 URL
```bash
freqtrade trade --strategy MyStrategy --db-url sqlite:///my_trades.sqlite
```

#### 指定交易费用
```bash
freqtrade trade --strategy MyStrategy --fee 0.001
```

### 配置文件 vs 命令行参数

大多数设置可以在配置文件中指定，也可以通过命令行参数覆盖：

- 命令行参数优先级最高
- 环境变量次之
- 配置文件设置优先级最低

### 监控和日志

#### 查看实时日志
```bash
tail -f user_data/logs/freqtrade.log
```

#### 使用 systemd 通知
```bash
freqtrade trade --strategy MyStrategy --sd-notify
```

### 最佳实践

1. **始终先进行模拟交易**：在使用真实资金之前，先在模拟模式下运行您的策略
2. **监控日志**：定期检查日志文件以了解机器人的行为
3. **备份配置**：保持配置文件的备份
4. **逐步增加投资**：从小额开始，逐步增加投资金额
5. **定期更新**：保持 Freqtrade 和您的策略更新

### 故障排除

如果遇到问题，请检查：
1. 配置文件语法是否正确
2. 策略文件是否存在且无语法错误
3. 交易所 API 密钥是否正确配置
4. 网络连接是否正常
5. 日志文件中的错误信息
