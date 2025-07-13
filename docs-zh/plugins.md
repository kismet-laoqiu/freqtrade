# 插件

## 交易对列表和交易对列表处理器

交易对列表处理器定义机器人应该交易的交易对列表（交易对列表）。它们在配置设置的 `pairlists` 部分中配置。

在您的配置中，您可以使用静态交易对列表（由 [`StaticPairList`](#静态交易对列表) 交易对列表处理器定义）和动态交易对列表（由 [`VolumePairList`](#成交量交易对列表) 和 [`PercentChangePairList`](#百分比变化交易对列表) 交易对列表处理器定义）。

此外，[`AgeFilter`](#agefilter)、[`PrecisionFilter`](#precisionfilter)、[`PriceFilter`](#pricefilter)、[`ShuffleFilter`](#shufflefilter)、[`SpreadFilter`](#spreadfilter) 和 [`VolatilityFilter`](#volatilityfilter) 作为交易对列表过滤器，删除某些交易对和/或移动它们在交易对列表中的位置。

如果使用多个交易对列表处理器，它们会被链接，所有交易对列表处理器的组合形成机器人用于交易和回测的结果交易对列表。交易对列表处理器按配置的顺序执行。您可以定义 `StaticPairList`、`VolumePairList`、`ProducerPairList`、`RemotePairList`、`MarketCapPairList` 或 `PercentChangePairList` 作为起始交易对列表处理器。

非活跃市场总是从结果交易对列表中删除。明确列入黑名单的交易对（`pair_blacklist` 配置设置中的那些）也总是从结果交易对列表中删除。

### 交易对黑名单

交易对黑名单（通过配置中的 `exchange.pair_blacklist` 配置）禁止某些交易对进行交易。
这可以简单到排除 `DOGE/BTC` - 这将删除确切的这个交易对。

交易对黑名单也支持通配符（正则表达式样式） - 所以 `BNB/.*` 将排除所有以 BNB 开头的交易对。
您也可以使用类似 `.*DOWN/BTC` 或 `.*UP/BTC` 来排除杠杆代币（检查您交易所的交易对命名约定！）

### 可用的交易对列表处理器

* [`StaticPairList`](#静态交易对列表)（默认，如果没有不同配置）
* [`VolumePairList`](#成交量交易对列表)
* [`PercentChangePairList`](#百分比变化交易对列表)
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
    交易对列表配置可能很难正确设置。最好使用 [`test-pairlist`](utils.md#test-pairlist) 实用工具子命令快速测试您的配置。

#### 静态交易对列表

默认情况下，使用 `StaticPairList` 方法，它使用配置中静态定义的交易对白名单。交易对列表也支持通配符（正则表达式样式） - 所以 `.*/BTC` 将包括所有以 BTC 作为基础货币的交易对。

它使用 `exchange.pair_whitelist` 和 `exchange.pair_blacklist` 的配置，在下面的示例中，将交易 BTC/USDT 和 ETH/USDT - 并将阻止 BNB/USDT 交易。

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
这对于回测过期交易对（如季度现货市场）很有用。

当在"后续"位置使用时（例如在 VolumePairlist 之后），`'pair_whitelist'` 中的所有交易对将被添加到交易对列表的末尾。

#### 成交量交易对列表

`VolumePairList` 通过交易量对交易对进行排序/过滤。它根据 `sort_key`（只能是 `quoteVolume`）选择 `number_assets` 个顶级交易对。

当在交易对列表处理器链中的非领先位置使用时（在 StaticPairList 和其他交易对列表过滤器之后），`VolumePairList` 考虑之前交易对列表处理器的输出，通过交易量添加其对交易对的排序/选择。

当在交易对列表处理器链的领先位置使用时，`pair_whitelist` 配置设置被忽略。相反，`VolumePairList` 从交易所上所有具有匹配基础货币的可用市场中选择顶级资产。

`refresh_period` 设置允许定义交易对列表刷新的周期（以秒为单位）。默认为 1800 秒（30 分钟）。
`VolumePairList` 上的交易对列表缓存（`refresh_period`）仅适用于生成交易对列表。
过滤实例（不在列表的第一个位置）不会应用任何缓存（除了在高级模式下缓存蜡烛图持续时间的蜡烛图）并且总是使用最新数据。

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
]
```

!!! Note "关于成交量"
    `VolumePairList` 使用滚动的 24 小时成交量。因此，在一天中的不同时间运行可能会产生不同的结果。

## 保护机制

保护机制是一种风险管理功能，可以在检测到某些市场条件时暂停交易。

保护机制在配置的 `protections` 部分中定义，并且可以基于以下条件：

* 最大回撤
* 止损计数
* 低利润对
* 冷却期

### 可用的保护机制

* [`StoplossGuard`](#stoplossguard) - 在连续止损后停止交易
* [`MaxDrawdown`](#maxdrawdown) - 在达到最大回撤时停止交易
* [`LowProfitPairs`](#lowprofitpairs) - 暂停表现不佳的交易对
* [`CooldownPeriod`](#cooldownperiod) - 在交易后强制冷却期

### StoplossGuard

在指定时间内发生一定数量的止损后停止交易。

```json
"protections": [
    {
        "method": "StoplossGuard",
        "lookback_period_candles": 60,
        "trade_limit": 4,
        "stop_duration_candles": 60,
        "only_per_pair": false
    }
]
```

### MaxDrawdown

当达到最大回撤百分比时停止交易。

```json
"protections": [
    {
        "method": "MaxDrawdown",
        "lookback_period_candles": 200,
        "trade_limit": 20,
        "stop_duration_candles": 40,
        "max_allowed_drawdown": 0.2
    }
]
```

### LowProfitPairs

暂停在指定期间内利润低于阈值的交易对。

```json
"protections": [
    {
        "method": "LowProfitPairs",
        "lookback_period_candles": 60,
        "trade_limit": 2,
        "stop_duration_candles": 60,
        "required_profit": 0.02
    }
]
```

### CooldownPeriod

在每次交易后强制冷却期。

```json
"protections": [
    {
        "method": "CooldownPeriod",
        "stop_duration_candles": 5
    }
]
```

!!! Note "保护机制的使用"
    保护机制应该谨慎使用，因为它们可能会阻止机器人在有利的市场条件下进行交易。建议在回测中彻底测试保护设置。

### 完整的交易对列表配置示例

以下是一个完整的交易对列表配置示例，展示了如何组合多个处理器和过滤器：

```json
"pairlists": [
    {
        "method": "VolumePairList",
        "number_assets": 20,
        "sort_key": "quoteVolume"
    },
    {"method": "AgeFilter", "min_days_listed": 10},
    {"method": "PrecisionFilter"},
    {"method": "PriceFilter", "low_price_ratio": 0.01},
    {"method": "SpreadFilter", "max_spread_ratio": 0.005},
    {
        "method": "RangeStabilityFilter",
        "lookback_days": 10,
        "min_rate_of_change": 0.01,
        "refresh_period": 86400
    },
    {
        "method": "VolatilityFilter",
        "lookback_days": 10,
        "min_volatility": 0.05,
        "max_volatility": 0.50,
        "refresh_period": 86400
    },
    {"method": "ShuffleFilter", "seed": 42}
]
```

这个配置将：

1. 选择前20个按成交量排序的交易对
2. 过滤掉上市少于10天的交易对
3. 移除精度不符合要求的交易对
4. 过滤掉价格过低的交易对
5. 移除价差过大的交易对
6. 过滤掉价格范围不稳定的交易对
7. 移除波动性过高或过低的交易对
8. 随机打乱最终列表

### 最佳实践

1. **测试配置**：使用 `freqtrade test-pairlist` 命令测试您的配置
2. **合理排序**：将生成器（如 VolumePairList）放在前面，过滤器放在后面
3. **性能考虑**：避免过于频繁的刷新，特别是对于计算密集型的过滤器
4. **监控结果**：定期检查生成的交易对列表是否符合预期
5. **回测验证**：在实盘使用前，先在回测中验证交易对列表的效果

通过合理配置交易对列表和保护机制，您可以创建一个既灵活又安全的交易环境。
