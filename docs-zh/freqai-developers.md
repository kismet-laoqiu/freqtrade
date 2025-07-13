# 开发

## 项目架构

FreqAI 的架构和功能是通用化的，以鼓励开发独特的特性、功能、模型等。

类结构和详细的算法概述如下图所示：

![image](assets/freqai_algorithm-diagram.jpg)

如图所示，FreqAI 包含三个不同的对象：

* **IFreqaiModel** - 一个单一的持久对象，包含收集、存储和处理数据、工程特征、运行训练和推理模型所需的所有逻辑。
* **FreqaiDataKitchen** - 一个非持久对象，为每个唯一的资产/模型唯一创建。除了元数据之外，它还包含各种数据处理工具。
* **FreqaiDataDrawer** - 一个单一的持久对象，包含所有历史预测、模型和保存/加载方法。

有各种内置的[预测模型](freqai-configuration.md#using-different-prediction-models)直接继承自 `IFreqaiModel`。这些模型中的每一个都可以完全访问 `IFreqaiModel` 中的所有方法，因此可以随意覆盖任何这些函数。但是，高级用户可能会坚持覆盖 `fit()`、`train()`、`predict()` 和 `data_cleaning_train/predict()`。

## 数据处理

FreqAI 旨在以简化后处理并通过自动数据重新加载增强崩溃恢复能力的方式组织模型文件、预测数据和元数据。数据保存在文件结构 `user_data_dir/models/` 中，其中包含与训练和回测相关的所有数据。`FreqaiDataKitchen()` 严重依赖文件结构进行正确的训练和推理，因此不应手动修改。

### 文件结构

文件结构基于[配置](freqai-configuration.md#setting-up-the-configuration-file)中设置的模型 `identifier` 自动生成。以下结构显示了数据存储在何处以进行后处理：

| 结构 | 描述 |
|-----------|-------------|
| `config_*.json` | 模型特定配置文件的副本。 |
| `historic_predictions.pkl` | 包含在实盘部署期间 `identifier` 模型生命周期内生成的所有历史预测的文件。`historic_predictions.pkl` 用于在崩溃或配置更改后重新加载模型。在主文件损坏的情况下，始终保留备份文件。FreqAI **自动** 检测损坏并用备份替换损坏的文件。 |
| `pair_dictionary.json` | 包含训练队列以及最近训练模型的磁盘位置的文件。 |
| `sub-train-*_TIMESTAMP` | 包含与单个模型相关的所有文件的文件夹，例如：<br>
|| `*_metadata.json` - 模型的元数据，如标准化最大值/最小值、预期训练特征列表等。<br>
|| `*_model.*` - 保存到磁盘的模型文件，用于从崩溃中重新加载。可以是 `joblib`（典型的提升库）、`zip`（stable_baselines）、`hd5`（keras 类型）等。<br>
|| `*_pca_object.pkl` - [主成分分析（PCA）](freqai-feature-engineering.md#data-dimensionality-reduction-with-principal-component-analysis) 变换（如果在配置中设置了 `principal_component_analysis: True`），将用于变换未见的预测特征。<br>
|| `*_svm_model.pkl` - [支持向量机（SVM）](freqai-feature-engineering.md#identifying-outliers-using-a-support-vector-machine-svm) 模型（如果在配置中设置了 `use_SVM_to_remove_outliers: True`），用于检测未见预测特征中的异常值。<br>
|| `*_trained_df.pkl` - 包含用于训练 `identifier` 模型的所有训练特征的数据框。这用于计算[相异性指数（DI）](freqai-feature-engineering.md#identifying-outliers-with-the-dissimilarity-index-di)，也可用于后处理。<br>
|| `*_trained_dates.df.pkl` - 与 `trained_df.pkl` 相关的日期，对后处理很有用。 |

示例文件结构如下所示：

```
├── models
│   └── unique-id
│       ├── config_freqai.example.json
│       ├── historic_predictions.backup.pkl
│       ├── historic_predictions.pkl
│       ├── pair_dictionary.json
│       ├── sub-train-1INCH_1662821319
│       │   ├── cb_1inch_1662821319_metadata.json
│       │   ├── cb_1inch_1662821319_model.joblib
│       │   ├── cb_1inch_1662821319_pca_object.pkl
│       │   ├── cb_1inch_1662821319_svm_model.joblib
│       │   ├── cb_1inch_1662821319_trained_dates_df.pkl
│       │   └── cb_1inch_1662821319_trained_df.pkl
│       ├── sub-train-1INCH_1662821371
│       │   ├── cb_1inch_1662821371_metadata.json
│       │   ├── cb_1inch_1662821371_model.joblib
│       │   ├── cb_1inch_1662821371_pca_object.pkl
│       │   ├── cb_1inch_1662821371_svm_model.joblib
│       │   ├── cb_1inch_1662821371_trained_dates_df.pkl
│       │   └── cb_1inch_1662821371_trained_df.pkl
│       ├── sub-train-ADA_1662821344
│       │   ├── cb_ada_1662821344_metadata.json
│       │   ├── cb_ada_1662821344_model.joblib
│       │   ├── cb_ada_1662821344_pca_object.pkl
│       │   ├── cb_ada_1662821344_svm_model.joblib
│       │   ├── cb_ada_1662821344_trained_dates_df.pkl
│       │   └── cb_ada_1662821344_trained_df.pkl
│       └── sub-train-ADA_1662821399
│           ├── cb_ada_1662821399_metadata.json
│           ├── cb_ada_1662821399_model.joblib
│           ├── cb_ada_1662821399_pca_object.pkl
│           ├── cb_ada_1662821399_svm_model.joblib
│           ├── cb_ada_1662821399_trained_dates_df.pkl
│           └── cb_ada_1662821399_trained_df.pkl

```
