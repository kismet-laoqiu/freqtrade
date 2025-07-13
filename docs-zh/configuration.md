# 配置机器人

Freqtrade 有许多可配置的功能和可能性。
默认情况下，这些设置通过配置文件进行配置（见下文）。

## Freqtrade 配置文件

机器人在运行期间使用一组配置参数，这些参数共同构成机器人配置。它通常从文件（Freqtrade 配置文件）中读取其配置。

默认情况下，机器人从位于当前工作目录中的 `config.json` 文件加载配置。

您可以使用 `-c/--config` 命令行选项指定机器人使用的不同配置文件。

如果您使用了[快速入门](docker_quickstart.md#docker-快速入门)方法安装机器人，安装脚本应该已经为您创建了默认配置文件（`config.json`）。

如果没有创建默认配置文件，我们建议使用 `freqtrade new-config --config user_data/config.json` 生成基本配置文件。

Freqtrade 配置文件应以 JSON 格式编写。

除了标准 JSON 语法外，您还可以在配置文件中使用单行 `// ...` 和多行 `/* ... */` 注释，以及参数列表中的尾随逗号。

如果您不熟悉 JSON 格式，请不要担心 -- 只需使用您选择的编辑器打开配置文件，对您需要的参数进行一些更改，保存更改，最后重新启动机器人，或者如果之前已停止，则使用您对配置所做的更改再次运行它。机器人在启动时验证配置文件的语法，如果您在编辑时出现任何错误，会警告您并指出有问题的行。

### 环境变量

通过环境变量在 Freqtrade 配置中设置选项。
这优先于配置或策略中的相应值。

环境变量必须以 `FREQTRADE__` 为前缀才能加载到 freqtrade 配置中。

`__` 用作级别分隔符，因此使用的格式应对应于 `FREQTRADE__{section}__{key}`。
因此 - 定义为 `export FREQTRADE__STAKE_AMOUNT=200` 的环境变量将导致 `{stake_amount: 200}`。

一个更复杂的例子可能是 `export FREQTRADE__EXCHANGE__KEY=<yourExchangeKey>` 来保持您的交易所密钥秘密。这将把值移动到配置的 `exchange.key` 部分。
使用此方案，所有配置设置也将作为环境变量可用。

请注意，环境变量将覆盖配置中的相应设置，但命令行参数始终获胜。

常见示例：

``` bash
FREQTRADE__TELEGRAM__CHAT_ID=<telegramchatid>
FREQTRADE__TELEGRAM__TOKEN=<telegramToken>
FREQTRADE__EXCHANGE__KEY=<yourExchangeKey>
FREQTRADE__EXCHANGE__SECRET=<yourExchangeSecret>
```

Json 列表被解析为 json - 因此您可以使用以下方式设置交易对列表：

``` bash
export FREQTRADE__EXCHANGE__PAIR_WHITELIST='["BTC/USDT", "ETH/USDT"]'
```

!!! Note
    检测到的环境变量在启动时记录 - 因此如果您找不到为什么某个值不是您基于配置认为应该的值，请确保它不是从环境变量加载的。

!!! Tip "验证组合结果"
    您可以使用 [show-config 子命令](utils.md#show-config) 查看最终的组合配置。

??? Warning "加载顺序"
    环境变量在初始配置之后加载。因此，您不能通过环境变量提供配置的路径。请为此使用 `--config path/to/config.json`。
    这在某种程度上也适用于 `user_dir`。虽然用户目录可以通过环境变量设置 - 配置将**不会**从该位置加载。

### 多个配置文件

机器人可以指定和使用多个配置文件，或者机器人可以从进程标准输入流读取其配置参数。

您可以在 `add_config_files` 中指定其他配置文件。此参数中指定的文件将被加载并与初始配置文件合并。文件相对于初始配置文件解析。
这类似于使用多个 `--config` 参数，但在使用上更简单，因为您不必为所有命令指定所有文件。

!!! Tip "验证组合结果"
    您可以使用 [show-config 子命令](utils.md#show-config) 查看最终的组合配置。

!!! Tip "使用多个配置文件保持秘密"
    您可以使用包含您的秘密的第二个配置文件。这样您可以共享您的"主要"配置文件，同时仍然为自己保留 API 密钥。
    第二个文件应该只指定您打算覆盖的内容。
    如果一个密钥在多个配置中，那么"最后指定的配置"获胜（在上面的例子中，`config-private.json`）。

    对于一次性命令，您也可以通过指定多个"--config"参数使用以下语法。

    ``` bash
    freqtrade trade --config user_data/config1.json --config user_data/config-private.json <...>
    ```

    下面等同于上面的例子 - 但在配置中有 2 个配置文件，以便更容易重用。

    ``` json title="user_data/config.json"
    "add_config_files": [
        "config1.json",
        "config-private.json"
    ]
    ```

    ``` bash
    freqtrade trade --config user_data/config.json <...>
    ```

??? Note "配置冲突处理"
    如果相同的配置设置在 `config.json` 和 `config-import.json` 中都存在，那么父配置获胜。
    在下面的情况下，合并后 `max_open_trades` 将是 3 - 因为可重用的"导入"配置的这个键被覆盖了。

    ``` json title="user_data/config.json"
    {
        "max_open_trades": 3,
        "stake_currency": "USDT",
        "add_config_files": [
            "config-import.json"
        ]
    }
    ```

    ``` json title="user_data/config-import.json"
    {
        "max_open_trades": 10,
        "stake_amount": "unlimited",
    }
    ```

    结果组合配置：

    ``` json title="Result"
    {
        "max_open_trades": 3,
        "stake_currency": "USDT",
        "stake_amount": "unlimited"
    }
    ```

    如果 `add_config_files` 部分中有多个文件，那么它们将被假定为相同级别，最后出现的覆盖较早的配置（除非父级已经定义了这样的键）。

## 编辑器自动完成和验证

如果您使用支持 JSON 模式的编辑器，您可以使用 Freqtrade 提供的模式通过在配置文件顶部添加以下行来获得配置文件的自动完成和验证：

``` json
{
    "$schema": "https://schema.freqtrade.io/schema.json",
}
```

??? Note "开发版本"
    开发模式可用作 `https://schema.freqtrade.io/schema_dev.json` - 但我们建议坚持使用稳定版本以获得最佳体验。

## 配置参数

下表将列出所有可用的配置参数。

Freqtrade 还可以通过命令行 (CLI) 参数加载许多选项（查看命令的 `--help` 输出以获取详细信息）。
