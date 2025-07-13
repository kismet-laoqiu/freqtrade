# Freqtrade 中文文档

欢迎使用 Freqtrade 中文文档！这是 Freqtrade 官方英文文档的完整中文翻译版本。

## 文档结构

### 🚀 快速开始
- [主页](index.md) - Freqtrade 介绍和概述
- [Docker 快速入门](docker_quickstart.md) - 使用 Docker 快速开始（推荐）
- [安装指南](installation.md) - 详细的安装说明
- [Windows 安装](windows_installation.md) - Windows 系统安装指南

### ⚙️ 配置
- [机器人配置](configuration.md) - 完整的配置参数说明
- [机器人基础](bot-basics.md) - 机器人基本概念
- [机器人使用](bot-usage.md) - 机器人使用指南

### 📈 策略开发
- [策略入门 101](strategy-101.md) - 策略开发快速入门
- [策略自定义](strategy-customization.md) - 高级策略自定义
- [策略高级功能](strategy-advanced.md) - 高级策略功能
- [策略回调](strategy-callbacks.md) - 策略回调函数
- [策略迁移](strategy_migration.md) - 策略版本迁移

### 🔍 回测和分析
- [回测](backtesting.md) - 策略回测指南
- [高级回测](advanced-backtesting.md) - 高级回测功能
- [数据分析](data-analysis.md) - 交易数据分析
- [数据下载](data-download.md) - 历史数据下载
- [绘图](plotting.md) - 数据可视化

### 🤖 机器学习 (FreqAI)
- [FreqAI 介绍](freqai.md) - 机器学习功能概述
- [FreqAI 配置](freqai-configuration.md) - FreqAI 配置说明
- [FreqAI 运行](freqai-running.md) - 运行 FreqAI
- [FreqAI 特征工程](freqai-feature-engineering.md) - 特征工程
- [FreqAI 强化学习](freqai-reinforcement-learning.md) - 强化学习
- [FreqAI 参数表](freqai-parameter-table.md) - 参数参考
- [FreqAI 开发者](freqai-developers.md) - 开发者指南

### 🔧 优化
- [超参数优化](hyperopt.md) - 策略参数优化
- [高级超参数优化](advanced-hyperopt.md) - 高级优化技术
- [前瞻性分析](lookahead-analysis.md) - 前瞻性偏差分析
- [递归分析](recursive-analysis.md) - 递归分析

### 💱 交易所和交易
- [支持的交易所](exchanges.md) - 交易所配置和说明
- [杠杆交易](leverage.md) - 期货和杠杆交易
- [止损](stoploss.md) - 止损策略
- [高级订单流](advanced-orderflow.md) - 高级订单管理

### 🖥️ 用户界面和 API
- [FreqUI](freq-ui.md) - Web 用户界面
- [REST API](rest-api.md) - API 接口文档
- [Telegram 使用](telegram-usage.md) - Telegram 机器人
- [Webhook 配置](webhook-config.md) - Webhook 配置

### 🛠️ 工具和实用程序
- [命令行工具](commands/main.md) - 所有命令行工具
- [实用程序](utils.md) - 实用工具和脚本
- [插件](plugins.md) - 插件系统
- [SQL 备忘单](sql_cheatsheet.md) - 数据库查询

### 🔧 高级主题
- [高级设置](advanced-setup.md) - 高级配置和设置
- [开发者指南](developer.md) - 开发者文档
- [生产者-消费者](producer-consumer.md) - 分布式交易
- [更新](updating.md) - 版本更新指南

### 📋 参考
- [常见问题](faq.md) - 常见问题解答
- [已弃用功能](deprecated.md) - 已弃用的功能
- [交易对象](trade-object.md) - 交易对象参考

## 命令行工具

### 核心命令
- [交易](commands/trade.md) - 启动实盘或模拟交易
- [回测](commands/backtesting.md) - 运行策略回测
- [超参数优化](commands/hyperopt.md) - 参数优化
- [数据下载](commands/download-data.md) - 下载历史数据

### 配置和设置
- [新建配置](commands/new-config.md) - 创建新配置文件
- [新建策略](commands/new-strategy.md) - 创建新策略
- [创建用户目录](commands/create-userdir.md) - 创建用户目录
- [显示配置](commands/show-config.md) - 显示当前配置

### 数据管理
- [转换数据](commands/convert-data.md) - 数据格式转换
- [转换数据库](commands/convert-db.md) - 数据库转换
- [转换交易数据](commands/convert-trade-data.md) - 交易数据转换
- [列出数据](commands/list-data.md) - 列出可用数据

### 分析工具
- [回测分析](commands/backtesting-analysis.md) - 回测结果分析
- [回测显示](commands/backtesting-show.md) - 显示回测结果
- [绘制数据框](commands/plot-dataframe.md) - 绘制价格图表
- [绘制利润](commands/plot-profit.md) - 绘制利润图表
- [显示交易](commands/show-trades.md) - 显示交易历史

### 列表命令
- [列出交易所](commands/list-exchanges.md) - 列出支持的交易所
- [列出市场](commands/list-markets.md) - 列出交易市场
- [列出交易对](commands/list-pairs.md) - 列出交易对
- [列出策略](commands/list-strategies.md) - 列出可用策略
- [列出时间框架](commands/list-timeframes.md) - 列出时间框架
- [列出 FreqAI 模型](commands/list-freqaimodels.md) - 列出 AI 模型
- [列出超参数损失](commands/list-hyperoptloss.md) - 列出损失函数

### 其他工具
- [Web 服务器](commands/webserver.md) - 启动 Web 界面
- [安装 UI](commands/install-ui.md) - 安装用户界面
- [策略更新器](commands/strategy-updater.md) - 更新策略
- [测试交易对列表](commands/test-pairlist.md) - 测试交易对列表
- [边缘](commands/edge.md) - 边缘定位
- [超参数列表](commands/hyperopt-list.md) - 列出优化结果
- [超参数显示](commands/hyperopt-show.md) - 显示优化结果

## 使用说明

1. **新手用户**：建议从[主页](index.md)开始，然后按照[Docker 快速入门](docker_quickstart.md)进行安装
2. **策略开发**：阅读[策略入门 101](strategy-101.md)了解基础概念
3. **高级用户**：查看[高级设置](advanced-setup.md)和[开发者指南](developer.md)

## 贡献

如果您发现翻译错误或有改进建议，欢迎提交 Issue 或 Pull Request。

## 版权声明

本中文文档基于 Freqtrade 官方英文文档翻译，遵循原项目的开源协议。
