# 交易所特定说明

本页面结合了特定于交易所的常见问题和信息，这些信息很可能不适用于其他交易所。

## 交易所配置

Freqtrade 基于 [CCXT 库](https://github.com/ccxt/ccxt)，支持超过 100 个加密货币交易所市场和交易 API。完整的最新列表可以在 [CCXT 仓库主页](https://github.com/ccxt/ccxt/tree/master/python) 中找到。
但是，机器人只由开发团队在少数几个交易所进行了测试。
这些交易所的当前列表可以在本文档的"主页"部分找到。

欢迎测试其他交易所并提交您的反馈或 PR 来改进机器人或确认完美运行的交易所。

一些交易所需要特殊配置，可以在下面找到。

### 示例交易所配置

"binance" 的交易所配置如下所示：

```json
"exchange": {
    "name": "binance",
    "key": "your_exchange_key",
    "secret": "your_exchange_secret",
    "ccxt_config": {},
    "ccxt_async_config": {},
    // ...
```

### 设置速率限制

通常，CCXT 设置的速率限制是可靠的并且工作良好。
如果遇到与速率限制相关的问题（通常是日志中的 DDOS 异常），很容易将 rateLimit 设置更改为其他值。

```json
"exchange": {
    "name": "kraken",
    "key": "your_exchange_key",
    "secret": "your_exchange_secret",
    "ccxt_config": {"enableRateLimit": true},
    "ccxt_async_config": {
        "enableRateLimit": true,
        "rateLimit": 3100
    },
```

此配置启用 kraken，以及速率限制以避免被交易所禁止。
`"rateLimit": 3100` 定义每次调用之间的 3.1 秒等待事件。这也可以通过将 `"enableRateLimit"` 设置为 false 来完全禁用。

!!! Note
    速率限制的最佳设置取决于交易所和白名单的大小，因此理想参数会因许多其他设置而异。
    我们尽量在可能的情况下为每个交易所提供合理的默认值，如果您遇到禁令，请确保启用 `"enableRateLimit"` 并逐步增加 `"rateLimit"` 参数。

## Binance

!!! Warning "服务器位置和地理 IP 限制"
    请注意，Binance 对服务器国家/地区的 API 访问有限制。当前被阻止的非详尽国家/地区包括加拿大、马来西亚、荷兰和美国。请访问 [binance 条款 > b. 资格](https://www.binance.com/en/terms) 查找最新列表。

Binance 支持 [time_in_force](configuration.md#understand-order_time_in_force)。

!!! Tip "交易所止损"
    Binance 支持 `stoploss_on_exchange` 并使用 `stop-loss-limit` 订单。它提供了很大的优势，因此我们建议通过在交易所启用止损来从中受益。
    在期货上，Binance 支持 `stop-limit` 和 `stop-market` 订单。您可以在 `order_types.stoploss` 配置设置中使用 `"limit"` 或 `"market"` 来决定使用哪种类型。

### Binance 黑名单建议

对于 Binance，建议将 `"BNB/<STAKE>"` 添加到您的黑名单中以避免问题，除非您愿意在账户上维护足够的额外 `BNB`，或者除非您愿意禁用使用 `BNB` 支付费用。
Binance 账户可能使用 `BNB` 支付费用，如果交易恰好在 `BNB` 上，进一步的交易可能会消耗这个头寸，使初始 BNB 交易无法出售，因为预期的金额不再存在。

如果没有足够的 `BNB` 来支付交易费用，那么费用将不会由 `BNB` 支付，也不会发生费用减免。Freqtrade 永远不会购买 BNB 来支付费用。为此需要手动购买和监控 BNB。

### Binance 站点

Binance 已分为 2 个，用户必须为其交易所使用正确的 ccxt 交易所 ID，否则 API 密钥不会被识别。

* [binance.com](https://www.binance.com/) - 国际用户。使用交易所 ID：`binance`。
* [binance.us](https://www.binance.us/) - 美国用户。使用交易所 ID：`binanceus`。

### Binance RSA 密钥

Freqtrade 支持 binance RSA API 密钥。

我们建议将它们用作环境变量。

``` bash
export FREQTRADE__EXCHANGE__SECRET="$(cat ./rsa_binance.private)"
```

但是，它们也可以通过配置文件进行配置。由于 json 不支持多行字符串，您必须将所有换行符替换为 `\n` 以获得有效的 json 文件。

``` json
// ...
 "key": "<someapikey>",
 "secret": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBABACAFQA<...>s8KX8=\n-----END PRIVATE KEY-----"
// ...
```

### Binance 期货

Binance 有特定的（不幸的是复杂的）[期货交易量化规则](https://www.binance.com/en/support/faq/4f462ebe6ff445d4a170be7d9e897272)，需要遵循，其中禁止过低的质押金额（以及其他）用于过多的订单。
违反这些规则将导致交易限制。

在 Binance 期货市场交易时，必须使用订单簿，因为期货没有价格行情数据。

```json
"exchange": {
    "name": "binance",
    "ccxt_config": {
        "options": {
            "defaultType": "future"
        }
    },
    // ...
}
```

!!! Warning "Binance 期货的质押货币"
    Binance 期货账户的质押货币必须是 `USDT`。
    这是因为 Binance 期货使用 USDT 作为保证金货币。

```json
"stake_currency": "USDT",
```

`stake_currency` 设置定义了机器人将运行的市场。这个选择实际上是任意的。

在交易所上，您必须使用"多资产模式" - 并且"持仓模式设置为"单向模式"。
Freqtrade 将在启动时检查这些设置，但不会尝试更改它们。

## Bingx

BingX 支持 [time_in_force](configuration.md#understand-order_time_in_force)，设置为 "GTC"（有效直到取消）、"IOC"（立即或取消）和 "PO"（仅发布）设置。

!!! Tip "交易所止损"
    Bingx 支持 `stoploss_on_exchange` 并可以使用止损限价和止损市价订单。它提供了很大的优势，因此我们建议通过在交易所启用止损来从中受益。

## Kraken

Kraken 支持 [time_in_force](configuration.md#understand-order_time_in_force)，设置为 "GTC"（有效直到取消）、"IOC"（立即或取消）和 "PO"（仅发布）设置。

!!! Tip "交易所止损"
    Kraken 支持 `stoploss_on_exchange` 并可以使用止损市价和止损限价订单。它提供了很大的优势，因此我们建议从中受益。
    您可以在 `order_types.stoploss` 配置设置中使用 `"limit"` 或 `"market"` 来决定使用哪种类型。

### Kraken 历史数据

Kraken API 仅提供 720 个历史蜡烛图，这对于 Freqtrade 模拟运行和实盘交易模式是足够的，但对于回测是一个问题。
要为 Kraken 交易所下载数据，使用 `--dl-trades` 是强制性的，否则机器人将一遍又一遍地下载相同的 720 个蜡烛图，您将没有足够的回测数据。

为了加快下载速度，您可以下载 Kraken 提供的[交易 zip 文件](https://support.kraken.com/hc/en-us/articles/360047543791-Downloadable-historical-market-data-time-and-sales-)。
这些通常每季度更新一次。Freqtrade 期望这些文件放置在 `user_data/data/kraken/trades_csv` 中。

```bash
# 下载 Kraken 历史数据
freqtrade download-data --exchange kraken --pairs BTC/USD ETH/USD --days 365 --dl-trades
```

### Kraken 费用

Kraken 有一个复杂的费用结构，取决于您的交易量。请参阅 [Kraken 费用页面](https://www.kraken.com/features/fee-schedule) 了解详细信息。

## Kucoin

Kucoin 需要为每个 API 密钥提供密码短语，因此您需要将此密钥添加到配置中，以便您的交易所部分如下所示：

```json
"exchange": {
    "name": "kucoin",
    "key": "your_exchange_key",
    "secret": "your_exchange_secret",
    "password": "your_exchange_api_key_password",
    // ...
}
```

Kucoin 支持 [time_in_force](configuration.md#understand-order_time_in_force)。

!!! Tip "交易所止损"
    Kucoin 支持 `stoploss_on_exchange` 并可以使用止损市价和止损限价订单。它提供了很大的优势，因此我们建议从中受益。
    您可以在 `order_types.stoploss` 配置设置中使用 `"limit"` 或 `"market"` 来决定应该使用哪种类型的止损。

### Kucoin 黑名单

对于 Kucoin，建议将 `"KCS/<STAKE>"` 添加到您的黑名单中以避免问题，除非您愿意在账户上维护足够的额外 `KCS`，或者除非您愿意禁用使用 `KCS` 支付费用。
Kucoin 账户可能使用 `KCS` 支付费用，如果交易恰好在 `KCS` 上，进一步的交易可能会消耗这个头寸，使初始 `KCS` 交易无法出售，因为预期的金额不再存在。

## HTX

!!! Tip "交易所止损"
    HTX 支持 `stoploss_on_exchange` 并使用 `stop-limit` 订单。它提供了很大的优势，因此我们建议通过在交易所启用止损来从中受益。

## OKX

OKX 需要为每个 API 密钥提供密码短语，因此您需要将此密钥添加到配置中，以便您的交易所部分如下所示：

```json
"exchange": {
    "name": "okx",
    "key": "your_exchange_key",
    "secret": "your_exchange_secret",
    "password": "your_exchange_api_key_password",
    // ...
}
```

如果您在主机 my.okx.com（OKX EAA）上注册了 OKX - 您需要使用 `"myokx"` 作为交易所名称。
使用错误的交易所将导致错误"OKX Error 50119: API key doesn't exist" - 因为这两个是独立的实体。

!!! Warning
    OKX 每次 API 调用仅提供 100 个蜡烛图。因此，策略在回测模式下只有相当少量的可用数据。

!!! Warning "期货"
    OKX 期货有"持仓模式"的概念 - 可以是"买入/卖出"或多头/空头（对冲模式）。
    Freqtrade 支持两种模式（我们建议使用买入/卖出模式） - 但不支持在交易中途更改模式，这将导致异常和无法下单。
    OKX 还仅提供过去约 3 个月的 MARK 蜡烛图。因此，在该日期之前回测期货将导致轻微偏差，因为没有此数据无法正确计算资金费用。

## Gate.io

!!! Tip "交易所止损"
    Gate.io 支持 `stoploss_on_exchange` 并使用 `stop-loss-limit` 订单。它提供了很大的优势，因此我们建议通过在交易所启用止损来从中受益。

### Gate.io API 权限

Gate.io 的 API 密钥需要以下权限：

* 现货交易
* 期货交易（如果您计划交易期货）
* 钱包（用于余额查询）

没有这些权限，机器人将无法正确启动并显示"权限缺失"等错误。

## Bybit

Bybit 上的期货交易目前支持 USDT 市场，并将使用隔离期货模式。

在启动时，freqtrade 将为整个（子）账户设置持仓模式为"单向模式"。这避免了一遍又一遍地进行此调用（减慢机器人操作），但意味着对此设置的更改可能导致异常和错误。

由于 bybit 不提供资金费率历史，模拟运行计算也用于实盘交易。

实盘期货交易的 API 密钥必须具有以下权限：

* 读写
* 合约 - 订单
* 合约 - 持仓

## Hyperliquid

Hyperliquid 是一个去中心化交易所（DEX），需要特殊的配置。

!!! Warning "私钥安全"
    Hyperliquid 使用私钥而不是 API 密钥。请确保您的私钥安全，并且永远不要与任何人分享。

### Hyperliquid 配置

```json
"exchange": {
    "name": "hyperliquid",
    "key": "",
    "secret": "your_private_key_here",
    // ...
}
```

### Hyperliquid 最佳实践

!!! Info "一些一般最佳实践（非详尽）"
    * 注意供应链攻击，如 pip 包中毒等。每当您使用私钥时，请确保您的环境是安全的。
    * 不要使用您的实际钱包私钥进行交易。使用 Hyperliquid [API 生成器](https://app.hyperliquid.xyz/API) 创建单独的 API 钱包。
    * 不要将您的实际钱包私钥存储在用于 freqtrade 的服务器上。请改用 API 钱包私钥。此密钥不允许提取，仅允许交易。
    * 始终保持您的助记词和私钥私密。
    * 不要使用与初始化硬件钱包时必须备份的相同助记词，使用相同的助记词基本上会删除硬件钱包的安全性。

## Bitvavo

Bitvavo 需要 `operatorId` 配置参数。

```json
"exchange": {
    "name": "bitvavo",
    "key": "your_exchange_key",
    "secret": "your_exchange_secret",
    "ccxt_config": {
        "operatorId": "your_operator_id"
    },
    // ...
}
```

Bitvavo 期望 `operatorId` 是一个整数。

## 所有交易所

如果您遇到 Nonce 的持续错误（如 `InvalidNonce`），最好重新生成 API 密钥。重置 Nonce 很困难，通常重新生成 API 密钥更容易。

## 其他交易所的随机说明

* The Ocean（交易所 ID：`theocean`）交易所使用 Web3 功能，需要安装 `web3` python 包：

```shell
pip3 install web3
```

### 获取最新价格 / 不完整蜡烛图

大多数交易所通过其 OHLCV/klines API 接口返回当前不完整的蜡烛图。
默认情况下，Freqtrade 假设从交易所获取不完整的蜡烛图，并删除最后一个蜡烛图，假设它是不完整的蜡烛图。

某些交易所提供不同的行为（返回仅完整的蜡烛图），可以通过在交易所配置中设置 `"ohlcv_partial_candle"` 为 `false` 来配置。

```json
"exchange": {
    "name": "binance",
    "ohlcv_partial_candle": false,
    // ...
}
```

### 覆盖交易所功能

某些交易所功能可以通过在交易所配置中设置 `_ft_has_params` 来覆盖。

例如，要使用 Kraken 测试订单类型 `FOK`，并将蜡烛图限制修改为 200（因此每次 API 调用只获得 200 个蜡烛图）：

```json
"exchange": {
    "name": "kraken",
    "_ft_has_params": {
        "order_time_in_force": ["GTC", "FOK"],
        "ohlcv_candle_limit": 200
        }
    //...
}
```

!!! Warning
    请确保在修改这些设置之前完全了解其影响。

### 常见交易所问题

#### 连接问题

如果您遇到连接问题：

1. 检查您的网络连接
2. 验证 API 密钥和权限
3. 检查交易所是否有维护或停机
4. 考虑使用 VPN 如果有地理限制

#### API 限制

大多数交易所都有 API 限制：

1. 启用速率限制：`"enableRateLimit": true`
2. 调整速率限制值：`"rateLimit": 1000`
3. 减少并发请求
4. 使用较少的交易对

#### 权限错误

确保您的 API 密钥具有必要的权限：

* 现货交易
* 期货交易（如果适用）
* 读取账户信息
* 读取交易历史

### 交易所特定配置示例

#### Binance 完整配置

```json
"exchange": {
    "name": "binance",
    "key": "your_api_key",
    "secret": "your_secret_key",
    "ccxt_config": {
        "enableRateLimit": true,
        "options": {
            "defaultType": "spot"  // 或 "future" 用于期货
        }
    },
    "ccxt_async_config": {
        "enableRateLimit": true,
        "rateLimit": 200
    }
}
```

#### Kraken 完整配置

```json
"exchange": {
    "name": "kraken",
    "key": "your_api_key",
    "secret": "your_secret_key",
    "ccxt_config": {
        "enableRateLimit": true
    },
    "ccxt_async_config": {
        "enableRateLimit": true,
        "rateLimit": 3100
    }
}
```

#### OKX 完整配置

```json
"exchange": {
    "name": "okx",
    "key": "your_api_key",
    "secret": "your_secret_key",
    "password": "your_passphrase",
    "ccxt_config": {
        "enableRateLimit": true,
        "options": {
            "defaultType": "spot"  // 或 "swap" 用于期货
        }
    },
    "ccxt_async_config": {
        "enableRateLimit": true,
        "rateLimit": 100
    }
}
```

### 测试交易所连接

在开始交易之前，建议测试您的交易所连接：

```bash
# 测试连接
freqtrade test-pairlist --config config.json

# 下载一些数据进行测试
freqtrade download-data --config config.json --days 1

# 运行模拟交易进行测试
freqtrade trade --config config.json --dry-run
```

### 故障排除

如果遇到问题：

1. 检查日志文件中的详细错误信息
2. 验证 API 密钥和权限
3. 检查网络连接和防火墙设置
4. 查看交易所的状态页面
5. 参考 Freqtrade 社区论坛和文档

记住，每个交易所都有其独特的特性和限制。在开始实盘交易之前，始终先进行彻底的测试。
