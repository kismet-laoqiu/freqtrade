# 特征工程

## 定义特征

低级特征工程在用户策略中通过一组名为 `feature_engineering_*` 的函数执行。这些函数设置 `基础特征`，如 `RSI`、`MFI`、`EMA`、`SMA`、时间、成交量等。`基础特征` 可以是自定义指标，也可以从任何技术分析库中导入。FreqAI 配备了一组函数来简化快速大规模特征工程：

|  函数 | 描述 |
|---------------|-------------|
| `feature_engineering_expand_all()` | 此可选函数将自动在配置定义的 `indicator_periods_candles`、`include_timeframes`、`include_shifted_candles` 和 `include_corr_pairs` 上扩展定义的特征。
| `feature_engineering_expand_basic()` | 此可选函数将自动在配置定义的 `include_timeframes`、`include_shifted_candles` 和 `include_corr_pairs` 上扩展定义的特征。注意：此函数 *不会* 在 `indicator_periods_candles` 上扩展。
| `feature_engineering_standard()` | 此可选函数将使用基础时间框架的数据框调用一次。这是最后调用的函数，这意味着进入此函数的数据框将包含由其他 `feature_engineering_expand` 函数从基础资产创建的所有特征和列。此函数是进行自定义特殊特征提取（例如 tsfresh）的好地方。此函数也是任何不应自动扩展的特征（例如，一周中的某一天）的好地方。
| `set_freqai_targets()` | 设置模型目标的必需函数。所有目标必须以 `&` 为前缀才能被 FreqAI 内部识别。

同时，高级特征工程在 FreqAI 配置的 `"feature_parameters":{}` 中处理。在此文件中，可以决定在 `base_features` 之上进行大规模特征扩展，例如"包含相关对"或"包含信息时间框架"甚至"包含最近的蜡烛图"。

建议从源提供的示例策略（在 `templates/FreqaiExampleStrategy.py` 中找到）中的模板 `feature_engineering_*` 函数开始，以确保特征定义遵循正确的约定。以下是如何在策略中设置指标和标签的示例：

```python
    def feature_engineering_expand_all(self, dataframe: DataFrame, period, metadata, **kwargs) -> DataFrame:
        """
        *仅适用于启用 FreqAI 的策略*
        此函数将自动在配置定义的 `indicator_periods_candles`、`include_timeframes`、
        `include_shifted_candles` 和 `include_corr_pairs` 上扩展定义的特征。
        换句话说，在此函数中定义的单个特征将自动扩展为总共
        `indicator_periods_candles` * `include_timeframes` * `include_shifted_candles` *
        `include_corr_pairs` 个添加到模型的特征数量。

        所有特征必须以 `%` 为前缀才能被 FreqAI 内部识别。

        使用以下方式访问元数据，如当前交易对/时间框架/周期：

        `metadata["pair"]` `metadata["tf"]`  `metadata["period"]`

        :param df: 将接收特征的策略数据框
        :param period: 指标的周期 - 使用示例：
        :param metadata: 当前交易对的元数据
        dataframe["%-ema-period"] = ta.EMA(dataframe, timeperiod=period)
        """

        dataframe["%-rsi-period"] = ta.RSI(dataframe, timeperiod=period)
        dataframe["%-mfi-period"] = ta.MFI(dataframe, timeperiod=period)
        dataframe["%-adx-period"] = ta.ADX(dataframe, timeperiod=period)
        dataframe["%-sma-period"] = ta.SMA(dataframe, timeperiod=period)
        dataframe["%-ema-period"] = ta.EMA(dataframe, timeperiod=period)

        bollinger = qtpylib.bollinger_bands(
            qtpylib.typical_price(dataframe), window=period, stds=2.2
        )
        dataframe["bb_lowerband-period"] = bollinger["lower"]
        dataframe["bb_middleband-period"] = bollinger["mid"]
        dataframe["bb_upperband-period"] = bollinger["upper"]

        dataframe["%-bb_width-period"] = (
            dataframe["bb_upperband-period"]
            - dataframe["bb_lowerband-period"]
        ) / dataframe["bb_middleband-period"]
        dataframe["%-close-bb_lower-period"] = (
            dataframe["close"] / dataframe["bb_lowerband-period"]
        )

        dataframe["%-roc-period"] = ta.ROC(dataframe, timeperiod=period)

        dataframe["%-relative_volume-period"] = (
            dataframe["volume"] / dataframe["volume"].rolling(period).mean()
        )

        return dataframe

    def feature_engineering_expand_basic(self, dataframe: DataFrame, metadata, **kwargs) -> DataFrame:
        """
        *仅适用于启用 FreqAI 的策略*
        此函数将自动在配置定义的 `include_timeframes`、`include_shifted_candles` 和 
        `include_corr_pairs` 上扩展定义的特征。
        换句话说，在此函数中定义的单个特征将自动扩展为总共
        `include_timeframes` * `include_shifted_candles` * `include_corr_pairs`
        个添加到模型的特征数量。

        此处定义的特征 *不会* 在用户定义的 `indicator_periods_candles` 上自动复制

        使用以下方式访问元数据，如当前交易对/时间框架：

        `metadata["pair"]` `metadata["tf"]`

        所有特征必须以 `%` 为前缀才能被 FreqAI 内部识别。

        :param df: 将接收特征的策略数据框
        :param metadata: 当前交易对的元数据
        dataframe["%-pct-change"] = dataframe["close"].pct_change()
        dataframe["%-ema-200"] = ta.EMA(dataframe, timeperiod=200)
        """
        dataframe["%-pct-change"] = dataframe["close"].pct_change()
        dataframe["%-raw_volume"] = dataframe["volume"]
        dataframe["%-raw_price"] = dataframe["close"]
        return dataframe

    def feature_engineering_standard(self, dataframe: DataFrame, metadata, **kwargs) -> DataFrame:
        """
        *仅适用于启用 FreqAI 的策略*
        此可选函数将使用基础时间框架的数据框调用一次。
        这是最后调用的函数，这意味着进入此函数的数据框将包含
        由所有其他 freqai_feature_engineering_* 函数创建的所有特征和列。

        此函数是进行自定义特殊特征提取（例如 tsfresh）的好地方。
        此函数是任何不应自动扩展的特征（例如一周中的某一天）的好地方。

        使用以下方式访问元数据，如当前交易对：

        `metadata["pair"]`

        所有特征必须以 `%` 为前缀才能被 FreqAI 内部识别。

        :param df: 将接收特征的策略数据框
        :param metadata: 当前交易对的元数据
        使用示例: dataframe["%-day_of_week"] = (dataframe["date"].dt.dayofweek + 1) / 7
        """
        dataframe["%-day_of_week"] = (dataframe["date"].dt.dayofweek + 1) / 7
        dataframe["%-hour_of_day"] = (dataframe["date"].dt.hour + 1) / 25
        return dataframe

    def set_freqai_targets(self, dataframe: DataFrame, metadata, **kwargs) -> DataFrame:
        """
        *仅适用于启用 FreqAI 的策略*
        设置模型目标的必需函数。
        所有目标必须以 `&` 为前缀才能被 FreqAI 内部识别。

        使用以下方式访问元数据，如当前交易对：

        `metadata["pair"]`

        :param df: 将接收目标的策略数据框
        :param metadata: 当前交易对的元数据
        使用示例: dataframe["&-target"] = dataframe["close"].shift(-1) / dataframe["close"]
        """
        dataframe["&-s_close"] = (
            dataframe["close"]
            .shift(-self.freqai_info["feature_parameters"]["label_period_candles"])
            .rolling(self.freqai_info["feature_parameters"]["label_period_candles"])
            .mean()
            / dataframe["close"]
            - 1
            )
        
        return dataframe
```

在所示示例中，用户不希望将 `bb_lowerband` 作为特征传递给模型，因此没有在其前面加上 `%`。但是，用户确实希望将 `bb_width` 传递给模型进行训练/预测，因此在其前面加上了 `%`。

定义了 `基础特征` 后，下一步是使用配置文件中强大的 `feature_parameters` 来扩展它们：

```json
    "freqai": {
        //...
        "feature_parameters" : {
            "include_timeframes": ["5m","15m","4h"],
            "include_corr_pairlist": [
                "ETH/USD",
                "LINK/USD",
                "BNB/USD"
            ],
            "label_period_candles": 24,
            "include_shifted_candles": 2,
            "indicator_periods_candles": [10, 20]
        },
        //...
    }
```

上述配置中的 `include_timeframes` 是策略中每次调用 `feature_engineering_expand_*()` 的时间框架（`tf`）。在所示情况下，用户要求将 `rsi`、`mfi`、`roc` 和 `bb_width` 的 `5m`、`15m` 和 `4h` 时间框架包含在特征集中。

您可以使用 `include_corr_pairlist` 要求为信息对也包含每个定义的特征。这意味着特征集将包含配置中定义的每个相关对（在所示示例中为 `ETH/USD`、`LINK/USD` 和 `BNB/USD`）的所有 `include_timeframes` 上的 `feature_engineering_expand_*()` 的所有特征。

`include_shifted_candles` 表示要包含在特征集中的先前蜡烛图数量。例如，`include_shifted_candles: 2` 告诉 FreqAI 为特征集中的每个特征包含过去 2 个蜡烛图。

总的来说，所示示例策略用户创建的特征数量为：`include_timeframes` 的长度 * `feature_engineering_expand_*()` 中的特征数量 * `include_corr_pairlist` 的长度 * `include_shifted_candles` 数量 * `indicator_periods_candles` 的长度
 $= 3 * 3 * 3 * 2 * 2 = 108$。
 
!!! note "了解更多关于创造性特征工程"
    查看我们的 [medium 文章](https://emergentmethods.medium.com/freqai-from-price-to-prediction-6fadac18b665)，旨在帮助用户学习如何创造性地设计特征。

### 使用 `metadata` 对 `feature_engineering_*` 函数进行更精细的控制

所有 `feature_engineering_*` 和 `set_freqai_targets()` 函数都会传递一个 `metadata` 字典，其中包含有关 FreqAI 为特征构建自动化的 `pair`、`tf`（时间框架）和 `period` 的信息。因此，用户可以在 `feature_engineering_*` 函数内使用 `metadata` 作为阻止/保留某些时间框架、周期、交易对等特征的标准。

```python
def feature_engineering_expand_all(self, dataframe: DataFrame, period, metadata, **kwargs) -> DataFrame:
    if metadata["tf"] == "1h":
        dataframe["%-roc-period"] = ta.ROC(dataframe, timeperiod=period)
```

这将阻止 `ta.ROC()` 被添加到除 `"1h"` 之外的任何时间框架。

### 从训练中返回额外信息

重要的指标可以通过在自定义预测模型类内将它们分配给 `dk.data['extra_returns_per_train']['my_new_value'] = XYZ` 来在每次模型训练结束时返回给策略。

FreqAI 获取此字典中分配的 `my_new_value` 并将其扩展以适应返回给策略的数据框。然后您可以通过 `dataframe['my_new_value']` 在策略中使用返回的指标。FreqAI 中如何使用返回值的示例是用于[创建动态目标阈值](freqai-configuration.md#creating-a-dynamic-target-threshold)的 `&*_mean` 和 `&*_std` 值。

另一个示例，用户想要使用来自交易数据库的实时指标，如下所示：

```json
    "freqai": {
        "extra_returns_per_train": {"total_profit": 4}
    }
```

您需要在配置中设置标准字典，以便 FreqAI 可以返回正确的数据框形状。这些值可能会被预测模型覆盖，但在模型尚未设置它们或需要默认初始值的情况下，预设值就是将要返回的值。

### 为时间重要性加权特征

FreqAI 允许您设置 `weight_factor` 通过指数函数更强烈地加权最近的数据而不是过去的数据：

$$ W_i = \exp(\frac{-i}{\alpha*n}) $$

其中 $W_i$ 是总共 $n$ 个数据点中数据点 $i$ 的权重。下图显示了不同权重因子对特征集中数据点的影响。

![weight-factor](assets/freqai_weight-factor.jpg)

## 构建数据管道

默认情况下，FreqAI 基于用户配置设置构建动态管道。默认设置是稳健的，旨在与各种方法一起工作。这两个步骤是 `MinMaxScaler(-1,1)` 和 `VarianceThreshold`，它删除任何方差为 0 的列。用户可以通过更多配置参数激活其他步骤。例如，如果用户将 `use_SVM_to_remove_outliers: true` 添加到 `freqai` 配置中，那么 FreqAI 将自动将 [`SVMOutlierExtractor`](#identifying-outliers-using-a-support-vector-machine-svm) 添加到管道中。同样，用户可以将 `principal_component_analysis: true` 添加到 `freqai` 配置中以激活 PCA。[DissimilarityIndex](#identifying-outliers-with-the-dissimilarity-index-di) 通过 `DI_threshold: 1` 激活。最后，也可以使用 `noise_standard_deviation: 0.1` 向数据添加噪声。最后，用户可以使用 `use_DBSCAN_to_remove_outliers: true` 添加 [DBSCAN](#identifying-outliers-with-dbscan) 异常值移除。

!!! note "更多信息可用"
    请查看[参数表](freqai-parameter-table.md)以获取有关这些参数的更多信息。


### 自定义管道

鼓励用户通过构建自己的数据管道来自定义数据管道以满足他们的需求。这可以通过在他们的 `IFreqaiModel` `train()` 函数内简单地将 `dk.feature_pipeline` 设置为他们所需的 `Pipeline` 对象来完成，或者如果他们不想触及 `train()` 函数，他们可以在他们的 `IFreqaiModel` 中覆盖 `define_data_pipeline`/`define_label_pipeline` 函数：

!!! note "更多信息可用"
    FreqAI 使用 [`DataSieve`](https://github.com/emergentmethods/datasieve) 管道，它遵循 SKlearn 管道 API，但除其他功能外，还添加了 X、y 和 sample_weight 向量点移除、特征移除、特征名称跟踪之间的一致性。

```python
from datasieve.transforms import SKLearnWrapper, DissimilarityIndex
from datasieve.pipeline import Pipeline
from sklearn.preprocessing import QuantileTransformer, StandardScaler
from freqai.base_models import BaseRegressionModel


class MyFreqaiModel(BaseRegressionModel):
    """
    一些很酷的自定义模型
    """
    def fit(self, data_dictionary: Dict, dk: FreqaiDataKitchen, **kwargs) -> Any:
        """
        我的自定义拟合函数
        """
        model = cool_model.fit()
        return model

    def define_data_pipeline(self) -> Pipeline:
        """
        用户在此定义他们的自定义特征管道（如果他们希望的话）
        """
        feature_pipeline = Pipeline([
            ('qt', SKLearnWrapper(QuantileTransformer(output_distribution='normal'))),
            ('di', ds.DissimilarityIndex(di_threshold=1))
        ])

        return feature_pipeline

    def define_label_pipeline(self) -> Pipeline:
        """
        用户在此定义他们的自定义标签管道（如果他们希望的话）
        """
        label_pipeline = Pipeline([
            ('qt', SKLearnWrapper(StandardScaler())),
        ])

        return label_pipeline
```

在这里，您正在定义将在训练和预测期间用于特征集的确切管道。您可以通过将它们包装在 `SKLearnWrapper` 类中来使用 *大多数* SKLearn 转换步骤，如上所示。此外，您可以使用 [`DataSieve` 库](https://github.com/emergentmethods/datasieve) 中可用的任何转换。

您可以通过创建一个继承自 datasieve `BaseTransform` 并实现您的 `fit()`、`transform()` 和 `inverse_transform()` 方法的类来轻松添加您自己的转换：

```python
from datasieve.transforms.base_transform import BaseTransform
# 导入您需要的任何其他内容

class MyCoolTransform(BaseTransform):
    def __init__(self, **kwargs):
        self.param1 = kwargs.get('param1', 1)

    def fit(self, X, y=None, sample_weight=None, feature_list=None, **kwargs):
        # 对 X、y、sample_weight 或/和 feature_list 做一些事情
        return X, y, sample_weight, feature_list

    def transform(self, X, y=None, sample_weight=None,
                  feature_list=None, outlier_check=False, **kwargs):
        # 对 X、y、sample_weight 或/和 feature_list 做一些事情
        return X, y, sample_weight, feature_list

    def inverse_transform(self, X, y=None, sample_weight=None, feature_list=None, **kwargs):
        # 对 X、y、sample_weight 或/和 feature_list 做/不做一些事情
        return X, y, sample_weight, feature_list
```

!!! note "提示"
    您可以在与您的 `IFreqaiModel` 相同的文件中定义此自定义类。

### 将自定义 `IFreqaiModel` 迁移到新管道

如果您已经创建了自己的带有自定义 `train()`/`predict()` 函数的自定义 `IFreqaiModel`，*并且* 您仍然依赖 `data_cleaning_train/predict()`，那么您需要迁移到新管道。如果您的模型 *不* 依赖 `data_cleaning_train/predict()`，那么您不需要担心此迁移。

有关迁移的更多详细信息可以在[这里](strategy_migration.md#freqai-new-data-pipeline)找到。

## 异常值检测

股票和加密货币市场受到异常值数据点形式的高水平非模式噪声的影响。FreqAI 实现了多种方法来识别此类异常值，从而降低风险。

### 使用相异性指数（DI）识别异常值

相异性指数（DI）旨在量化与模型做出的每个预测相关的不确定性。

您可以通过在配置中包含以下语句来告诉 FreqAI 使用 DI 从训练/测试数据集中移除异常值数据点：

```json
    "freqai": {
        "feature_parameters" : {
            "DI_threshold": 1
        }
    }
```

这将向您的 `feature_pipeline` 添加 `DissimilarityIndex` 步骤并将阈值设置为 1。DI 允许由于低确定性水平而丢弃异常值（在模型特征空间中不存在）的预测。为此，FreqAI 测量每个训练数据点（特征向量）$X_{a}$ 与所有其他训练数据点之间的距离：

$$ d_{ab} = \sqrt{\sum_{j=1}^p(X_{a,j}-X_{b,j})^2} $$

其中 $d_{ab}$ 是标准化点 $a$ 和 $b$ 之间的距离，$p$ 是特征数量，即向量 $X$ 的长度。一组训练数据点的特征距离 $\overline{d}$ 简单地是平均距离的均值：

$$ \overline{d} = \sum_{a=1}^n(\sum_{b=1}^n(d_{ab}/n)/n) $$

$\overline{d}$ 量化训练数据的分布，它与新预测特征向量 $X_k$ 和所有训练数据之间的距离进行比较：

$$ d_k = \arg \min d_{k,i} $$

这使得能够估计相异性指数为：

$$ DI_k = d_k/\overline{d} $$

您可以通过 `DI_threshold` 调整 DI 以增加或减少训练模型的外推。较高的 `DI_threshold` 意味着 DI 更宽松，允许使用距离训练数据更远的预测，而较低的 `DI_threshold` 具有相反的效果，因此丢弃更多预测。

下图描述了 3D 数据集的 DI。

![DI](assets/freqai_DI.jpg)

### 使用支持向量机（SVM）识别异常值

您可以通过在配置中包含以下语句来告诉 FreqAI 使用支持向量机（SVM）从训练/测试数据集中移除异常值数据点：

```json
    "freqai": {
        "feature_parameters" : {
            "use_SVM_to_remove_outliers": true
        }
    }
```

这将向您的 `feature_pipeline` 添加 `SVMOutlierExtractor` 步骤。SVM 将在训练数据上进行训练，SVM 认为超出特征空间的任何数据点都将被移除。

您可以选择通过配置中的 `feature_parameters.svm_params` 字典为 SVM 提供额外参数，例如 `shuffle` 和 `nu`。

参数 `shuffle` 默认设置为 `False` 以确保一致的结果。如果设置为 `True`，在同一数据集上多次运行 SVM 可能会由于 `max_iter` 对算法达到所需 `tol` 来说太低而导致不同的结果。增加 `max_iter` 解决了这个问题，但会导致过程花费更长时间。

参数 `nu`，*非常* 广泛地说，是应该被视为异常值的数据点数量，应该在 0 和 1 之间。

### 使用 DBSCAN 识别异常值

您可以配置 FreqAI 使用 DBSCAN 来聚类和从训练/测试数据集中移除异常值或从预测中移除传入的异常值，通过在配置中激活 `use_DBSCAN_to_remove_outliers`：

```json
    "freqai": {
        "feature_parameters" : {
            "use_DBSCAN_to_remove_outliers": true
        }
    }
```

这将向您的 `feature_pipeline` 添加 `DataSieveDBSCAN` 步骤。这是一种无监督机器学习算法，它在不需要知道应该有多少个聚类的情况下对数据进行聚类。

给定数据点数量 $N$ 和距离 $\varepsilon$，DBSCAN 通过将在距离 $\varepsilon$ 内有 $N-1$ 个其他数据点的所有数据点设置为 *核心点* 来对数据集进行聚类。在距离 *核心点* $\varepsilon$ 内但本身在距离 $\varepsilon$ 内没有 $N-1$ 个其他数据点的数据点被视为 *边缘点*。聚类然后是 *核心点* 和 *边缘点* 的集合。在距离 $<\varepsilon$ 处没有其他数据点的数据点被视为异常值。下图显示了 $N = 3$ 的聚类。

![dbscan](assets/freqai_dbscan.jpg)

FreqAI 使用 `sklearn.cluster.DBSCAN`（详细信息可在 scikit-learn 的网页[这里](https://scikit-learn.org/stable/modules/generated/sklearn.cluster.DBSCAN.html)（外部网站）获得），其中 `min_samples`（$N$）取为特征集中时间点（蜡烛图）数量的 1/4。`eps`（$\varepsilon$）自动计算为从特征集中所有数据点的成对距离中的最近邻计算的 *k-距离图* 中的肘点。


### 使用主成分分析进行数据降维

您可以通过在配置中激活 principal_component_analysis 来减少特征的维度：

```json
    "freqai": {
        "feature_parameters" : {
            "principal_component_analysis": true
        }
    }
```

这将对特征执行 PCA 并减少它们的维度，使得数据集的解释方差 >= 0.999。减少数据维度使训练模型更快，因此允许更多最新的模型。
