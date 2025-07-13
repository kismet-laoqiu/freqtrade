# REST API

## FreqUI

FreqUI 现在有自己专门的[文档部分](freq-ui.md) - 请参考该部分获取有关 FreqUI 的所有信息。

## 配置

通过将 api_server 部分添加到您的配置并将 `api_server.enabled` 设置为 `true` 来启用 rest API。

示例配置：

``` json
    "api_server": {
        "enabled": true,
        "listen_ip_address": "127.0.0.1",
        "listen_port": 8080,
        "verbosity": "error",
        "enable_openapi": false,
        "jwt_secret_key": "somethingrandom",
        "CORS_origins": [],
        "username": "Freqtrader",
        "password": "SuperSecret1!",
        "ws_token": "sercet_Ws_t0ken"
    },
```

!!! Danger "安全警告"
    默认情况下，配置仅监听 localhost（因此无法从其他系统访问）。我们强烈建议不要将此 API 暴露给互联网，并选择一个强大、唯一的密码，因为其他人可能能够控制您的机器人。

??? Note "远程服务器上的 API/UI 访问"
    如果您在 VPS 上运行，您应该考虑使用 ssh 隧道或设置 VPN（openVPN、wireguard）来连接到您的机器人。
    这将确保 freqUI 不会直接暴露给互联网，出于安全原因不建议这样做（freqUI 开箱即用不支持 https）。
    这些工具的设置不是本教程的一部分，但是在互联网上可以找到许多好的教程。

然后您可以通过在浏览器中访问 `http://127.0.0.1:8080/api/v1/ping` 来访问 API，以检查 API 是否正确运行。
这应该返回响应：

``` output
{"status":"pong"}
```

所有其他端点返回敏感信息并需要身份验证，因此无法通过网络浏览器访问。

### 安全性

要生成安全密码，最好使用密码管理器，或使用下面的代码。

``` python
import secrets
secrets.token_hex()
```

!!! Hint "JWT 令牌"
    使用相同的方法也生成 JWT 秘密密钥（`jwt_secret_key`）。

!!! Danger "密码选择"
    请确保选择一个非常强大、唯一的密码来保护您的机器人免受未经授权的访问。
    还要将 `jwt_secret_key` 更改为随机内容（无需记住这个，但它将用于加密您的会话，所以最好是唯一的！）。

### 使用 docker 的配置

如果您使用 docker 运行机器人，您需要让机器人监听传入连接。然后安全性由 docker 处理。

``` json
    "api_server": {
        "enabled": true,
        "listen_ip_address": "0.0.0.0",
        "listen_port": 8080,
        "username": "Freqtrader",
        "password": "SuperSecret1!",
        //...
    },
```

确保您的 docker-compose 文件中有以下 2 行：

```yml
    ports:
      - "127.0.0.1:8080:8080"
```

!!! Danger "安全警告"
    通过在 docker 端口映射中使用 `"8080:8080"`（或 `"0.0.0.0:8080:8080"`），API 将对连接到正确端口下的服务器的每个人可用，因此其他人可能能够控制您的机器人。
    如果您在安全环境中运行机器人（如您的家庭网络），这**可能**是安全的，但不建议将 API 暴露给互联网。

## Rest API

### 使用 API

我们建议通过使用支持的 `freqtrade-client` 包（也可作为 `scripts/rest_client.py` 使用）来使用 API。

此命令可以通过使用 `pip install freqtrade-client` 独立于任何运行的 freqtrade 机器人安装。

此模块设计为轻量级，仅依赖于 `requests` 和 `python-rapidjson` 模块，跳过 freqtrade 否则需要的所有重型依赖项。

``` bash
freqtrade-client <command> [optional parameters]
```

默认情况下，脚本假设使用 `127.0.0.1`（localhost）和端口 `8080`，但是您可以指定配置文件来覆盖此行为。

#### 最小客户端配置

```json
{
    "api_server": {
        "enabled": true,
        "listen_ip_address": "0.0.0.0",
        "listen_port": 8080,
        "username": "Freqtrader",
        "password": "SuperSecret1!",
        //...
    }
}
```

```bash
freqtrade-client --config rest_config.json <command> [optional parameters]
```

具有许多参数的命令可能需要关键字参数（为了清晰起见） - 可以按如下方式提供：

```bash
freqtrade-client --config rest_config.json forceenter BTC/USDT long enter_tag=GutFeeling
```

此方法适用于所有参数 - 检查"show"命令以获取可用参数列表。

??? Note "程序化使用"
    `freqtrade-client` 包（可独立于 freqtrade 安装）可以在您自己的脚本中使用以与 freqtrade API 交互。
    为此，请使用以下内容：

    ```python
    from freqtrade_client import FtRestClient


    client = FtRestClient(server_url, username, password)

    # 获取机器人状态
    ping = client.ping()
    print(ping)
    # ...
    ```

    有关可用命令的完整列表，请参考下面的列表。

可以使用 `help` 命令从 rest-client 脚本列出可能的命令。

```bash
freqtrade-client help
```

```output
可能的命令：

available_pairs
	根据时间框架/质押货币选择返回可用交易对（回测数据）

        :param timeframe: 仅具有此时间框架可用的交易对。
        :param stake_currency: 仅包含此时间框架的交易对

balance
	获取账户余额。

blacklist
	显示当前黑名单。

        :param add: 要添加的币种列表（示例："BNB/BTC"）

cancel_open_order
	取消交易的开放订单。

        :param trade_id: 取消此交易的开放订单。

count
	返回开放交易的数量。

daily
	返回每天的利润和交易数量。

delete_trade
	删除交易（从数据库中删除）。

        :param trade_id: 要删除的交易 ID。

entries
	返回每个入场标签的利润统计。

        :param pair: 要获取数据的交易对

exits
	返回每个出场原因的利润统计。

        :param pair: 要获取数据的交易对

forceexit
	立即退出交易。

        :param tradeid: 要退出的交易 ID。
        :param ordertype: 订单类型（limit 或 market，默认为 market）
        :param amount: 要退出的金额（默认为全部）

forceenter
	立即进入交易。

        :param pair: 要进入的交易对
        :param side: 交易方向（long 或 short，默认为 long）
        :param rate: 进入价格（可选）
        :param enter_tag: 入场标签（可选）
        :param leverage: 杠杆（可选）

health
	获取机器人健康状态。

locks
	显示当前锁定的交易对。

logs
	显示最近的日志消息。

        :param limit: 限制返回的日志条目数量（默认为最后 10 条）

mix_tags
	返回每个入场标签 + 出场原因组合的利润统计。

        :param pair: 要获取数据的交易对

pair_candles
	返回交易对的历史蜡烛图数据

        :param pair: 要获取数据的交易对
        :param timeframe: 仅具有此时间框架可用的交易对。
        :param strategy: 要分析并获取值的策略
        :param timerange: 要获取数据的时间范围（与 --timerange 端点相同格式）

pair_history
	返回历史的、分析过的数据框

        :param pair: 要获取数据的交易对
        :param timeframe: 仅具有此时间框架可用的交易对。
        :param strategy: 要分析并获取值的策略
        :param timerange: 要获取数据的时间范围（与 --timerange 端点相同格式）

performance
	返回不同币种的表现。

ping
	简单的 ping

plot_config
	如果策略定义了绘图配置，则返回绘图配置。

profit
	返回利润摘要。

reload_config
	重新加载配置。

show_config
        返回配置的一部分，与交易操作相关。

start
	如果机器人处于停止状态，则启动机器人。

pause
	如果机器人处于运行状态，则暂停机器人。如果在停止状态下触发，将处理开放头寸。

status
	获取机器人状态。

stats
	返回利润/损失原因摘要以及平均持有时间。

stop
	停止机器人。

stopbuy
	停止机器人开新仓。

strategies
	列出策略目录中的策略。

sysinfo
	获取系统信息。

trades
	返回交易列表。

        :param limit: 限制返回的交易数量（默认为最后 50 笔交易）
        :param offset: 偏移量（用于分页）

version
	获取机器人版本。

whitelist
	显示当前白名单。

```

### 可用端点

如果您希望通过另一种路由手动调用 REST API，例如直接通过 `curl`，下表显示了相关的 URL 端点和参数。
下表中的所有端点都需要以 API 的基本 URL 为前缀，例如 `http://127.0.0.1:8080/api/v1/` - 因此命令变为 `http://127.0.0.1:8080/api/v1/<command>`。

|  端点 | 方法 | 描述 / 参数 |
|-----------|--------|--------------------------|
| `/ping` | GET | 测试 API 就绪性的简单命令 - 不需要身份验证。
| `/start` | POST | 启动交易者。
| `/pause` | POST | 暂停交易者。根据规则优雅地处理开放交易。不进入新头寸。
| `/stop` | POST | 停止交易者。
| `/stopbuy` | POST | 停止交易者开新仓。根据规则优雅地关闭开放交易。
| `/reload_config` | POST | 重新加载配置文件。
| `/trades` | GET | 列出最近的交易。每次调用限制为 500 笔交易。
| `/trade/<tradeid>` | GET | 获取特定交易。<br/>*参数:*<br/>- `tradeid` (`int`)
| `/trades/<tradeid>` | DELETE | 从数据库中删除交易。尝试关闭开放订单。需要在交易所手动处理此交易。<br/>*参数:*<br/>- `tradeid` (`int`)
| `/trades/<tradeid>/open-order` | DELETE | 取消此交易的开放订单。<br/>*参数:*<br/>- `tradeid` (`int`)
| `/trades/<tradeid>/reload` | POST | 从交易所重新加载交易。仅在实盘中有效，可能有助于恢复在交易所手动卖出的交易。<br/>*参数:*<br/>- `tradeid` (`int`)
| `/show_config` | GET | 显示当前配置的一部分，包含与操作相关的设置。
| `/logs` | GET | 显示最近的日志消息。
| `/status` | GET | 列出所有开放交易。
| `/count` | GET | 显示已使用和可用的交易数量。
| `/entries` | GET | 显示给定交易对（如果未给出交易对则为所有交易对）每个入场标签的利润统计。交易对是可选的。<br/>*参数:*<br/>- `pair` (`str`)
| `/exits` | GET | 显示给定交易对（如果未给出交易对则为所有交易对）每个出场原因的利润统计。交易对是可选的。<br/>*参数:*<br/>- `pair` (`str`)
| `/mix_tags` | GET | 显示给定交易对（如果未给出交易对则为所有交易对）每个入场标签 + 出场原因组合的利润统计。交易对是可选的。<br/>*参数:*<br/>- `pair` (`str`)
| `/locks` | GET | 显示当前锁定的交易对。
| `/delete_lock` | DELETE | 删除锁定。<br/>*参数:*<br/>- `<lockid>` (`int`)
| `/forceexit` | POST | 立即退出给定交易（忽略 `minimum_roi`），使用给定的订单类型（"market" 或 "limit"，如果未指定则使用您的配置设置），以及选择的金额（如果未指定则全部卖出）。如果提供 `all` 作为 `tradeid`，则所有当前开放的交易都将被强制退出。<br/>*参数:*<br/>- `<tradeid>` (`int` 或 `str`)<br/>- `<ordertype>` (`str`)<br/>- `[amount]` (`float`)
| `/forceenter` | POST | 立即进入给定交易对。方向是可选的，可以是 `long` 或 `short`（默认为 `long`）。价格是可选的。（必须将 `force_entry_enable` 设置为 True）<br/>*参数:*<br/>- `<pair>` (`str`)<br/>- `<side>` (`str`)<br/>- `[rate]` (`float`)
| `/performance` | GET | 显示按交易对分组的每个已完成交易的表现。
| `/balance` | GET | 显示每种货币的账户余额。
| `/daily` | GET | 显示过去 n 天的每日利润或损失（n 默认为 7）。<br/>*参数:*<br/>- `<n>` (`int`)
| `/weekly` | GET | 显示过去 n 天的每周利润或损失（n 默认为 4）。<br/>*参数:*<br/>- `<n>` (`int`)
| `/monthly` | GET | 显示过去 n 天的每月利润或损失（n 默认为 3）。<br/>*参数:*<br/>- `<n>` (`int`)
| `/stats` | GET | 显示利润/损失原因摘要以及平均持有时间。
| `/whitelist` | GET | 显示当前白名单。
| `/blacklist` | GET | 显示当前黑名单。
| `/blacklist` | POST | 将指定交易对添加到黑名单。<br/>*参数:*<br/>- `pair` (`str`)
| `/blacklist` | DELETE | 从黑名单中删除指定的交易对列表。<br/>*参数:*<br/>- `[pair,pair]` (`list[str]`)
| `/pair_candles` | GET | 在机器人运行时返回交易对/时间框架组合的数据框。**Alpha**
| `/pair_candles` | POST | 在机器人运行时返回交易对/时间框架组合的数据框，由提供的列列表过滤返回。**Alpha**<br/>*参数:*<br/>- `<column_list>` (`list[str]`)
| `/pair_history` | GET | 返回给定时间范围的分析数据框，由给定策略分析。**Alpha**
| `/pair_history` | POST | 返回给定时间范围的分析数据框，由给定策略分析，由提供的列列表过滤返回。**Alpha**<br/>*参数:*<br/>- `<column_list>` (`list[str]`)
| `/plot_config` | GET | 从策略获取绘图配置（如果未配置则为空）。**Alpha**
| `/strategies` | GET | 列出策略目录中的策略。**Alpha**
| `/strategy/<strategy>` | GET | 通过策略类名获取特定策略内容。**Alpha**<br/>*参数:*<br/>- `<strategy>` (`str`)
| `/available_pairs` | GET | 列出可用的回测数据。**Alpha**
| `/version` | GET | 显示版本。
| `/sysinfo` | GET | 显示系统负载信息。
| `/health` | GET | 显示机器人健康状态（最后一次机器人循环）。

!!! Note
    所有标记为 **Alpha** 的端点都不被视为稳定，可能会在没有通知的情况下更改。

### 消息 WebSocket

API 服务器包含一个 websocket 端点，用于订阅来自 freqtrade 机器人的 RPC 消息。
这可以用于从您的机器人消费实时数据，例如入场/出场成交消息、白名单更改、交易对的填充指标等。

这也用于在 Freqtrade 中设置[生产者/消费者模式](producer-consumer.md)。

假设您的 rest API 设置为 `127.0.0.1` 端口 `8080`，端点在 `http://localhost:8080/api/v1/message/ws` 可用。

要访问 websocket 端点，需要在端点 URL 中将 `ws_token` 作为查询参数。

要生成安全的 `ws_token`，您可以运行以下代码：

```python
import secrets
secrets.token_urlsafe()
```

然后将此令牌添加到您的配置中：

```json
"api_server": {
    "enabled": true,
    "listen_ip_address": "127.0.0.1",
    "listen_port": 8080,
    "verbosity": "error",
    "enable_openapi": false,
    "jwt_secret_key": "somethingrandom",
    "CORS_origins": [],
    "username": "Freqtrader",
    "password": "SuperSecret1!",
    "ws_token": "hZ-y58LXyX_HZ8O1cJzVyN6ePWrLpNQv4Q"
},
```

您现在可以连接到端点 `http://localhost:8080/api/v1/message/ws?token=hZ-y58LXyX_HZ8O1cJzVyN6ePWrLpNQv4Q`。

!!! Danger "重用示例令牌"
    请不要使用上述示例令牌。为了确保您的安全，请生成一个全新的令牌。

#### 使用 WebSocket

连接到 WebSocket 后，机器人将向任何订阅它们的人广播 RPC 消息。要订阅消息类型列表，您必须通过 WebSocket 发送如下所示的 JSON 请求。`data` 键必须是消息类型字符串的列表。

```json
{
  "type": "subscribe",
  "data": ["whitelist", "analyzed_df"] // 字符串消息类型的列表
}
```

有关消息类型列表，请参考 `freqtrade/enums/rpcmessagetype.py` 中的 RPCMessageType 枚举

现在，只要连接处于活动状态，每当在机器人中发送这些类型的 RPC 消息时，您都会通过 WebSocket 接收它们。它们通常采用与请求相同的形式：

```json
{
  "type": "analyzed_df",
  "data": {
      "key": ["NEO/BTC", "5m", "spot"],
      "df": {}, // 数据框
      "la": "2022-09-08 22:14:41.457786+00:00"
  }
}
```

#### 反向代理和 WebSocket

如果您在反向代理后面运行 freqtrade，您可能需要确保它也支持 websocket 连接。

大多数现代反向代理应该处理这个问题，但是如果您遇到问题，请确保您的反向代理支持 websocket 连接。

```
# Nginx 示例配置
location /api/v1/message/ws {
    proxy_pass http://freqtrade;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}
```

要正确配置您的反向代理（安全地），请查阅其代理 websockets 的文档。

- **Traefik**: Traefik 开箱即用支持 websockets，请参阅[文档](https://doc.traefik.io/traefik/)
- **Caddy**: Caddy v2 开箱即用支持 websockets，请参阅[文档](https://caddyserver.com/docs/v2-upgrade#proxy)

!!! Tip "SSL 证书"
    您可以使用 certbot 等工具设置 ssl 证书，通过使用上述任何反向代理通过加密连接访问您的机器人 UI。
    虽然这将保护您的传输中数据，但我们不建议在您的私人网络（VPN、SSH 隧道）之外运行 freqtrade API。

### OpenAPI 接口

要启用内置的 openAPI 接口（Swagger UI），请在 api_server 配置中指定 `"enable_openapi": true`。
这将在 `/docs` 端点启用 Swagger UI。默认情况下，它在 http://localhost:8080/docs 运行 - 但这取决于您的设置。

### 使用 JWT 令牌的高级 API 使用

!!! Note
    以下应该在应用程序中完成（Freqtrade REST API 客户端，通过 API 获取信息），不打算定期使用。

Freqtrade 的 REST API 还提供 JWT（JSON Web Tokens）。
您可以使用以下命令登录，然后使用生成的 access_token。

```bash
> curl -X POST --user Freqtrader http://localhost:8080/api/v1/token/login
{"access_token":"eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpYXQiOjE1ODkxMTk2ODEsIm5iZiI6MTU4OTExOTY4MSwianRpIjoiMmEwYmY0NWUtMjhmOS00YTUzLTlmNzItMmM5ZWVlYThkNzc2IiwiZXhwIjoxNTg5MTIwNTgxLCJpZGVudGl0eSI6eyJ1IjoiRnJlcXRyYWRlciJ9LCJmcmVzaCI6ZmFsc2UsInR5cGUiOiJhY2Nlc3MifQ.qt6MAXYIa-l556OM7arBvYJ0SDI9J8bIk3_glDujF5g","refresh_token":"eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpYXQiOjE1ODkxMTk2ODEsIm5iZiI6MTU4OTExOTY4MSwianRpIjoiZWQ1ZWI3YjAtYjMwMy00YzAyLTg2N2MtNWViMjIxNWQ2YTMxIiwiZXhwIjoxNTkxNzExNjgxLCJpZGVudGl0eSI6eyJ1IjoiRnJlcXRyYWRlciJ9LCJ0eXBlIjoicmVmcmVzaCJ9.d1AT_jYICyTAjD0fiQAr52rkRqtxCjUGEMwlNuuzgNQ"}

> access_token="eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpYXQiOjE1ODkxMTk2ODEsIm5iZiI6MTU4OTExOTY4MSwianRpIjoiMmEwYmY0NWUtMjhmOS00YTUzLTlmNzItMmM5ZWVlYThkNzc2IiwiZXhwIjoxNTg5MTIwNTgxLCJpZGVudGl0eSI6eyJ1IjoiRnJlcXRyYWRlciJ9LCJmcmVzaCI6ZmFsc2UsInR5cGUiOiJhY2Nlc3MifQ.qt6MAXYIa-l556OM7arBvYJ0SDI9J8bIk3_glDujF5g"
# 使用 access_token 进行身份验证
> curl -X GET --header "Authorization: Bearer ${access_token}" http://localhost:8080/api/v1/count

```

由于访问令牌有短暂的超时（15 分钟） - 应该定期使用 `token/refresh` 请求来获取新的访问令牌：

```bash
> curl -X POST --header "Authorization: Bearer ${refresh_token}"http://localhost:8080/api/v1/token/refresh
{"access_token":"eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpYXQiOjE1ODkxMTk5NzQsIm5iZiI6MTU4OTExOTk3NCwianRpIjoiMDBjNTlhMWUtMjBmYS00ZTk0LTliZjAtNWQwNTg2MTdiZDIyIiwiZXhwIjoxNTg5MTIwODc0LCJpZGVudGl0eSI6eyJ1IjoiRnJlcXRyYWRlciJ9LCJmcmVzaCI6ZmFsc2UsInR5cGUiOiJhY2Nlc3MifQ.1seHlII3WprjjclY6DpRhen0rqdF4j6jbvxIhUFaSbs"}
```

## CORS

CORS（跨源资源共享）可以通过在 `api_server` 配置中设置 `CORS_origins` 来启用。

```json
{
    "api_server": {
        "enabled": true,
        "listen_ip_address": "0.0.0.0",
        "listen_port": 8080,
        "CORS_origins": ["https://example.com", "http://localhost:3000"],
        "username": "Freqtrader",
        "password": "SuperSecret1!",
        //...
    },
}
```

!!! Note
    这通常仅在您从不同域的 Web 应用程序访问 API 时才需要。
    如果您不确定是否需要这个，您可能不需要。

## 安全考虑

### 网络安全

- 永远不要将 API 直接暴露给互联网
- 使用强密码和 JWT 密钥
- 考虑使用 VPN 或 SSH 隧道进行远程访问
- 定期更新密码和令牌

### API 密钥管理

- 使用强大、唯一的密码
- 定期轮换 JWT 密钥
- 监控 API 访问日志
- 限制 API 访问到必要的 IP 地址

### 最佳实践

- 在生产环境中禁用 OpenAPI/Swagger UI
- 使用 HTTPS（通过反向代理）
- 实施适当的日志记录和监控
- 定期审查 API 访问权限
