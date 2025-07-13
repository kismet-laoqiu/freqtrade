# Webhook 使用

## 配置

通过在配置文件中添加 webhook 部分并将 `webhook.enabled` 设置为 `true` 来启用 webhooks。

示例配置（使用 IFTTT 测试）。

```json
  "webhook": {
        "enabled": true,
        "url": "https://maker.ifttt.com/trigger/<YOUREVENT>/with/key/<YOURKEY>/",
        "entry": {
            "value1": "Buying {pair}",
            "value2": "limit {limit:8f}",
            "value3": "{stake_amount:8f} {stake_currency}"
        },
        "entry_cancel": {
            "value1": "Cancelling Open Buy Order for {pair}",
            "value2": "limit {limit:8f}",
            "value3": "{stake_amount:8f} {stake_currency}"
        },
         "entry_fill": {
            "value1": "Buy Order for {pair} filled",
            "value2": "at {open_rate:8f}",
            "value3": ""
        },
        "exit": {
            "value1": "Exiting {pair}",
            "value2": "limit {limit:8f}",
            "value3": "profit: {profit_amount:8f} {stake_currency} ({profit_ratio})"
        },
        "exit_cancel": {
            "value1": "Cancelling Open Exit Order for {pair}",
            "value2": "limit {limit:8f}",
            "value3": "profit: {profit_amount:8f} {stake_currency} ({profit_ratio})"
        },
        "exit_fill": {
            "value1": "Exit Order for {pair} filled",
            "value2": "at {close_rate:8f}.",
            "value3": ""
        },
        "status": {
            "value1": "Status: {status}",
            "value2": "",
            "value3": ""
        }
    },
```

`webhook.url` 中的 url 应该指向您的 webhook 的正确 url。如果您使用 [IFTTT](https://ifttt.com)（如上面示例所示），请将您的事件和密钥插入到 url 中。

您可以将 POST 正文格式设置为表单编码（默认）、JSON 编码或原始数据。分别使用 `"format": "form"`、`"format": "json"` 或 `"format": "raw"`。Mattermost Cloud 集成的示例配置：

```json
  "webhook": {
        "enabled": true,
        "url": "https://<YOURSUBDOMAIN>.cloud.mattermost.com/hooks/<YOURHOOK>",
        "format": "json",
        "status": {
            "text": "Status: {status}"
        }
    },
```

结果将是一个 POST 请求，例如 `{"text":"Status: running"}` 正文和 `Content-Type: application/json` 标头，这会在 Mattermost 频道中产生 `Status: running` 消息。

当使用表单编码或 JSON 编码配置时，您可以配置任意数量的有效负载值，键和值都将在 POST 请求中输出。但是，当使用原始数据格式时，您只能配置一个值，并且它**必须**命名为 `"data"`。在这种情况下，数据键不会在 POST 请求中输出，只有值。例如：

```json
  "webhook": {
        "enabled": true,
        "url": "https://<YOURHOOKURL>",
        "format": "raw",
        "webhookstatus": {
            "data": "Status: {status}"
        }
    },
```

结果将是一个 POST 请求，例如 `Status: running` 正文和 `Content-Type: text/plain` 标头。

## 其他配置

`webhook.retries` 参数可以设置为 webhook 请求在不成功时应尝试的最大重试次数（即 HTTP 响应状态不是 200）。默认情况下，这设置为 `0`，即禁用。可以设置额外的 `webhook.retry_delay` 参数来指定重试尝试之间的时间（以秒为单位）。默认情况下，这设置为 `0.1`（即 100ms）。请注意，如果 webhook 存在连接问题，增加重试次数或重试延迟可能会减慢交易者的速度。
您还可以指定 `webhook.timeout` - 它定义机器人将等待多长时间，直到它假设另一个主机无响应（默认为 10s）。

重试的示例配置：

```json
  "webhook": {
        "enabled": true,
        "url": "https://<YOURHOOKURL>",
        "timeout": 10,
        "retries": 3,
        "retry_delay": 0.2,
        "status": {
            "status": "Status: {status}"
        }
    },
```

## 可用变量

以下变量可在 webhook 消息中使用：

### 通用变量
- `{exchange}` - 交易所名称
- `{pair}` - 交易对
- `{base_currency}` - 基础货币
- `{quote_currency}` - 报价货币
- `{stake_currency}` - 投注货币
- `{stake_amount}` - 投注金额
- `{fiat_currency}` - 法币货币
- `{order_type}` - 订单类型
- `{limit}` - 限价
- `{amount}` - 数量
- `{open_rate}` - 开盘价
- `{close_rate}` - 收盘价

### 入场相关变量
- `{enter_tag}` - 入场标签
- `{side}` - 交易方向（long/short）

### 出场相关变量
- `{exit_reason}` - 出场原因
- `{profit_amount}` - 利润金额
- `{profit_ratio}` - 利润比率
- `{profit_percent}` - 利润百分比

### 状态变量
- `{status}` - 机器人状态
- `{current_rate}` - 当前价格

## 支持的 Webhook 事件

Freqtrade 支持以下 webhook 事件：

- `entry` - 入场订单下达时
- `entry_fill` - 入场订单成交时
- `entry_cancel` - 入场订单取消时
- `exit` - 出场订单下达时
- `exit_fill` - 出场订单成交时
- `exit_cancel` - 出场订单取消时
- `status` - 机器人状态变化时
- `startup` - 机器人启动时
- `protection_trigger` - 保护机制触发时
- `protection_trigger_global` - 全局保护机制触发时
- `strategy_msg` - 策略发送消息时

## 安全考虑

使用 webhooks 时请注意以下安全事项：

1. **URL 安全**: 确保您的 webhook URL 是安全的，不要在公共场所暴露
2. **数据敏感性**: 避免在 webhook 消息中包含敏感信息
3. **网络安全**: 使用 HTTPS 而不是 HTTP
4. **访问控制**: 限制对 webhook 端点的访问

## 故障排除

### 常见问题

1. **Webhook 不工作**
   - 检查 URL 是否正确
   - 验证网络连接
   - 查看日志文件中的错误信息

2. **消息格式错误**
   - 验证 JSON 格式是否正确
   - 检查变量名称是否正确

3. **超时问题**
   - 增加 `timeout` 值
   - 检查目标服务器的响应时间

### 调试技巧

- 使用 `webhook.retries` 和 `webhook.retry_delay` 处理临时网络问题
- 在日志中启用详细模式以查看 webhook 请求详情
- 使用测试工具（如 webhook.site）验证 webhook 配置

可以为不同的事件配置不同的有效负载。并非所有字段都是必需的，但您应该至少配置其中一个字典，否则永远不会调用 webhook。

## 自定义消息

可以通过策略中的 `self.dp.send_msg()` 函数向 Webhook 端点发送自定义消息。要启用此功能，请将 `allow_custom_messages` 选项设置为 `true`：

```json
  "webhook": {
        "enabled": true,
        "url": "https://<YOURHOOKURL>",
        "allow_custom_messages": true,
        "strategy_msg": {
            "status": "策略消息: {msg}"
        }
    },
```

## Webhook 消息类型

### 入场 (Entry)

当机器人执行多头/空头时，`webhook.entry` 中的字段会被填充。参数使用 string.format 填充。
可能的参数包括：

* `trade_id` - 交易 ID
* `exchange` - 交易所
* `pair` - 交易对
* `direction` - 方向
* `leverage` - 杠杆
* `open_rate` - 开仓价格
* `amount` - 数量
* `open_date` - 开仓日期
* `stake_amount` - 质押金额
* `stake_currency` - 质押货币
* `base_currency` - 基础货币
* `quote_currency` - 报价货币
* `fiat_currency` - 法币货币
* `order_type` - 订单类型
* `current_rate` - 当前价格
* `enter_tag` - 入场标签

### 入场取消 (Entry Cancel)

当机器人取消多头/空头订单时，`webhook.entry_cancel` 中的字段会被填充。参数使用 string.format 填充。
可能的参数包括：

* `trade_id` - 交易 ID
* `exchange` - 交易所
* `pair` - 交易对
* `direction` - 方向
* `leverage` - 杠杆
* `limit` - 限价
* `amount` - 数量
* `open_date` - 开仓日期
* `stake_amount` - 质押金额
* `stake_currency` - 质押货币
* `base_currency` - 基础货币
* `quote_currency` - 报价货币
* `fiat_currency` - 法币货币
* `order_type` - 订单类型
* `current_rate` - 当前价格
* `enter_tag` - 入场标签

### 入场成交 (Entry Fill)

当机器人成交多头/空头订单时，`webhook.entry_fill` 中的字段会被填充。参数使用 string.format 填充。
可能的参数包括：

* `trade_id` - 交易 ID
* `exchange` - 交易所
* `pair` - 交易对
* `direction` - 方向
* `leverage` - 杠杆
* `open_rate` - 开仓价格
* `amount` - 数量
* `open_date` - 开仓日期
* `stake_amount` - 质押金额
* `stake_currency` - 质押货币
* `base_currency` - 基础货币
* `quote_currency` - 报价货币
* `fiat_currency` - 法币货币
* `order_type` - 订单类型
* `current_rate` - 当前价格
* `enter_tag` - 入场标签

### 出场 (Exit)

当机器人退出交易时，`webhook.exit` 中的字段会被填充。参数使用 string.format 填充。
可能的参数包括：

* `trade_id` - 交易 ID
* `exchange` - 交易所
* `pair` - 交易对
* `direction` - 方向
* `leverage` - 杠杆
* `gain` - 收益
* `limit` - 限价
* `amount` - 数量
* `open_rate` - 开仓价格
* `profit_amount` - 利润金额
* `profit_ratio` - 利润比率
* `stake_currency` - 质押货币
* `base_currency` - 基础货币
* `quote_currency` - 报价货币
* `fiat_currency` - 法币货币
* `exit_reason` - 出场原因
* `order_type` - 订单类型
* `open_date` - 开仓日期
* `close_date` - 平仓日期

### 出场成交 (Exit Fill)

当机器人成交出场订单（关闭交易）时，`webhook.exit_fill` 中的字段会被填充。参数使用 string.format 填充。
可能的参数包括：

* `trade_id` - 交易 ID
* `exchange` - 交易所
* `pair` - 交易对
* `direction` - 方向
* `leverage` - 杠杆
* `gain` - 收益
* `close_rate` - 平仓价格
* `amount` - 数量
* `open_rate` - 开仓价格
* `current_rate` - 当前价格
* `profit_amount` - 利润金额
* `profit_ratio` - 利润比率
* `stake_currency` - 质押货币
* `base_currency` - 基础货币
* `quote_currency` - 报价货币
* `fiat_currency` - 法币货币
* `exit_reason` - 出场原因
* `order_type` - 订单类型
* `open_date` - 开仓日期
* `close_date` - 平仓日期

### 出场取消 (Exit Cancel)

当机器人取消出场订单时，`webhook.exit_cancel` 中的字段会被填充。参数使用 string.format 填充。
可能的参数包括：

* `trade_id` - 交易 ID
* `exchange` - 交易所
* `pair` - 交易对
* `direction` - 方向
* `leverage` - 杠杆
* `gain` - 收益
* `limit` - 限价
* `amount` - 数量
* `open_rate` - 开仓价格
* `current_rate` - 当前价格
* `profit_amount` - 利润金额
* `profit_ratio` - 利润比率
* `stake_currency` - 质押货币
* `base_currency` - 基础货币
* `quote_currency` - 报价货币
* `fiat_currency` - 法币货币
* `exit_reason` - 出场原因
* `order_type` - 订单类型
* `open_date` - 开仓日期
* `close_date` - 平仓日期

### 状态 (Status)

`webhook.status` 中的字段用于常规状态消息（已启动/已停止/...）。参数使用 string.format 填充。

这里唯一可能的值是 `{status}`。

## Discord

Discord 有一种特殊形式的 webhook 可用。
您可以按如下方式配置：

```json
"discord": {
    "enabled": true,
    "webhook_url": "https://discord.com/api/webhooks/<Your webhook URL ...>",
    "exit_fill": [
        {"交易 ID": "{trade_id}"},
        {"交易所": "{exchange}"},
        {"交易对": "{pair}"},
        {"方向": "{direction}"},
        {"开仓价格": "{open_rate}"},
        {"平仓价格": "{close_rate}"},
        {"数量": "{amount}"},
        {"开仓日期": "{open_date:%Y-%m-%d %H:%M:%S}"},
        {"平仓日期": "{close_date:%Y-%m-%d %H:%M:%S}"},
        {"利润": "{profit_amount} {stake_currency}"},
        {"盈利率": "{profit_ratio:.2%}"},
        {"入场标签": "{enter_tag}"},
        {"出场原因": "{exit_reason}"},
        {"策略": "{strategy}"},
        {"时间框架": "{timeframe}"},
    ],
    "entry_fill": [
        {"交易 ID": "{trade_id}"},
        {"交易所": "{exchange}"},
        {"交易对": "{pair}"},
        {"方向": "{direction}"},
        {"开仓价格": "{open_rate}"},
        {"数量": "{amount}"},
        {"开仓日期": "{open_date:%Y-%m-%d %H:%M:%S}"},
        {"入场标签": "{enter_tag}"},
        {"策略": "{strategy} {timeframe}"},
    ]
}
```

上述配置代表默认设置（`exit_fill` 和 `entry_fill` 是可选的，将默认为上述配置） - 显然可以进行修改。
要禁用两个默认值中的任何一个（`entry_fill` / `exit_fill`），您可以为它们分配一个空数组（`exit_fill: []`）。

可用字段对应于 webhook 的字段，并在相应的 webhook 部分中记录。

默认情况下，通知将如下所示。

![discord-notification](assets/discord_notification.png)

可以通过 dataprovider.send_msg() 函数从策略向 Discord 端点发送自定义消息。要启用此功能，请将 `allow_custom_messages` 选项设置为 `true`：

```json
  "discord": {
        "enabled": true,
        "webhook_url": "https://discord.com/api/webhooks/<Your webhook URL ...>",
        "allow_custom_messages": true,
    },
```

## 高级配置示例

### 多个 Webhook URL

您可以配置多个 webhook URL 以同时发送到多个服务：

```json
{
    "webhook": {
        "enabled": true,
        "url": [
            "https://discord.com/api/webhooks/...",
            "https://hooks.slack.com/services/...",
            "https://maker.ifttt.com/trigger/..."
        ],
        "format": "json",
        "entry": {
            "message": "买入 {pair} @ {open_rate}"
        }
    }
}
```

### 条件性 Webhook

在策略中使用条件逻辑控制 webhook 发送：

```python
class MyStrategy(IStrategy):

    def confirm_trade_entry(self, pair: str, order_type: str, amount: float, rate: float,
                           time_in_force: str, current_time: datetime, entry_tag: str | None,
                           side: str, **kwargs) -> bool:

        # 只为重要交易发送 webhook
        if amount > 1000:  # 大额交易
            self.dp.send_msg(f"大额交易警告: {pair} - {amount} USDT")

        return True
```

### 错误处理

配置 webhook 错误处理和重试：

```json
{
    "webhook": {
        "enabled": true,
        "url": "https://your-webhook.com",
        "timeout": 30,
        "retries": 5,
        "retry_delay": 1.0,
        "entry": {
            "message": "入场: {pair}"
        }
    }
}
```

## 最佳实践

1. **测试配置**: 在生产环境中使用前，先在测试环境中验证 webhook 配置
2. **监控性能**: 监控 webhook 响应时间，避免影响交易性能
3. **安全考虑**: 使用 HTTPS，保护 webhook URL，避免泄露敏感信息
4. **错误处理**: 配置适当的重试和超时设置
5. **日志记录**: 启用详细日志以便调试问题

通过正确配置 webhook，您可以将 Freqtrade 与各种外部服务集成，实现实时通知、自动化工作流程和高级监控功能。
