# Telegram 使用

## 设置您的 Telegram 机器人

下面我们解释如何创建您的 Telegram 机器人，以及如何获取您的 Telegram 用户 ID。

### 1. 创建您的 Telegram 机器人

与 [Telegram BotFather](https://telegram.me/BotFather) 开始聊天

发送消息 `/newbot`。

*BotFather 回复：*

> Alright, a new bot. How are we going to call it? Please choose a name for your bot.

选择您机器人的公开名称（例如 `Freqtrade bot`）

*BotFather 回复：*

> Good. Now let's choose a username for your bot. It must end in `bot`. Like this, for example: TetrisBot or tetris_bot.

选择您机器人的名称 ID 并发送给 BotFather（例如 "`My_own_freqtrade_bot`"）

*BotFather 回复：*

> Done! Congratulations on your new bot. You will find it at `t.me/yourbots_name_bot`. You can now add a description, about section and profile picture for your bot, see /help for a list of commands. By the way, when you've finished creating your cool bot, ping our Bot Support if you want a better username for it. Just make sure the bot is fully operational before you do this.

> Use this token to access the HTTP API: `22222222:APITOKEN`

> For a description of the Bot API, see this page: https://core.telegram.org/bots/api Father bot will return you the token (API key)

复制 API Token（上面示例中的 `22222222:APITOKEN`）并将其用于配置参数 `token`。

不要忘记通过点击 `/START` 按钮开始与您的机器人对话

### 2. Telegram user_id

#### 获取您的用户 ID

与 [userinfobot](https://telegram.me/userinfobot) 对话

获取您的"Id"，您将用它作为配置参数 `chat_id`。

#### 使用群组 ID

要获取群组 ID，您可以将机器人添加到群组，启动 freqtrade，并发出 `/tg_info` 命令。
这将向您返回群组 ID，而无需使用某个随机机器人。
虽然仍然需要"chat_id"，但对于此命令，它不需要设置为这个特定的群组 ID。

响应还将包含"topic_id"（如果需要）- 两者都以准备复制/粘贴到您的配置中的格式提供。

``` json
 {
    "enabled": true,
    "token": "********",
    "chat_id": "-1001332619709",
    "topic_id": "122"
}
```

对于 Freqtrade 配置，您可以使用完整值（包括 `-`）作为字符串：

```json
   "chat_id": "-1001332619709"
```

!!! Warning "使用 telegram 群组"
    当使用 telegram 群组时，您将让 telegram 群组的每个成员都能访问您的 freqtrade 机器人以及通过 telegram 可能的所有命令。请确保您可以信任 telegram 群组中的每个人，以避免不愉快的意外。

##### 群组主题 ID

要在群组中使用特定主题，您可以在配置中使用 `topic_id` 参数。这将允许您在群组的特定主题中使用机器人。
如果没有这个，如果为群组聊天启用了主题，机器人将始终响应群组中的常规频道。

```json
   "chat_id": "-1001332619709",
   "topic_id": "3"
```

与群组 ID 类似 - 您可以从主题/线程使用 `/tg_info` 来获取正确的主题 ID。

#### 授权用户

对于群组，限制谁可以向机器人发送命令可能很有用。

如果存在 `"authorized_users": []` 且为空，则不允许任何用户控制机器人。
在下面的示例中，只有 ID 为"1234567"的用户被允许控制机器人 - 所有其他用户只能接收消息。

```json
   "chat_id": "-1001332619709",
   "topic_id": "3",
   "authorized_users": ["1234567"]
```

## 控制 telegram 噪音

Freqtrade 提供了控制您的 telegram 机器人详细程度的方法。
每个设置都有以下可能的值：

* `on` - 将发送消息，用户将收到通知。
* `silent` - 将发送消息，通知将没有声音/振动。
* `off` - 完全跳过发送消息类型。

显示不同设置的示例配置：

``` json
"telegram": {
    "enabled": true,
    "token": "your_telegram_token",
    "chat_id": "your_telegram_chat_id",
    "allow_custom_messages": true,
    "notification_settings": {
        "status": "silent",
        "warning": "on",
        "startup": "off",
        "entry": "silent",
        "entry_fill": "on",
        "entry_cancel": "silent",
        "exit": {
            "roi": "silent",
            "emergency_exit": "on",
            "force_exit": "on",
            "exit_signal": "silent",
            "trailing_stop_loss": "on",
            "stop_loss": "on",
            "stoploss_on_exchange": "on",
            "custom_exit": "silent",  // 没有指定退出原因的自定义退出
            "partial_exit": "on",
            // "custom_exit_message": "silent",  // 禁用个别自定义退出原因
            "*": "off"  // 禁用所有其他退出原因
        },
        // "exit": "off",  // 禁用所有退出消息的简化配置
        "exit_cancel": "on",
        "exit_fill": "off",
        "protection_trigger": "off",
        "protection_trigger_global": "on",
        "strategy_msg": "off",
        "show_candle": "off"
    },
    "reload": true,
    "balance_dust_level": 0.01
},
```

* `entry` 通知在下单时发送，而 `entry_fill` 通知在订单在交易所成交时发送。
* `exit` 通知在下单时发送，而 `exit_fill` 通知在订单在交易所成交时发送。
    退出消息（`exit` 和 `exit_fill`）可以在个别退出原因级别进一步控制，以特定退出原因作为键。所有退出原因的默认值是 `on` - 但可以通过特殊的 `*` 键配置 - 它将作为所有未明确定义的退出原因的通配符。
* `*_fill` 通知默认关闭，必须明确启用。
* `protection_trigger` 通知在保护触发时发送，`protection_trigger_global` 通知在全局保护触发时触发。
* `strategy_msg` - 接收来自策略的通知，通过策略中的 `self.dp.send_msg()` 发送 [更多详情](strategy-customization.md#send-notification)。
* `show_candle` - 将蜡烛图值显示为入场/出场消息的一部分。只有可能的值是 `"ohlc"` 或 `"off"`。
* `balance_dust_level` 将定义 `/balance` 命令将什么视为"灰尘" - 余额低于此值的货币将被显示。
* `allow_custom_messages` 完全禁用策略消息。
* `reload` 允许您在选定消息上禁用重新加载按钮。

## 创建自定义键盘（命令快捷按钮）

Telegram 允许我们创建带有命令按钮的自定义键盘。
默认自定义键盘如下所示。

```python
[
    ["/daily", "/profit", "/balance"], # 第1行，3个命令
    ["/status", "/status table", "/performance"], # 第2行，3个命令
    ["/count", "/start", "/stop", "/help"] # 第3行，4个命令
]
```

### 用法

您可以在 `config.json` 中创建自己的键盘：

``` json
"telegram": {
      "enabled": true,
      "token": "your_telegram_token",
      "chat_id": "your_telegram_chat_id",
      "keyboard": [
          ["/daily", "/stats", "/balance", "/profit"],
          ["/status table", "/performance"],
          ["/reload_config", "/count", "/logs"]
      ]
   },
```

!!! Note "支持的命令"
    只允许以下命令。不支持命令参数！

    `/start`, `/pause`, `/stop`, `/status`, `/status table`, `/trades`, `/profit`, `/performance`, `/daily`, `/stats`, `/count`, `/locks`, `/balance`, `/stopentry`, `/reload_config`, `/show_config`, `/logs`, `/whitelist`, `/blacklist`, `/help`, `/version`, `/marketdir`

## Telegram 命令

默认情况下，Telegram 机器人显示预定义的命令。一些命令只能通过向机器人发送它们来使用。下表列出了官方命令。您可以随时使用 `/help` 寻求帮助。

|  命令 | 描述 |
|----------|-------------|
| **系统命令**
| `/start` | 启动交易者
| `/pause | /stopentry | /stopbuy` | 暂停交易者。根据规则优雅地处理开放交易。不进入新头寸。
| `/stop` | 停止交易者
| `/reload_config` | 重新加载配置文件
| `/show_config` | 显示当前配置的一部分，包含与操作相关的设置
| `/logs [limit]` | 显示最近的日志消息。
| `/help` | 显示帮助消息
| `/version` | 显示版本
| **状态** |
| `/status` | 列出所有开放交易
| `/status <trade_id>` | 列出一个或多个特定交易。用空格分隔多个 <trade_id>。
| `/status table` | 以表格格式列出所有开放交易。待买订单用星号 (*) 标记，待卖订单用双星号 (**) 标记
| `/order <trade_id>` | 列出一个或多个特定交易的订单。用空格分隔多个 <trade_id>。
| `/trades [limit]` | 以表格格式列出所有最近关闭的交易。
| `/count` | 显示已使用和可用的交易数量
| `/locks` | 显示当前锁定的交易对。
| `/unlock <pair or lock_id>` | 移除此交易对的锁定（或此锁定 ID）。
| `/marketdir [long \| short \| even \| none]` | 更新代表当前市场方向的用户管理变量。如果未提供方向，将显示当前设置的方向。
| **交易控制** |
| `/forcelong <pair> [rate]` | 立即做多给定交易对。价格是可选的，仅适用于限价订单。（必须将 `force_entry_enable` 设置为 True）
| `/forceshort <pair> [rate]` | 立即做空给定交易对。价格是可选的，仅适用于限价订单。这仅在非现货市场上有效。（必须将 `force_entry_enable` 设置为 True）
| `/delete <trade_id>` | 从数据库中删除特定交易。尝试关闭开放订单。需要在交易所手动处理此交易。
| `/reload_trade <trade_id>` | 从交易所重新加载交易。仅在实盘中有效，可能有助于恢复在交易所手动卖出的交易。
| `/cancel_open_order <trade_id> \| /coo <trade_id>` | 取消交易的开放订单。
| **指标** |
| `/profit [<n>]` | 显示您从关闭交易中的利润/损失摘要以及您的表现统计，过去 n 天（默认所有交易）
| `/performance` | 显示按交易对分组的每个已完成交易的表现
| `/balance` | 显示机器人管理的每种货币余额
| `/balance full` | 显示每种货币的账户余额
| `/daily <n>` | 显示过去 n 天的每日利润或损失（n 默认为 7）
| `/weekly <n>` | 显示过去 n 周的每周利润或损失（n 默认为 8）
| `/monthly <n>` | 显示过去 n 个月的每月利润或损失（n 默认为 6）
| `/stats` | 显示按出场原因的胜负以及买卖的平均持有时间
| `/exits` | 显示按出场原因的胜负以及买卖的平均持有时间
| `/entries` | 显示按入场原因的胜负以及买卖的平均持有时间
| `/whitelist [sorted] [baseonly]` | 显示当前白名单。可选择按字母顺序显示和/或仅显示每个配对的基础货币。
| `/blacklist [pair]` | 显示当前黑名单，或将交易对添加到黑名单。

## Telegram 命令实际操作

下面是您将为每个命令收到的 Telegram 消息示例。

### /start

> **状态:** `running`

### /pause | /stopentry | /stopbuy

> **状态:** `paused, no more entries will occur from now. Run /start to enable entries.`

### /stop

> `Stopping trader ...`
> **状态:** `stopped`

### /status

对于每个开放交易，机器人将向您发送以下消息。
入场标签可通过策略配置。

> **交易 ID:** `123` `(since 1 days ago)`
> **当前交易对:** CVC/BTC
> **方向:** Long
> **杠杆:** 1.0
> **数量:** `26.64180098`
> **入场标签:** Awesome Long Signal
> **开仓价格:** `0.00007489`
> **当前价格:** `0.00007489`
> **未实现利润:** `12.95%`
> **止损:** `0.00007389 (-0.02%)`

### /status table

以表格格式返回所有开放交易的状态。

```
ID L/S    Pair     Since   Profit
----    --------  -------  --------
  67 L   SC/BTC    1 d      13.33%
 123 S   CVC/BTC   1 h      12.95%
```

### /count

返回已使用和可用的交易数量。

```
current    max
---------  -----
     2     10
```

### /profit

返回您的利润/损失和表现摘要。

> **ROI:** Close trades
>   ∙ `0.00485701 BTC (2.2%) (15.2 Σ%)`
>   ∙ `62.968 USD`
> **ROI:** All trades
>   ∙ `0.00255280 BTC (1.5%) (6.43 Σ%)`
>   ∙ `33.095 EUR`
>
> **总交易数:** `138`
> **机器人启动:** `2022-07-11 18:40:44`
> **首次交易开启:** `3 days ago`
> **最新交易开启:** `2 minutes ago`
> **平均持续时间:** `2:33:45`
> **最佳表现:** `PAY/BTC: 50.23%`
> **交易量:** `0.5 BTC`
> **利润因子:** `1.04`
> **胜/负:** `102 / 36`
> **胜率:** `73.91%`
> **期望值（比率）:** `4.87 (1.66)`
> **最大回撤:** `9.23% (0.01255 BTC)`

### /forcelong <pair> [rate] | /forceshort <pair> [rate]

`/forcebuy <pair> [rate]` 也支持做多，但应被视为已弃用。

> **BINANCE:** Long ETH/BTC with limit `0.03400000` (`1.000000 ETH`, `225.290 USD`)

省略交易对将打开一个查询，询问要交易的交易对（基于当前白名单）。
通过 `/forcelong` 创建的交易将具有 `force_entry` 的买入标签。

![Telegram force-buy screenshot](assets/telegram_forcebuy.png)

请注意，为了使其工作，需要将 `force_entry_enable` 设置为 true。

[更多详情](configuration.md#understand-force_entry_enable)

### /performance

显示按交易对分组的每个已完成交易的表现。

> **Performance:**
> 1. `RCN/BTC 57.77%`
> 2. `PAY/BTC 56.91%`
> 3. `VIB/BTC 47.07%`
> 4. `SALT/BTC 30.24%`
> 5. `STORJ/BTC 27.24%`
> ...

### /balance

> **Currency:** BTC
> **Available:** 3.05890234
> **Balance:** 3.05890234
> **Pending:** 0.0

### /daily <n>

默认情况下 `/daily` 将返回最近 7 天。下面的示例是 `/daily 3`：

> **过去 3 天的每日利润:**

```
Day (count)     USDT          USD         Profit %
--------------  ------------  ----------  ----------
2022-06-11 (1)  -0.746 USDT   -0.75 USD   -0.08%
2022-06-10 (0)  0 USDT        0.00 USD    0.00%
2022-06-09 (5)  20 USDT       20.10 USD   5.00%
```

### /weekly <n>

默认情况下 `/weekly` 将返回最近 8 周，包括当前周。每周从周一开始。下面的示例是 `/weekly 3`：

> **过去 3 周的每周利润（从周一开始）:**

```
Monday (count)  Profit BTC      Profit USD   Profit %
-------------  --------------  ------------    ----------
2018-01-03 (5)  0.00224175 BTC  29,142 USD   4.98%
2017-12-27 (1)  0.00033131 BTC   4,307 USD   0.00%
2017-12-20 (4)  0.00269130 BTC  34.986 USD   5.12%
```

### /monthly <n>

默认情况下 `/monthly` 将返回最近 6 个月，包括当前月。下面的示例是 `/monthly 3`：

> **过去 3 个月的每月利润:**
```
Month (count)  Profit BTC      Profit USD    Profit %
-------------  --------------  ------------    ----------
2018-01 (20)    0.00224175 BTC  29,142 USD  4.98%
2017-12 (5)    0.00033131 BTC   4,307 USD   0.00%
2017-11 (10)    0.00269130 BTC  34.986 USD  5.10%
```

### /whitelist

显示当前白名单

> Using whitelist `StaticPairList` with 22 pairs
> `IOTA/BTC, NEO/BTC, TRX/BTC, VET/BTC, ADA/BTC, ETC/BTC, NCASH/BTC, DASH/BTC, XRP/BTC, XVG/BTC, EOS/BTC, LTC/BTC, OMG/BTC, BTG/BTC, LSK/BTC, ZEC/BTC, HOT/BTC, IOTX/BTC, XMR/BTC, AST/BTC, XLM/BTC, NANO/BTC`

### /blacklist [pair]

显示当前黑名单。
如果设置了交易对，则此交易对将被添加到配对列表中。
也支持多个交易对，用空格分隔。
使用 `/reload_config` 重置黑名单。

> Using blacklist `StaticPairList` with 2 pairs
>`DODGE/BTC`, `HOT/BTC`.

### /version

> **Version:** `0.14.3`

### /marketdir

显示或设置当前市场方向。

> **Market direction:** `long`

如果提供了方向参数：

> **Market direction:** `short`

## 配置示例

### 基本配置

```json
"telegram": {
    "enabled": true,
    "token": "your_telegram_token",
    "chat_id": "your_telegram_chat_id"
}
```

### 高级配置

```json
"telegram": {
    "enabled": true,
    "token": "your_telegram_token",
    "chat_id": "your_telegram_chat_id",
    "topic_id": "3",
    "authorized_users": ["1234567"],
    "allow_custom_messages": true,
    "balance_dust_level": 0.01,
    "notification_settings": {
        "status": "silent",
        "warning": "on",
        "startup": "off",
        "entry": "silent",
        "entry_fill": "on",
        "entry_cancel": "silent",
        "exit": {
            "roi": "silent",
            "emergency_exit": "on",
            "force_exit": "on",
            "exit_signal": "silent",
            "trailing_stop_loss": "on",
            "stop_loss": "on",
            "stoploss_on_exchange": "on",
            "custom_exit": "silent",
            "partial_exit": "on"
        },
        "exit_cancel": "on",
        "exit_fill": "off",
        "protection_trigger": "on",
        "protection_trigger_global": "on",
        "strategy_msg": "on",
        "show_candle": "ohlc"
    },
    "keyboard": [
        ["/daily", "/stats", "/balance", "/profit"],
        ["/status table", "/performance"],
        ["/reload_config", "/count", "/logs"]
    ]
}
```

## 故障排除

### 常见问题

1. **机器人不响应命令**
   - 检查机器人令牌是否正确
   - 确保已与机器人开始对话（点击 /start）
   - 验证 chat_id 是否正确

2. **权限错误**
   - 确保机器人具有发送消息的权限
   - 检查群组设置（如果使用群组）

3. **通知不工作**
   - 检查通知设置配置
   - 确保机器人正在运行

### 安全建议

- 不要与任何人分享您的机器人令牌
- 在群组中使用时要小心授权用户
- 定期检查谁有权访问您的机器人
- 考虑使用私人聊天而不是群组

### 最佳实践

- 使用自定义键盘提高效率
- 配置适当的通知级别以避免垃圾信息
- 定期检查机器人日志
- 保持机器人令牌安全
