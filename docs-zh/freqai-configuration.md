# 配置

FreqAI 通过典型的 [Freqtrade 配置文件](configuration.md) 和标准的 [Freqtrade 策略](strategy-customization.md) 进行配置。FreqAI 配置和策略文件的示例可以分别在 `config_examples/config_freqai.example.json` 和 `freqtrade/templates/FreqaiExampleStrategy.py` 中找到。

## 设置配置文件

虽然有很多额外的参数可供选择，如 [参数表](freqai-parameter-table.md#parameter-table) 中所强调的，FreqAI 配置至少必须包含以下参数（参数值仅为示例）：

```json
    "freqai": {
        "enabled": true,
        "purge_old_models": 2,
        "train_period_days": 30,
        "backtest_period_days": 7,
        "identifier" : "unique-id",
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
        "data_split_parameters" : {
            "test_size": 0.25
        }
    }
```

完整的示例配置可在 `config_examples/config_freqai.example.json` 中找到。

!!! Note "注意"
    `identifier` 经常被新手忽略，但是这个值在您的配置中起着重要作用。这个值是您选择的唯一 ID，用于描述您的一次运行。保持相同的值可以让您维持崩溃恢复能力以及更快的回测。一旦您想要尝试新的运行（新特征、新模型等），您应该更改此值（或删除 `user_data/models/unique-id` 文件夹）。更多详细信息请参见 [参数表](freqai-parameter-table.md#feature-parameters)。

## 构建 FreqAI 策略

FreqAI 策略需要在标准 [Freqtrade 策略](strategy-customization.md) 中包含以下代码行：

```python
    # 用户应定义最大启动蜡烛数量（传递给任何单个指标的最大蜡烛数量）
    startup_candle_count: int = 20

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:

        # 模型将返回用户在 `set_freqai_targets()` 中创建的所有标签
        # （和附加目标），是否应该接受预测的指示，
        # 用户在 `set_freqai_targets()` 中为每个训练期间创建的每个标签的
        # 目标均值/标准差值。

        dataframe = self.freqai.start(dataframe, metadata, self)

        return dataframe

    def feature_engineering_expand_all(self, dataframe: DataFrame, period, **kwargs) -> DataFrame:
        """
        *仅在启用 FreqAI 的策略中有效*
        此函数将自动扩展配置中定义的特征到
        `indicator_periods_candles`、`include_timeframes`、`include_shifted_candles` 和
        `include_corr_pairs`。换句话说，在此函数中定义的单个特征
        将自动扩展为总共
        `indicator_periods_candles` * `include_timeframes` * `include_shifted_candles` *
        `include_corr_pairs` 个特征添加到模型中。

        所有特征必须以 `%` 为前缀才能被 FreqAI 内部识别。

        :param df: 将接收特征的策略数据框
        :param period: 指标的周期 - 使用示例：
        dataframe["%-ema-period"] = ta.EMA(dataframe, timeperiod=period)
        """

        dataframe["%-rsi-period"] = ta.RSI(dataframe, timeperiod=period)
        dataframe["%-mfi-period"] = ta.MFI(dataframe, timeperiod=period)
        dataframe["%-adx-period"] = ta.ADX(dataframe, timeperiod=period)
        dataframe["%-sma-period"] = ta.SMA(dataframe, timeperiod=period)
        dataframe["%-ema-period"] = ta.EMA(dataframe, timeperiod=period)

        return dataframe

    def feature_engineering_expand_basic(self, dataframe: DataFrame, **kwargs) -> DataFrame:
        """
        *仅在启用 FreqAI 的策略中有效*
        此函数将自动扩展配置中定义的特征到
        `include_timeframes`、`include_shifted_candles` 和 `include_corr_pairs`。
        换句话说，在此函数中定义的单个特征
        将自动扩展为总共
        `include_timeframes` * `include_shifted_candles` * `include_corr_pairs`
        个特征添加到模型中。

        在此处定义的特征将*不会*在用户定义的
        `indicator_periods_candles` 上自动复制

        所有特征必须以 `%` 为前缀才能被 FreqAI 内部识别。

        :param df: 将接收特征的策略数据框
        dataframe["%-pct-change"] = dataframe["close"].pct_change()
        dataframe["%-ema-200"] = ta.EMA(dataframe, timeperiod=200)
        """
        dataframe["%-pct-change"] = dataframe["close"].pct_change()
        dataframe["%-raw_volume"] = dataframe["volume"]
        dataframe["%-raw_price"] = dataframe["close"]
        return dataframe

    def feature_engineering_standard(self, dataframe: DataFrame, **kwargs) -> DataFrame:
        """
        *仅在启用 FreqAI 的策略中有效*
        此可选函数将使用基础时间框架的数据框调用一次。
        这是最后调用的函数，这意味着进入此函数的数据框
        将包含所有其他 freqai_feature_engineering_* 函数创建的
        所有特征和列。

        此函数是进行自定义异构特征提取（例如 tsfresh）的好地方。
        此函数是任何不应自动扩展的特征的好地方
        （例如一周中的某一天）。

        所有特征必须以 `%` 为前缀才能被 FreqAI 内部识别。

        :param df: 将接收特征的策略数据框
        使用示例：dataframe["%-day_of_week"] = (dataframe["date"].dt.dayofweek + 1) / 7
        """
        dataframe["%-day_of_week"] = (dataframe["date"].dt.dayofweek + 1) / 7
        dataframe["%-hour_of_day"] = (dataframe["date"].dt.hour + 1) / 25
        return dataframe

    def set_freqai_targets(self, dataframe: DataFrame, **kwargs) -> DataFrame:
        """
        *仅在启用 FreqAI 的策略中有效*
        设置模型目标的必需函数。
        所有目标必须以 `&` 为前缀才能被 FreqAI 内部识别。

        :param df: 将接收目标的策略数据框
        使用示例：dataframe["&-target"] = dataframe["close"].shift(-1) / dataframe["close"]
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

注意 `feature_engineering_*()` 是添加 [特征](freqai-feature-engineering.md#feature-engineering) 的地方。同时 `set_freqai_targets()` 添加标签/目标。完整的示例策略可在 `templates/FreqaiExampleStrategy.py` 中找到。

!!! Note "注意"
    `self.freqai.start()` 函数不能在 `populate_indicators()` 之外调用。

!!! Note "注意"
    特征**必须**在 `feature_engineering_*()` 中定义。在 `populate_indicators()` 中定义 FreqAI 特征将导致算法在实时/模拟模式下失败。为了添加与特定交易对或时间框架无关的通用特征，您应该使用 `feature_engineering_standard()`（如 `freqtrade/templates/FreqaiExampleStrategy.py` 中所示）。

## 重要的数据框键模式

以下是您可以期望在典型策略数据框（`df[]`）中包含/使用的值：

|  数据框键 | 描述 |
|------------|-------------|
| `df['&*']` | 在 `set_freqai_targets()` 中以 `&` 为前缀的任何数据框列都被视为 FreqAI 内部的训练目标（标签）（通常遵循命名约定 `&-s*`）。例如，要预测未来 40 根蜡烛的收盘价，您可以设置 `df['&-s_close'] = df['close'].shift(-self.freqai_info["feature_parameters"]["label_period_candles"])` 并在配置中设置 `"label_period_candles": 40`。FreqAI 进行预测并在相同的键（`df['&-s_close']`）下返回它们，以便在 `populate_entry/exit_trend()` 中使用。<br> **数据类型：** 取决于模型的输出。
| `df['&*_std/mean']` | 训练期间定义标签的标准差和均值（或使用 `fit_live_predictions_candles` 进行实时跟踪）。通常用于理解预测的稀有性（使用 z-score，如 `templates/FreqaiExampleStrategy.py` 中所示，并在 [此处](#creating-a-dynamic-target-threshold) 解释，以评估在训练期间或使用 `fit_live_predictions_candles` 历史上观察到特定预测的频率）。<br> **数据类型：** 浮点数。
| `df['do_predict']` | 异常数据点的指示。返回值是 -2 到 2 之间的整数，让您知道预测是否可信。`do_predict==1` 意味着预测是可信的。如果输入数据点的相异性指数（DI，详见 [此处](freqai-feature-engineering.md#identifying-outliers-with-the-dissimilarity-index-di)）超过配置中定义的阈值，FreqAI 将从 `do_predict` 中减去 1，导致 `do_predict==0`。如果 `use_SVM_to_remove_outliers` 处于活动状态，支持向量机（SVM，详见 [此处](freqai-feature-engineering.md#identifying-outliers-using-a-support-vector-machine-svm)）也可能检测训练和预测数据中的异常值。在这种情况下，SVM 也会从 `do_predict` 中减去 1。如果输入数据点被 SVM 认为是异常值但 DI 不认为，或反之，结果将是 `do_predict==0`。如果 DI 和 SVM 都认为输入数据点是异常值，结果将是 `do_predict==-1`。与 SVM 一样，如果 `use_DBSCAN_to_remove_outliers` 处于活动状态，DBSCAN（详见 [此处](freqai-feature-engineering.md#identifying-outliers-with-dbscan)）也可能检测异常值并从 `do_predict` 中减去 1。因此，如果 SVM 和 DBSCAN 都处于活动状态并识别出超过 DI 阈值的数据点为异常值，结果将是 `do_predict==-2`。特殊情况是当 `do_predict == 2` 时，这意味着模型由于超过 `expired_hours` 而过期。<br> **数据类型：** -2 到 2 之间的整数。
| `df['DI_values']` | 相异性指数（DI）值是 FreqAI 对预测置信度的代理。较低的 DI 意味着预测接近训练数据，即更高的预测置信度。有关 DI 的详细信息请参见 [此处](freqai-feature-engineering.md#identifying-outliers-with-the-dissimilarity-index-di)。<br> **数据类型：** 浮点数。
| `df['%*']` | 在 `feature_engineering_*()` 中以 `%` 为前缀的任何数据框列都被视为训练特征。例如，您可以通过设置 `df['%-rsi']` 将 RSI 包含在训练特征集中（类似于 `templates/FreqaiExampleStrategy.py` 中的做法）。有关如何执行此操作的更多详细信息请参见 [此处](freqai-feature-engineering.md)。<br> **注意：** 由于以 `%` 为前缀的特征数量可能会非常快速地增加（使用例如 `include_shifted_candles` 和 `include_timeframes` 的乘法功能很容易设计出数万个特征，如 [参数表](freqai-parameter-table.md) 中所述），这些特征会从 FreqAI 返回给策略的数据框中移除。要保留特定类型的特征用于绘图目的，您可以在其前面加上 `%%`（详见下文）。<br> **数据类型：** 取决于用户创建的特征。
| `df['%%*']` | 在 `feature_engineering_*()` 中以 `%%` 为前缀的任何数据框列都被视为训练特征，与上面的 `%` 前缀相同。但是，在这种情况下，特征会返回给策略，用于 FreqUI/plot-dataframe 绘图和在模拟/实时/回测中监控。<br> **数据类型：** 取决于用户创建的特征。请注意，在 `feature_engineering_expand()` 中创建的特征将根据您配置的扩展（即 `include_timeframes`、`include_corr_pairlist`、`indicators_periods_candles`、`include_shifted_candles`）具有自动 FreqAI 命名模式。因此，如果您想从 `feature_engineering_expand_all()` 绘制 `%%-rsi`，您的绘图配置的最终命名方案将是：`%%-rsi-period_10_ETH/USDT:USDT_1h`，用于 `period=10`、`timeframe=1h` 和 `pair=ETH/USDT:USDT` 的 `rsi` 特征（如果您使用期货交易对，会添加 `:USDT`）。在 `self.freqai.start()` 之后在您的 `populate_indicators()` 中简单地添加 `print(dataframe.columns)` 来查看返回给策略用于绘图目的的可用特征的完整列表是很有用的。

## 设置 `startup_candle_count`

FreqAI 策略中的 `startup_candle_count` 需要以与标准 Freqtrade 策略相同的方式设置（详见 [此处](strategy-customization.md#strategy-startup-period)）。此值由 Freqtrade 使用，以确保在调用 `dataprovider` 时提供足够的数据，以避免第一次训练开始时出现任何 NaN。您可以通过识别传递给指标创建函数（例如 TA-Lib 函数）的最长周期（以蜡烛单位）来轻松设置此值。在所示示例中，`startup_candle_count` 为 20，因为这是 `indicators_periods_candles` 中的最大值。

!!! Note "注意"
    有些情况下，TA-Lib 函数实际上需要比传递的 `period` 更多的数据，否则特征数据集会被 NaN 填充。根据经验，将 `startup_candle_count` 乘以 2 总是会导致完全无 NaN 的训练数据集。因此，通常最安全的做法是将预期的 `startup_candle_count` 乘以 2。注意此日志消息以确认数据是干净的：

    ```
    2022-08-31 15:14:04 - freqtrade.freqai.data_kitchen - INFO - dropped 0 training points due to NaNs in populated dataset 4319.
    ```

## 创建动态目标阈值

决定何时进入或退出交易可以以动态方式完成，以反映当前市场条件。FreqAI 允许您从模型训练中返回额外信息（更多信息 [此处](freqai-feature-engineering.md#returning-additional-info-from-training)）。例如，`&*_std/mean` 返回值描述了*最近训练期间*目标/标签的统计分布。将给定预测与这些值进行比较可以让您了解预测的稀有性。在 `templates/FreqaiExampleStrategy.py` 中，`target_roi` 和 `sell_roi` 被定义为距离均值 1.25 个 z-score，这会导致更接近均值的预测被过滤掉。

```python
dataframe["target_roi"] = dataframe["&-s_close_mean"] + dataframe["&-s_close_std"] * 1.25
dataframe["sell_roi"] = dataframe["&-s_close_mean"] - dataframe["&-s_close_std"] * 1.25
```

要考虑*历史预测*的总体来创建动态目标，而不是如上所述的训练信息，您可以在配置中设置 `fit_live_predictions_candles` 为您希望用于生成目标统计的历史预测蜡烛数量。

```json
    "freqai": {
        "fit_live_predictions_candles": 300,
    }
```

如果设置了此值，FreqAI 将最初使用训练数据的预测，随后开始引入生成的真实预测数据。FreqAI 将保存此历史数据，以便在您停止并重新启动具有相同 `identifier` 的模型时重新加载。

## 使用不同的预测模型

FreqAI 有多个示例预测模型库，可以通过标志 `--freqaimodel` 直接使用。这些库包括 `CatBoost`、`LightGBM` 和 `XGBoost` 回归、分类和多目标模型，可以在 `freqai/prediction_models/` 中找到。

回归和分类模型在预测目标方面有所不同 - 回归模型将预测连续值的目标，例如明天 BTC 的价格，而分类器将预测离散值的目标，例如明天 BTC 的价格是否会上涨。这意味着您必须根据使用的模型类型以不同方式指定目标（详见 [下文](#setting-model-targets)）。

所有上述模型库都实现了梯度提升决策树算法。它们都基于集成学习的原理工作，其中来自多个简单学习器的预测被组合以获得更稳定和通用的最终预测。在这种情况下，简单学习器是决策树。梯度提升是指学习方法，其中每个简单学习器按顺序构建 - 后续学习器用于改进前一个学习器的错误。如果您想了解更多关于不同模型库的信息，可以在它们各自的文档中找到信息：

* CatBoost: https://catboost.ai/en/docs/
* LightGBM: https://lightgbm.readthedocs.io/en/v3.3.2/#
* XGBoost: https://xgboost.readthedocs.io/en/stable/#

还有许多在线文章描述和比较这些算法。一些相对轻量级的示例是 [CatBoost vs. LightGBM vs. XGBoost — Which is the best algorithm?](https://towardsdatascience.com/catboost-vs-lightgbm-vs-xgboost-c80f40662924#:~:text=In%20CatBoost%2C%20symmetric%20trees%2C%20or,the%20same%20depth%20can%20differ.) 和 [XGBoost, LightGBM or CatBoost — which boosting algorithm should I use?](https://medium.com/riskified-technology/xgboost-lightgbm-or-catboost-which-boosting-algorithm-should-i-use-e7fda7bb36bc)。请记住，每个模型的性能高度依赖于应用，因此任何报告的指标可能不适用于您对模型的特定使用。

除了 FreqAI 中已有的模型外，还可以使用 `IFreqaiModel` 类自定义和创建您自己的预测模型。建议您继承 `fit()`、`train()` 和 `predict()` 来自定义训练过程的各个方面。您可以将自定义 FreqAI 模型放在 `user_data/freqaimodels` 中 - freqtrade 将根据提供的 `--freqaimodel` 名称从那里选择它们 - 该名称必须与您的自定义模型的类名相对应。
确保使用唯一名称以避免覆盖内置模型。

### 设置模型目标

#### 回归器

如果您使用回归器，您需要指定具有连续值的目标。FreqAI 包含各种回归器，例如通过标志 `--freqaimodel CatboostRegressor` 的 `CatboostRegressor`。如何设置回归目标以预测未来 100 根蜡烛价格的示例是

```python
df['&s-close_price'] = df['close'].shift(-100)
```

如果您想预测多个目标，您需要使用如上所示的相同语法定义多个标签。

#### 分类器

如果您使用分类器，您需要指定具有离散值的目标。FreqAI 包含各种分类器，例如通过标志 `--freqaimodel CatboostClassifier` 的 `CatboostClassifier`。如果您选择使用分类器，需要使用字符串设置类别。例如，如果您想预测未来 100 根蜡烛的价格是上涨还是下跌，您可以设置

```python
df['&s-up_or_down'] = np.where( df["close"].shift(-100) > df["close"], 'up', 'down')
```

如果您想预测多个目标，您必须在同一标签列中指定所有标签。例如，您可以添加标签 `same` 来定义价格未变化的情况，设置

```python
df['&s-up_or_down'] = np.where( df["close"].shift(-100) > df["close"], 'up', 'down')
df['&s-up_or_down'] = np.where( df["close"].shift(-100) == df["close"], 'same', df['&s-up_or_down'])
```

## PyTorch 模块

### 快速开始

快速运行 pytorch 模型的最简单方法是使用以下命令（用于回归任务）：

```bash
freqtrade trade --config config_examples/config_freqai.example.json --strategy FreqaiExampleStrategy --freqaimodel PyTorchMLPRegressor --strategy-path freqtrade/templates
```

!!! Note "安装/docker"
    PyTorch 模块需要大型包如 `torch`，应在 `./setup.sh -i` 期间通过回答"Do you also want dependencies for freqai-rl or PyTorch (~700mb additional space required) [y/N]?"问题为"y"来明确请求。
    偏好 docker 的用户应确保使用附加了 `_freqaitorch` 的 docker 镜像。
    我们在 `docker/docker-compose-freqai.yml` 中提供了明确的 docker-compose 文件 - 可以通过 `docker compose -f docker/docker-compose-freqai.yml run ...` 使用 - 或者可以复制以替换原始 docker 文件。
    此 docker-compose 文件还包含一个（禁用的）部分，用于在 docker 容器内启用 GPU 资源。这显然假设系统有可用的 GPU 资源。

    PyTorch 在版本 2.3 中停止了对 macOS x64（基于 intel 的 Apple 设备）的支持。随后，freqtrade 也停止了在此平台上对 PyTorch 的支持。

### 结构

#### 模型

您可以通过在自定义 [`IFreqaiModel` 文件](#using-different-prediction-models) 中简单定义您的 `nn.Module` 类，然后在您的 `def train()` 函数中使用该类来在 PyTorch 中构建您自己的神经网络架构。以下是使用 PyTorch 实现逻辑回归模型的示例（应与 nn.BCELoss 准则一起使用）用于分类任务。

```python

class LogisticRegression(nn.Module):
    def __init__(self, input_size: int):
        super().__init__()
        # 定义您的层
        self.linear = nn.Linear(input_size, 1)
        self.activation = nn.Sigmoid()

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # 定义前向传播
        out = self.linear(x)
        out = self.activation(out)
        return out

class MyCoolPyTorchClassifier(BasePyTorchClassifier):
    """
    这是一个自定义 IFreqaiModel，展示用户如何为其训练
    设置自己的自定义神经网络架构。
    """

    @property
    def data_convertor(self) -> PyTorchDataConvertor:
        return DefaultPyTorchDataConvertor(target_tensor_type=torch.float)

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        config = self.freqai_info.get("model_training_parameters", {})
        self.learning_rate: float = config.get("learning_rate",  3e-4)
        self.model_kwargs: dict[str, Any] = config.get("model_kwargs",  {})
        self.trainer_kwargs: dict[str, Any] = config.get("trainer_kwargs",  {})

    def fit(self, data_dictionary: dict, dk: FreqaiDataKitchen, **kwargs) -> Any:
        """
        用户在此设置训练和测试数据以适应其所需的模型
        :param data_dictionary: 包含训练、测试、标签、权重的所有数据的字典
        :param dk: 当前币种/模型的数据厨房对象
        """

        class_names = self.get_class_names()
        self.convert_label_column_to_int(data_dictionary, dk, class_names)
        n_features = data_dictionary["train_features"].shape[-1]
        model = LogisticRegression(
            input_dim=n_features
        )
        model.to(self.device)
        optimizer = torch.optim.AdamW(model.parameters(), lr=self.learning_rate)
        criterion = torch.nn.CrossEntropyLoss()
        init_model = self.get_init_model(dk.pair)
        trainer = PyTorchModelTrainer(
            model=model,
            optimizer=optimizer,
            criterion=criterion,
            model_meta_data={"class_names": class_names},
            device=self.device,
            init_model=init_model,
            data_convertor=self.data_convertor,
            **self.trainer_kwargs,
        )
        trainer.fit(data_dictionary, self.splits)
        return trainer

```

#### 训练器

`PyTorchModelTrainer` 执行惯用的 PyTorch 训练循环：
定义我们的模型、损失函数和优化器，然后将它们移动到适当的设备（GPU 或 CPU）。在循环内，我们遍历数据加载器中的批次，将数据移动到设备，计算预测和损失，反向传播，并使用优化器更新模型参数。

此外，训练器负责以下工作：
 - 保存和加载模型
 - 将数据从 `pandas.DataFrame` 转换为 `torch.Tensor`。

#### 与 Freqai 模块的集成

像所有 freqai 模型一样，PyTorch 模型继承 `IFreqaiModel`。`IFreqaiModel` 声明三个抽象方法：`train`、`fit` 和 `predict`。我们在三个层次的层次结构中实现这些方法。
从上到下：

1. `BasePyTorchModel` - 实现 `train` 方法。所有 `BasePyTorch*` 都继承它。负责一般数据准备（例如数据标准化）和调用 `fit` 方法。设置子类使用的 `device` 属性。设置父类使用的 `model_type` 属性。
2. `BasePyTorch*` - 实现 `predict` 方法。这里，`*` 代表一组算法，如分类器或回归器。负责数据预处理、预测和必要时的后处理。
3. `PyTorch*Classifier` / `PyTorch*Regressor` - 实现 `fit` 方法。负责主要的训练流程，我们在其中初始化训练器和模型对象。

![image](assets/freqai_pytorch-diagram.png)

#### 完整示例

使用 MLP（多层感知器）模型、MSELoss 准则和 AdamW 优化器构建 PyTorch 回归器。

```python
class PyTorchMLPRegressor(BasePyTorchRegressor):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        config = self.freqai_info.get("model_training_parameters", {})
        self.learning_rate: float = config.get("learning_rate",  3e-4)
        self.model_kwargs: dict[str, Any] = config.get("model_kwargs",  {})
        self.trainer_kwargs: dict[str, Any] = config.get("trainer_kwargs",  {})

    def fit(self, data_dictionary: dict, dk: FreqaiDataKitchen, **kwargs) -> Any:
        n_features = data_dictionary["train_features"].shape[-1]
        model = PyTorchMLPModel(
            input_dim=n_features,
            output_dim=1,
            **self.model_kwargs
        )
        model.to(self.device)
        optimizer = torch.optim.AdamW(model.parameters(), lr=self.learning_rate)
        criterion = torch.nn.MSELoss()
        init_model = self.get_init_model(dk.pair)
        trainer = PyTorchModelTrainer(
            model=model,
            optimizer=optimizer,
            criterion=criterion,
            device=self.device,
            init_model=init_model,
            target_tensor_type=torch.float,
            **self.trainer_kwargs,
        )
        trainer.fit(data_dictionary)
        return trainer
```

在这里我们创建了一个实现 `fit` 方法的 `PyTorchMLPRegressor` 类。`fit` 方法指定了训练构建块：模型、优化器、准则和训练器。我们继承了 `BasePyTorchRegressor` 和 `BasePyTorchModel`，前者实现了适合我们回归任务的 `predict` 方法，后者实现了 train 方法。

??? Note "为分类器设置类名"
    使用分类器时，用户必须通过覆盖 `IFreqaiModel.class_names` 属性来声明类名（或目标）。这通过在 FreqAI 策略内的 `set_freqai_targets` 方法中设置 `self.freqai.class_names` 来实现。

    例如，如果您使用二元分类器来预测价格变动为上涨或下跌，您可以如下设置类名：
    ```python
    def set_freqai_targets(self, dataframe: DataFrame, metadata: dict, **kwargs) -> DataFrame:
        self.freqai.class_names = ["down", "up"]
        dataframe['&s-up_or_down'] = np.where(dataframe["close"].shift(-100) >
                                                  dataframe["close"], 'up', 'down')

        return dataframe
    ```
    要查看完整示例，您可以参考 [分类器测试策略类](https://github.com/freqtrade/freqtrade/blob/develop/tests/strategy/strats/freqai_test_classifier.py)。


#### 使用 `torch.compile()` 提高性能

Torch 提供了一个 `torch.compile()` 方法，可用于改善特定 GPU 硬件的性能。更多详细信息可以在 [此处](https://pytorch.org/tutorials/intermediate/torch_compile_tutorial.html) 找到。简而言之，您只需将您的 `model` 包装在 `torch.compile()` 中：


```python
        model = PyTorchMLPModel(
            input_dim=n_features,
            output_dim=1,
            **self.model_kwargs
        )
        model.to(self.device)
        model = torch.compile(model)
```

然后正常使用模型。请记住，这样做将移除急切执行，这意味着错误和回溯将不会提供信息。
