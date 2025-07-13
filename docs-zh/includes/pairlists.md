## 交易对列表和交易对列表处理器

交易对列表处理器定义机器人应该交易的交易对列表（交易对列表）。它们在配置设置的 `pairlists` 部分中配置。

在您的配置中，您可以使用静态交易对列表（由 [`StaticPairList`](#static-pair-list) 交易对列表处理器定义）和动态交易对列表（由 [`VolumePairList`](#volume-pair-list) 和 [`PercentChangePairList`](#percent-change-pair-list) 交易对列表处理器定义）。

此外，[`AgeFilter`](#agefilter)、[`PrecisionFilter`](#precisionfilter)、[`PriceFilter`](#pricefilter)、[`ShuffleFilter`](#shufflefilter)、[`SpreadFilter`](#spreadfilter) 和 [`VolatilityFilter`](#volatilityfilter) 作为交易对列表过滤器，移除某些交易对和/或移动它们在交易对列表中的位置。

如果使用多个交易对列表处理器，它们会被链接，所有交易对列表处理器的组合形成机器人用于交易和回测的最终交易对列表。交易对列表处理器按照它们配置的顺序执行。您可以定义 `StaticPairList`、`VolumePairList`、`ProducerPairList`、`RemotePairList`、`MarketCapPairList` 或 `PercentChangePairList` 作为起始交易对列表处理器。

非活跃市场总是从结果交易对列表中移除。明确列入黑名单的交易对（在 `pair_blacklist` 配置设置中的那些）也总是从结果交易对列表中移除。

### 交易对黑名单

交易对黑名单（通过配置中的 `exchange.pair_blacklist` 配置）禁止某些交易对进行交易。
这可以简单到排除 `DOGE/BTC` - 这将移除确切的这个交易对。

交易对黑名单也支持通配符（正则表达式样式）- 所以 `BNB/.*` 将排除所有以 BNB 开头的交易对。
您也可以使用类似 `.*DOWN/BTC` 或 `.*UP/BTC` 来排除杠杆代币（检查您交易所的交易对命名约定！）

### 可用的交易对列表处理器

* [`StaticPairList`](#static-pair-list)（默认，如果没有不同配置）
* [`VolumePairList`](#volume-pair-list)
* [`PercentChangePairList`](#percent-change-pair-list)
* [`ProducerPairList`](#producerpairlist)
* [`RemotePairList`](#remotepairlist)
* [`MarketCapPairList`](#marketcappairlist)
* [`AgeFilter`](#agefilter)
* [`FullTradesFilter`](#fulltradesfilter)
* [`OffsetFilter`](#offsetfilter)
* [`PerformanceFilter`](#performancefilter)
* [`PrecisionFilter`](#precisionfilter)
* [`PriceFilter`](#pricefilter)
* [`ShuffleFilter`](#shufflefilter)
* [`SpreadFilter`](#spreadfilter)
* [`RangeStabilityFilter`](#rangestabilityfilter)
* [`VolatilityFilter`](#volatilityfilter)

!!! Tip "测试交易对列表"
    交易对列表配置可能很难正确设置。最好使用 [`test-pairlist`](utils.md#test-pairlist) 实用程序子命令来快速测试您的配置。

#### 静态交易对列表

默认情况下，使用 `StaticPairList` 方法，它使用配置中静态定义的交易对白名单。交易对列表也支持通配符（正则表达式样式）- 所以 `.*/BTC` 将包含所有以 BTC 作为基础货币的交易对。

它使用来自 `exchange.pair_whitelist` 和 `exchange.pair_blacklist` 的配置，在下面的示例中，将交易 BTC/USDT 和 ETH/USDT - 并将阻止 BNB/USDT 交易。

两个 `pair_*list` 参数都支持正则表达式 - 所以像 `.*/USDT` 这样的值将启用所有不在黑名单中的交易对的交易。

```json
"exchange": {
    "name": "...",
    // ...
    "pair_whitelist": [
        "BTC/USDT",
        "ETH/USDT",
        // ...
    ],
    "pair_blacklist": [
        "BNB/USDT",
        // ...
    ]
},
"pairlists": [
    {"method": "StaticPairList"}
],
```

默认情况下，只允许当前启用的交易对。
要跳过对活跃市场的交易对验证，请在 `StaticPairList` 配置中设置 `"allow_inactive": true`。
这对于回测过期的交易对（如季度现货市场）很有用。

当在"后续"位置使用时（例如在 VolumePairlist 之后），`'pair_whitelist'` 中的所有交易对将被添加到交易对列表的末尾。

#### 成交量交易对列表

`VolumePairList` 采用按交易量对交易对进行排序/过滤。它根据 `sort_key`（只能是 `quoteVolume`）选择 `number_assets` 个顶级交易对。

当在交易对列表处理器链中的非领导位置使用时（在 StaticPairList 和其他交易对列表过滤器之后），`VolumePairList` 考虑先前交易对列表处理器的输出，添加其按交易量对交易对的排序/选择。

当在交易对列表处理器链的领导位置使用时，`pair_whitelist` 配置设置被忽略。相反，`VolumePairList` 从交易所上所有具有匹配基础货币的可用市场中选择顶级资产。

`refresh_period` 设置允许定义交易对列表刷新的周期（以秒为单位）。默认为 1800 秒（30 分钟）。
`VolumePairList` 上的交易对列表缓存（`refresh_period`）仅适用于生成交易对列表。
过滤实例（不在列表的第一个位置）不会应用任何缓存（除了在高级模式下为蜡烛图持续时间缓存蜡烛图），并且总是使用最新数据。

`VolumePairList` 默认基于交易所的行情数据，如 ccxt 库报告的：

* `quoteVolume` 是在过去 24 小时内交易（买入或卖出）的报价（基础）货币数量。

```json
"pairlists": [
    {
        "method": "VolumePairList",
        "number_assets": 20,
        "sort_key": "quoteVolume",
        "min_value": 0,
        "max_value": 8000000,
        "refresh_period": 1800
    }
],
```

您可以使用 `min_value` 定义最小成交量 - 这将过滤掉在指定时间范围内成交量低于指定值的交易对。
除此之外，您还可以使用 `max_value` 定义最大成交量 - 这将过滤掉在指定时间范围内成交量高于指定值的交易对。

##### VolumePairList 高级模式

`VolumePairList` 也可以在高级模式下运行，在指定蜡烛图大小的给定时间范围内构建成交量。它利用交易所历史蜡烛图数据，构建典型价格（通过 (开盘+最高+最低)/3 计算）并将典型价格与每个蜡烛图的成交量相乘。总和是给定范围内的 `quoteVolume`。这允许不同的场景，当使用较长范围和较大蜡烛图大小时获得更平滑的成交量，或者当使用短范围和小蜡烛图时相反。

为了方便，可以指定 `lookback_days`，这将意味着将使用 1d 蜡烛图进行回看。在下面的示例中，交易对列表将基于过去 7 天创建：

```json
"pairlists": [
    {
        "method": "VolumePairList",
        "number_assets": 20,
        "sort_key": "quoteVolume",
        "min_value": 0,
        "refresh_period": 86400,
        "lookback_days": 7
    }
],
```

!!! Warning "范围回看和刷新周期"
    当与 `lookback_days` 和 `lookback_timeframe` 结合使用时，`refresh_period` 不能小于蜡烛图大小（以秒为单位）。因为这将导致对交易所 API 的不必要请求。

!!! Warning "使用回看范围时的性能影响"
    如果在第一个位置与回看结合使用，基于范围的成交量计算可能会消耗时间和资源，因为它会下载所有可交易交易对的蜡烛图。因此，强烈建议使用标准方法与 `VolumeFilter` 来缩小交易对列表以进行进一步的范围成交量计算。

??? Tip "不支持的交易所"
    在某些交易所（如 Gemini）上，常规 VolumePairList 不起作用，因为 API 本身不提供 24 小时成交量。这可以通过使用蜡烛图数据来构建成交量来解决。
    要大致模拟 24 小时成交量，您可以使用以下配置。
    请注意，这些交易对列表每天只会刷新一次。

    ```json
    "pairlists": [
        {
            "method": "VolumePairList",
            "number_assets": 20,
            "sort_key": "quoteVolume",
            "min_value": 0,
            "refresh_period": 86400,
            "lookback_days": 1
        }
    ],
    ```

可以使用更复杂的方法，通过使用 `lookback_timeframe` 作为蜡烛图大小和 `lookback_period` 指定蜡烛图数量。此示例将基于 3 天 1 小时蜡烛图的滚动周期构建成交量交易对：

```json
"pairlists": [
    {
        "method": "VolumePairList",
        "number_assets": 20,
        "sort_key": "quoteVolume",
        "min_value": 0,
        "refresh_period": 3600,
        "lookback_timeframe": "1h",
        "lookback_period": 72
    }
],
```

!!! Note
    `VolumePairList` 不支持回测模式。

#### 百分比变化交易对列表

`PercentChangePairList` 根据过去 24 小时或作为高级选项的任何定义时间框架内价格的百分比变化来过滤和排序交易对。这允许交易者专注于经历了显著价格变动（正向或负向）的资产。

**配置选项**

* `number_assets`: 指定基于 24 小时百分比变化选择的顶级交易对数量。
* `min_value`: 设置最小百分比变化阈值。百分比变化低于此值的交易对将被过滤掉。
* `max_value`: 设置最大百分比变化阈值。百分比变化高于此值的交易对将被过滤掉。
* `sort_direction`: 指定基于百分比变化对交易对进行排序的顺序。接受两个值：`asc` 表示升序，`desc` 表示降序。
* `refresh_period`: 定义交易对列表刷新的间隔（以秒为单位）。默认为 1800 秒（30 分钟）。
* `lookback_days`: 回看的天数。当选择 `lookback_days` 时，`lookback_timeframe` 默认为 1 天。
* `lookback_timeframe`: 用于回看期间的时间框架。
* `lookback_period`: 回看的周期数。

当 PercentChangePairList 在其他交易对列表处理器之后使用时，它将对这些处理器的输出进行操作。如果它是领导交易对列表处理器，它将从具有指定基础货币的所有可用市场中选择交易对。

`PercentChangePairList` 使用来自交易所的行情数据，通过 ccxt 库提供：
百分比变化计算为过去 24 小时内价格的变化。

??? Note "不支持的交易所"
    在某些交易所（如 HTX）上，常规 PercentChangePairList 不起作用，因为 API 本身不提供 24 小时价格百分比变化。这可以通过使用蜡烛图数据来计算百分比变化来解决。要大致模拟 24 小时百分比变化，您可以使用以下配置。请注意，这些交易对列表每天只会刷新一次。
    ```json
    "pairlists": [
        {
            "method": "PercentChangePairList",
            "number_assets": 20,
            "min_value": 0,
            "refresh_period": 86400,
            "lookback_days": 1
        }
    ],
    ```

**从行情读取的示例配置**

```json
"pairlists": [
    {
        "method": "PercentChangePairList",
        "number_assets": 15,
        "min_value": -10,
        "max_value": 50
    }
],
```

在此配置中：

1. 基于过去 24 小时内最高价格百分比变化选择前 15 个交易对。
2. 只考虑百分比变化在 -10% 和 50% 之间的交易对。

**从蜡烛图读取的示例配置**

```json
"pairlists": [
    {
        "method": "PercentChangePairList",
        "number_assets": 15,
        "sort_key": "percentage",
        "min_value": 0,
        "refresh_period": 3600,
        "lookback_timeframe": "1h",
        "lookback_period": 72
    }
],
```

此示例通过使用 `lookback_timeframe` 作为蜡烛图大小和 `lookback_period` 指定蜡烛图数量，基于 3 天 1 小时蜡烛图的滚动周期构建百分比变化交易对。

价格百分比变化使用以下公式计算，该公式表示当前蜡烛图收盘价与前一个蜡烛图收盘价之间的百分比差异，由指定的时间框架和回看期间定义：

$$ Percent Change = (\frac{Current Close - Previous Close}{Previous Close}) * 100 $$

!!! Warning "范围回看和刷新周期"
    当与 `lookback_days` 和 `lookback_timeframe` 结合使用时，`refresh_period` 不能小于蜡烛图大小（以秒为单位）。因为这将导致对交易所 API 的不必要请求。

!!! Warning "使用回看范围时的性能影响"
    如果在第一个位置与回看结合使用，基于范围的百分比变化计算可能会消耗时间和资源，因为它会下载所有可交易交易对的蜡烛图。因此，强烈建议使用标准方法与 `PercentChangePairList` 来缩小交易对列表以进行进一步的百分比变化计算。
