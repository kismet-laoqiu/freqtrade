![freqai-logo](assets/freqai_doc_logo.svg)

# FreqAI

## 介绍

FreqAI 是一个软件，旨在自动化与训练预测性机器学习模型相关的各种任务，以根据一组输入信号生成市场预测。总的来说，FreqAI 旨在成为一个沙盒，用于在实时数据上轻松部署强大的机器学习库（[详情](#freqai-在开源机器学习领域的地位)）。

!!! Note
    FreqAI 是，并且永远是一个非营利的开源项目。FreqAI *没有*加密货币代币，FreqAI *不*出售信号，FreqAI 除了当前的 [freqtrade 文档](https://www.freqtrade.io/en/latest/freqai/) 之外没有其他域名。

功能包括：

* **自适应重新训练** - 在[实盘部署](freqai-running.md#实盘部署)期间重新训练模型，以监督方式自适应市场
* **快速特征工程** - 基于用户创建的简单策略创建大型丰富的[特征集](freqai-feature-engineering.md#特征工程)（10k+ 特征）
* **高性能** - 线程允许在与模型推理（预测）和机器人交易操作分离的线程（或 GPU 如果可用）上进行自适应模型重新训练。最新的模型和数据保存在 RAM 中以进行快速推理
* **现实的回测** - 使用[回测模块](freqai-running.md#回测)在历史数据上模拟自适应训练，该模块自动化重新训练
* **可扩展性** - 通用且强大的架构允许整合 Python 中可用的任何[机器学习库/方法](freqai-configuration.md#使用不同的预测模型)。目前提供八个示例，包括分类器、回归器和卷积神经网络
* **智能异常值移除** - 使用各种[异常值检测技术](freqai-feature-engineering.md#异常值检测)从训练和预测数据集中移除异常值
* **崩溃恢复能力** - 将训练好的模型存储到磁盘，使从崩溃中重新加载变得快速简单，并[清除过时文件](freqai-running.md#清除旧模型数据)以维持模拟/实盘运行
* **自动数据标准化** - 以智能且统计安全的方式[标准化数据](freqai-feature-engineering.md#构建数据管道)
* **自动数据下载** - 计算数据下载的时间范围并更新历史数据（在实盘部署中）
* **清理传入数据** - 在训练和模型推理之前安全处理 NaN
* **降维** - 通过[主成分分析](freqai-feature-engineering.md#使用主成分分析进行数据降维)减少训练数据的大小
* **部署机器人集群** - 设置一个机器人训练模型，而一群[消费者](producer-consumer.md)使用信号。

## 快速开始

快速测试 FreqAI 的最简单方法是使用以下命令在模拟模式下运行：

```bash
freqtrade trade --config config_examples/config_freqai.example.json --strategy FreqaiExampleStrategy --freqaimodel LightGBMRegressor --strategy-path freqtrade/templates
```

您将看到自动数据下载的启动过程，然后是同时进行的训练和交易。

!!! danger "不适用于生产环境"
    Freqtrade 源代码提供的示例策略是为了展示/测试各种 FreqAI 功能而设计的。它也被设计为在小型计算机上运行，以便可以用作开发者和用户之间的基准。它*不是*为在生产环境中运行而设计的。

可以在 `freqtrade/templates/FreqaiExampleStrategy.py`、`freqtrade/freqai/prediction_models/LightGBMRegressor.py` 和 `config_examples/config_freqai.example.json` 中分别找到用作起点的示例策略、预测模型和配置。

## 一般方法

您为 FreqAI 提供一组自定义*基础指标*（与[典型的 Freqtrade 策略](strategy-customization.md)相同的方式）以及目标值（*标签*）。对于白名单中的每个交易对，FreqAI 训练一个模型来基于自定义指标的输入预测目标值。然后以预定频率一致地重新训练模型，以适应市场条件。FreqAI 提供回测策略（通过在历史数据上定期重新训练来模拟现实）和部署模拟/实盘运行的能力。在模拟/实盘条件下，FreqAI 可以设置为在后台线程中持续重新训练，以保持模型尽可能最新。

下面显示了算法概述，解释了数据处理管道和模型使用。

![freqai-algo](assets/freqai_algo.jpg)

### 重要的机器学习词汇

**特征** - 基于历史数据的参数，模型在这些参数上进行训练。单个蜡烛图的所有特征都存储为一个向量。在 FreqAI 中，您可以从策略中构建的任何内容构建特征数据集。

**标签** - 模型训练的目标值。每个特征向量都与您在策略中定义的单个标签相关联。这些标签有意地展望未来，是您训练模型能够预测的内容。

**训练** - "教授"模型将特征集与相关标签匹配的过程。不同类型的模型以不同的方式"学习"，这意味着一种模型可能比另一种更适合特定应用。有关 FreqAI 中已实现的不同模型的更多信息可以在[这里](freqai-configuration.md#使用不同的预测模型)找到。

**训练数据** - 在训练期间提供给模型的特征数据集的子集，用于"教授"模型如何预测目标。这些数据直接影响模型中的权重连接。

**测试数据** - 用于在训练后评估模型性能的特征数据集的子集。这些数据不影响模型内的节点权重。

**推理** - 向训练好的模型提供新的未见过的数据并让其进行预测的过程。

## 安装先决条件

正常的 Freqtrade 安装过程会询问您是否希望安装 FreqAI 依赖项。如果您希望使用 FreqAI，应该对此问题回答"是"。如果您没有回答是，可以在安装后手动安装这些依赖项：

```bash
pip install -r requirements-freqai.txt
```

!!! Note
    Catboost 不会安装在低功耗 ARM 设备（树莓派）上，因为它不为此平台提供轮子。

### 使用 Docker

如果您使用 docker，可以使用带有 FreqAI 依赖项的专用标签 `:freqai`。因此，您可以将 docker compose 文件中的镜像行替换为 `image: freqtradeorg/freqtrade:stable_freqai`。此镜像包含常规的 FreqAI 依赖项。与本地安装类似，Catboost 在基于 ARM 的设备上不可用。如果您想使用 PyTorch 或强化学习，应该使用 torch 或 RL 标签，`image: freqtradeorg/freqtrade:stable_freqaitorch`，`image: freqtradeorg/freqtrade:stable_freqairl`。

!!! note "docker-compose-freqai.yml"
    我们在 `docker/docker-compose-freqai.yml` 中提供了一个明确的 docker-compose 文件 - 可以通过 `docker compose -f docker/docker-compose-freqai.yml run ...` 使用 - 或者可以复制以替换原始 docker 文件。此 docker-compose 文件还包含一个（禁用的）部分，用于在 docker 容器内启用 GPU 资源。这显然假设系统有可用的 GPU 资源。

### FreqAI 在开源机器学习领域的地位

FreqAI 是专门为加密货币市场设计的，但其架构足够通用，可以应用于任何时间序列。FreqAI 不是一个独立的机器学习库，而是一个包装器，旨在为用户提供一个简单的界面来与各种机器学习库进行交互。

### 引用 FreqAI

FreqAI 已[发表在开源软件期刊](https://joss.theoj.org/papers/10.21105/joss.04864)上。如果您发现 FreqAI 在您的研究中有用，请使用以下引用：

```bibtex
@article{Caulk2022,
    doi = {10.21105/joss.04864},
    url = {https://doi.org/10.21105/joss.04864},
    year = {2022}, publisher = {The Open Journal},
    volume = {7}, number = {80}, pages = {4864},
    author = {Robert A. Caulk and Elin Törnquist and Matthias Voppichler and Andrew R. Lawless and Ryan McMullan and Wagner Costa Santos and Timothy C. Pogue and Johan van der Vlugt and Stefan P. Gehring and Pascal Schmidt},
    title = {FreqAI: generalizing adaptive modeling for chaotic time-series market forecasts},
    journal = {Journal of Open Source Software} }
```

## 常见陷阱

FreqAI 不能与动态 `VolumePairlists`（或任何动态添加和删除交易对的交易对列表过滤器）结合使用。这是出于性能原因 - FreqAI 依赖于快速预测/重新训练。为了有效地做到这一点，它需要在模拟/实盘实例开始时下载所有训练数据。FreqAI 自动存储和追加新蜡烛图以供将来重新训练。这意味着如果由于成交量交易对列表而在模拟运行后期出现新交易对，它将没有准备好的数据。但是，FreqAI 确实可以与 `ShufflePairlist` 或保持总交易对列表恒定（但根据成交量重新排序交易对）的 `VolumePairlist` 一起工作。

## 其他学习材料

这里我们编译了一些外部材料，提供对 FreqAI 各个组件的更深入了解：

- [实时对比：使用 XGBoost 和 CatBoost 对金融市场数据进行自适应建模](https://emergentmethods.medium.com/real-time-head-to-head-adaptive-modeling-of-financial-market-data-using-xgboost-and-catboost-995a115a7495)
- [FreqAI - 从价格到预测](https://emergentmethods.medium.com/freqai-from-price-to-prediction-6fadac18b665)

## 支持

您可以在各种地方找到 FreqAI 的支持，包括 [Freqtrade discord](https://discord.gg/Jd8JYeWHc4)、专用的 [FreqAI discord](https://discord.gg/7AMWACmbjT) 和 [github issues](https://github.com/freqtrade/freqtrade/issues)。

## 致谢

FreqAI 由一群个人开发，他们都为项目贡献特定的技能。

概念和软件开发：
Robert Caulk @robcaulk

理论头脑风暴和数据分析：
Elin Törnquist @th0rntwig

代码审查和软件架构头脑风暴：
@xmatthias

软件开发：
Wagner Costa @wagnercosta
Emre Suzen @aemr3
Timothy Pogue @wizrds

Beta 测试和错误报告：
Stefan Gehring @bloodhunter4rc, @longyu, Andrew Lawless @paranoidandy, Pascal Schmidt @smidelis, Ryan McMullan @smarmau, Juha Nykänen @suikula, Johan van der Vlugt @jooopiert, Richárd Józsa @richardjosza
