# 启动机器人

本页面解释机器人的不同参数以及如何运行它。

!!! Note
    如果您使用了 `setup.sh`，在运行 freqtrade 命令之前不要忘记激活您的虚拟环境（`source .venv/bin/activate`）。

!!! Warning "最新时钟"
    运行机器人的系统上的时钟必须准确，经常与 NTP 服务器同步，以避免与交易所通信时出现问题。

## 机器人命令

--8<-- "commands/main.md"

### 机器人交易命令

--8<-- "commands/trade.md"

### 如何指定使用哪个配置文件？

机器人允许您通过 `-c/--config` 命令行选项选择要使用的配置文件：

```bash
freqtrade trade -c path/far/far/away/config.json
```

默认情况下，机器人从当前工作目录加载 `config.json` 配置文件。

### 如何使用多个配置文件？

机器人允许您通过在命令行中指定多个 `-c/--config` 选项来使用多个配置文件。在后面的配置文件中定义的配置参数会覆盖在命令行中较早指定的前面配置文件中定义的同名参数。

例如，您可以为您用于交易的交易所制作一个包含密钥和秘钥的单独配置文件，在模拟模式下运行时指定具有空密钥和秘钥值的默认配置文件（实际上不需要它们）：

```bash
freqtrade trade -c ./config.json
```

在正常的实盘交易模式下运行时指定两个配置文件：

```bash
freqtrade trade -c ./config.json -c path/to/secrets/keys.config.json
```

这可以帮助您通过为包含实际秘密的文件设置适当的文件权限来在本地机器上隐藏您的私有交易所密钥和交易所秘钥，此外，当您在项目问题或互联网上发布配置示例时，防止意外泄露敏感的私人数据。

有关此技术的更多详细信息和示例，请参阅[配置](configuration.md)文档页面。

### 在哪里存储自定义数据

Freqtrade 允许使用 `freqtrade create-userdir --userdir someDirectory` 创建用户数据目录。
此目录将如下所示：

```
user_data/
├── backtest_results
├── data
├── hyperopts
├── hyperopt_results
├── plot
└── strategies
```

您可以在配置中添加 "user_data_dir" 设置，以始终将您的机器人指向此目录。
或者，向每个命令传递 `--userdir`。
如果目录不存在，机器人将无法启动，但会创建必要的子目录。

此目录应包含您的自定义策略、自定义超参数优化和超参数优化损失函数、回测历史数据（使用回测命令或下载脚本下载）和绘图输出。

建议使用版本控制来跟踪策略的更改。

### 如何使用 **--strategy**？

此参数将允许您加载自定义策略类。
要测试机器人安装，您可以使用由 `create-userdir` 子命令安装的 `SampleStrategy`（通常是 `user_data/strategy/sample_strategy.py`）。

机器人将在 `user_data/strategies` 中搜索您的策略文件。
要使用其他目录，请阅读下一节关于 `--strategy-path` 的内容。

要加载策略，只需在此参数中传递类名（例如：`CustomStrategy`）。

**示例：**
在 `user_data/strategies` 中您有一个文件 `my_awesome_strategy.py`，其中有一个名为 `AwesomeStrategy` 的策略类来加载它：

```bash
freqtrade trade --strategy AwesomeStrategy
```

如果机器人找不到您的策略文件，它将在错误消息中显示原因（文件未找到，或您的代码中有错误）。

在[策略自定义](strategy-customization.md)中了解更多关于策略文件的信息。

### 如何使用 **--strategy-path**？

此参数允许您添加额外的策略查找路径，该路径在默认位置之前被检查（传递的路径必须是目录！）：

```bash
freqtrade trade --strategy AwesomeStrategy --strategy-path /some/directory
```

#### 如何安装策略？

这非常简单。将您的策略文件复制粘贴到目录 `user_data/strategies` 中或使用 `--strategy-path`。瞧，机器人已准备好使用它。

### 如何使用 **--db-url**？

当您在模拟运行模式下运行机器人时，默认情况下不会在数据库中存储任何交易。如果您想使用 `--db-url` 在数据库中存储您的机器人操作。这也可以用于在生产模式下指定自定义数据库。示例命令：

```bash
freqtrade trade -c config.json --db-url sqlite:///tradesv3.dry_run.sqlite
```

## 下一步

机器人的最佳策略将根据市场趋势随时间而变化。下一步是[策略自定义](strategy-customization.md)。
