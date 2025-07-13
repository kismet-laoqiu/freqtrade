# 已弃用功能

本页面包含机器人开发团队声明为已弃用且不再支持的命令行参数、配置参数和机器人功能的描述。请避免在您的配置中使用它们。

## 已移除功能

### `--refresh-pairs-cached` 命令行选项

在回测、超参数优化和边缘定位的上下文中，`--refresh-pairs-cached` 允许刷新用于回测的蜡烛图数据。
由于这会导致很多混乱，并且会减慢回测速度（虽然不是回测的一部分），这已被单独作为一个独立的 freqtrade 子命令 `freqtrade download-data`。

此命令行选项在 2019.7-dev（开发分支）中被弃用，并在 2019.9 中被移除。

### `--dynamic-whitelist` 命令行选项

此命令行选项在 2018 年被弃用，并在 freqtrade 2019.6-dev（开发分支）和 freqtrade 2019.7 中被移除。
请参考[交易对列表](plugins.md#交易对列表和交易对列表处理器)代替。

### `--live` 命令行选项

在回测上下文中，`--live` 允许下载最新的行情数据进行回测。
只下载最新的 500 根蜡烛图，因此在获取良好的回测数据方面效果不佳。
在 2019-7-dev（开发分支）和 freqtrade 2019.8 中被移除。

### `ticker_interval`（现在是 `timeframe`）

对 `ticker_interval` 术语的支持在 2020.6 中被弃用，改为使用 `timeframe` - 兼容性代码在 2022.3 中被移除。

### 允许按顺序运行多个交易对列表

配置中以前的 `"pairlist"` 部分已被移除，并被 `"pairlists"` 替换 - 作为一个列表来指定交易对列表的序列。

旧的配置参数部分（`"pairlist"`）在 2019.11 中被弃用，并在 2020.4 中被移除。

### 从成交量交易对列表中弃用 bidVolume 和 askVolume

由于只有 quoteVolume 可以在资产之间进行比较，其他选项（bidVolume、askVolume）在 2020.4 中被弃用，并在 2020.9 中被移除。

### 使用订单簿步骤进行出场价格

使用 `order_book_min` 和 `order_book_max` 曾经允许步进订单簿并尝试找到下一个 ROI 槽位 - 尝试提前下达卖出订单。
然而，由于这会增加风险且不提供任何好处，为了可维护性目的，在 2021.7 中被移除。

### 传统超参数优化模式

使用单独的超参数优化文件在 2021.4 中被弃用，并在 2021.9 中被移除。
请切换到新的[参数化策略](hyperopt.md)以从新的超参数优化界面中受益。

## V2 和 V3 之间的策略变更

隔离期货/空头交易在 2022.4 中引入。这需要对配置设置、策略接口等进行重大更改。

我们已经努力保持与现有策略的兼容性，因此如果您只想继续在现货市场中使用 freqtrade，则无需进行任何更改。
虽然我们可能会在将来的某个时候放弃对当前接口的支持，但我们将单独宣布这一点并有适当的过渡期。

请遵循[策略迁移](strategy_migration.md)指南将您的策略迁移到新格式以开始使用新功能。

### webhooks - 2022.4 的变更

#### `buy_tag` 已重命名为 `enter_tag`

这应该只适用于您的策略和可能的 webhooks。
我们将保持 1-2 个版本的兼容性层（因此 `buy_tag` 和 `enter_tag` 仍然可以工作），但在 webhooks 中对此的支持将在那之后消失。

#### 命名变更

Webhook 术语从"sell"更改为"exit"，从"buy"更改为"entry"，在此过程中移除了"webhook"。

* `webhookbuy`, `webhookentry` -> `entry`
* `webhookbuyfill`, `webhookentryfill` -> `entry_fill`
* `webhookbuycancel`, `webhookentrycancel` -> `entry_cancel`
* `webhooksell`, `webhookexit` -> `exit`
* `webhooksellfill`, `webhookexitfill` -> `exit_fill`
* `webhooksellcancel`, `webhookexitcancel` -> `exit_cancel`

## 移除 `populate_any_indicators`

版本 2023.3 看到了 `populate_any_indicators` 的移除，改为使用用于特征工程和目标的分割方法。请阅读[迁移文档](strategy_migration.md#freqai-策略)了解完整详情。

## 从配置中移除 `protections`

通过 `"protections": [],` 从配置设置保护机制在 2024.10 中被移除，在发出弃用警告超过 3 年后。

## hdf5 数据存储

使用 hdf5 作为数据存储在 2024.12 中被弃用，并在 2025.1 中被移除。我们建议切换到 feather 数据格式。

请在更新之前使用[`convert-data` 子命令](data-download.md#子命令-convert-data)将您的现有数据转换为支持的格式之一。

## 通过配置配置高级日志记录

分别通过 `--logfile systemd` 和 `--logfile journald` 配置 syslog 和 journald 在 2025.3 中被弃用。
请使用基于配置的[日志设置](advanced-setup.md#高级日志记录)代替。

## 移除边缘模块

边缘模块在 2023.9 中被弃用，并在 2025.6 中被移除。
边缘的所有功能都已被移除，配置边缘将导致错误。
