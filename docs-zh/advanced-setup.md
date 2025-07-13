# 高级安装后任务

本页面解释了一些可以在机器人安装后执行的高级任务和配置选项，这些在某些环境中可能很有用。

如果您不知道这里提到的内容是什么意思，您可能不需要它。

## 运行多个 Freqtrade 实例

本节将向您展示如何在同一台机器上同时运行多个机器人。

### 需要考虑的事项

* 使用不同的数据库文件。
* 使用不同的 Telegram 机器人（需要多个不同的配置文件；仅在启用 Telegram 时适用）。
* 使用不同的端口（仅在启用 Freqtrade REST API 网络服务器时适用）。

### 不同的数据库文件

为了跟踪您的交易、利润等，freqtrade 使用 SQLite 数据库，其中存储各种类型的信息，例如您过去执行的交易和您在任何时候持有的当前头寸。这允许您跟踪您的利润，但最重要的是，如果机器人进程重新启动或意外终止，可以跟踪正在进行的活动。

默认情况下，Freqtrade 将为模拟运行和实盘机器人使用单独的数据库文件（这假设在配置或通过命令行参数中都没有给出数据库 URL）。
对于实盘交易模式，默认数据库将是 `tradesv3.sqlite`，对于模拟运行将是 `tradesv3.dryrun.sqlite`。

用于指定这些文件路径的交易命令的可选参数是 `--db-url`，它需要一个有效的 SQLAlchemy URL。
因此，当您在模拟运行模式下仅使用配置和策略参数启动机器人时，以下 2 个命令将具有相同的结果。

``` bash
freqtrade trade -c MyConfig.json -s MyStrategy
# 等同于
freqtrade trade -c MyConfig.json -s MyStrategy --db-url sqlite:///tradesv3.dryrun.sqlite
```

这意味着如果您在两个不同的终端中运行交易命令，例如测试您的策略在 USDT 交易和在另一个实例中的 BTC 交易，您将必须使用不同的数据库运行它们。

如果您指定一个不存在的数据库的 URL，freqtrade 将创建一个具有您指定名称的数据库。因此，要使用 BTC 和 USDT 投注货币测试您的自定义策略，您可以使用以下命令（在 2 个单独的终端中）：

``` bash
# 终端 1:
freqtrade trade -c MyConfigBTC.json -s MyCustomStrategy --db-url sqlite:///user_data/tradesBTC.dryrun.sqlite
# 终端 2:
freqtrade trade -c MyConfigUSDT.json -s MyCustomStrategy --db-url sqlite:///user_data/tradesUSDT.dryrun.sqlite
```

相反，如果您希望在生产模式下做同样的事情，您还必须创建至少一个新数据库（除了默认数据库之外）并指定"实盘"数据库的路径，例如：

``` bash
# 终端 1:
freqtrade trade -c MyConfigBTC.json -s MyCustomStrategy --db-url sqlite:///user_data/tradesBTC.live.sqlite
# 终端 2:
freqtrade trade -c MyConfigUSDT.json -s MyCustomStrategy --db-url sqlite:///user_data/tradesUSDT.live.sqlite
```

有关 sqlite 数据库使用的更多信息，例如手动输入或删除交易，请参考 [SQL 备忘单](sql_cheatsheet.md)。

### 使用 docker 的多个实例

要使用 docker 运行多个 freqtrade 实例，您需要编辑 docker-compose.yml 文件并将您想要的所有实例添加为单独的服务。请记住，您可以将配置分离到多个文件中，因此考虑使它们模块化是一个好主意，然后如果您需要编辑所有机器人共同的内容，您可以在单个配置文件中完成。

``` yml
---
version: '3'
services:
  freqtrade1:
    image: freqtradeorg/freqtrade:stable
    restart: always
    container_name: freqtrade1
    volumes:
      - "./user_data:/freqtrade/user_data"
    ports:
     - "127.0.0.1:8080:8080"
    command: >
      trade
      --logfile /freqtrade/user_data/logs/freqtrade1.log
      --db-url sqlite:////freqtrade/user_data/tradesv3_freqtrade1.sqlite
      --config /freqtrade/user_data/config.json
      --config /freqtrade/user_data/config.freqtrade1.json
      --strategy SampleStrategy
  
  freqtrade2:
    image: freqtradeorg/freqtrade:stable
    restart: always
    container_name: freqtrade2
    volumes:
      - "./user_data:/freqtrade/user_data"
    ports:
     - "127.0.0.1:8081:8080"
    command: >
      trade
      --logfile /freqtrade/user_data/logs/freqtrade2.log
      --db-url sqlite:////freqtrade/user_data/tradesv3_freqtrade2.sqlite
      --config /freqtrade/user_data/config.json
      --config /freqtrade/user_data/config.freqtrade2.json
      --strategy SampleStrategy
```

## 使用不同的数据库系统

Freqtrade 支持多种数据库系统。默认情况下使用 SQLite，但您也可以使用 PostgreSQL 或 MariaDB。

### PostgreSQL

要使用 PostgreSQL，您需要安装额外的依赖项：

```bash
pip install psycopg2-binary
```

然后在配置中设置数据库 URL：

```json
{
    "db_url": "postgresql://username:password@localhost:5432/freqtrade"
}
```

### MariaDB/MySQL

要使用 MariaDB 或 MySQL，您需要安装额外的依赖项：

```bash
pip install pymysql
```

然后在配置中设置数据库 URL：

```json
{
    "db_url": "mysql+pymysql://username:password@localhost:3306/freqtrade"
}
```

## 高级日志记录

Freqtrade 支持高级日志记录配置，允许您自定义日志输出格式、级别和目标。

### 配置日志记录

您可以在配置文件中设置日志记录：

```json
{
    "logging": {
        "version": 1,
        "disable_existing_loggers": false,
        "formatters": {
            "default": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": "INFO",
                "formatter": "default",
                "stream": "ext://sys.stdout"
            },
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "DEBUG",
                "formatter": "default",
                "filename": "logs/freqtrade.log",
                "maxBytes": 10485760,
                "backupCount": 10
            }
        },
        "loggers": {
            "freqtrade": {
                "level": "DEBUG",
                "handlers": ["console", "file"],
                "propagate": false
            }
        }
    }
}
```

### 系统日志集成

您可以将 Freqtrade 日志发送到系统日志：

```json
{
    "logging": {
        "handlers": {
            "syslog": {
                "class": "logging.handlers.SysLogHandler",
                "level": "INFO",
                "formatter": "default",
                "address": "/dev/log"
            }
        }
    }
}
```

## 性能优化

### 内存优化

对于大型数据集，您可以调整以下设置：

```json
{
    "internals": {
        "process_throttle_secs": 5,
        "heartbeat_interval": 60
    }
}
```

### CPU 优化

使用多进程进行回测和超参数优化：

```bash
freqtrade hyperopt --jobs 4
```

## 安全考虑

### API 安全

确保 API 访问的安全：

```json
{
    "api_server": {
        "enabled": true,
        "listen_ip_address": "127.0.0.1",
        "listen_port": 8080,
        "jwt_secret_key": "your-secret-key",
        "username": "your-username",
        "password": "your-strong-password"
    }
}
```

### 文件权限

设置适当的文件权限：

```bash
chmod 600 config.json
chmod 700 user_data/
```

## 监控和警报

### 系统监控

使用系统监控工具监控 Freqtrade：

```bash
# 使用 systemd 服务
sudo systemctl status freqtrade
```

### 健康检查

实现健康检查脚本：

```bash
#!/bin/bash
if ! pgrep -f "freqtrade trade" > /dev/null; then
    echo "Freqtrade is not running!"
    # 发送警报或重启服务
fi
```
