# 生产者/消费者模式

freqtrade 提供了一种机制，其中一个实例（也称为`消费者`）可以使用消息 websocket 监听来自上游 freqtrade 实例（也称为`生产者`）的消息。主要是 `analyzed_df` 和 `whitelist` 消息。这允许在多个机器人中重用计算的指标（和信号），而无需多次计算它们。

请参阅 Rest API 文档中的[消息 Websocket](rest-api.md#消息-websocket)，了解如何为您的消息 websocket 设置 `api_server` 配置（这将是您的生产者）。

!!! Note
    我们强烈建议将 `ws_token` 设置为只有您自己知道的随机值，以避免未经授权访问您的机器人。

## 配置

通过在消费者的配置文件中添加 `external_message_consumer` 部分来启用订阅实例。

```json
{
    //...
   "external_message_consumer": {
        "enabled": true,
        "producers": [
            {
                "name": "default", // 这可以是您喜欢的任何名称，默认为 "default"
                "host": "127.0.0.1", // 来自您生产者的 api_server 配置的主机
                "port": 8080, // 来自您生产者的 api_server 配置的端口
                "secure": false, // 使用安全的 websockets 连接，默认 false
                "ws_token": "sercet_Ws_t0ken" // 来自您生产者的 api_server 配置的 ws_token
            }
        ],
        // 以下配置是可选的，通常不需要
        // "wait_timeout": 300,
        // "ping_timeout": 10,
        // "sleep_time": 10,
        // "remove_entry_exit_signals": false,
        // "message_size_limit": 8
    }
    //...
}
```

|  参数 | 描述 |
|------------|-------------|
| `enabled` | **必需。** 启用消费者模式。如果设置为 false，此部分中的所有其他设置都将被忽略。<br>*默认为 `false`。*<br> **数据类型：** boolean 。
| `producers` | **必需。** 生产者列表 <br> **数据类型：** Array。
| `producers.name` | **必需。** 此生产者的名称。如果使用多个生产者，则必须在调用 `get_producer_pairs()` 和 `get_producer_df()` 时使用此名称。<br> **数据类型：** string
| `producers.host` | **必需。** 来自您生产者的主机名或 IP 地址。<br> **数据类型：** string
| `producers.port` | **必需。** 与上述主机匹配的端口。<br>*默认为 `8080`。*<br> **数据类型：** Integer
| `producers.secure` | **可选。**  在 websockets 连接中使用 ssl。默认 False。<br> **数据类型：** string
| `producers.ws_token` | **必需。**  在生产者上配置的 `ws_token`。<br> **数据类型：** string
| | **可选设置**
| `wait_timeout` | 如果没有收到消息，再次 ping 之前的超时时间。 <br>*默认为 `300`。*<br> **数据类型：** Integer - 以秒为单位。
| `ping_timeout` | Ping 超时 <br>*默认为 `10`。*<br> **数据类型：** Integer - 以秒为单位。
| `sleep_time` | 重试连接前的睡眠时间。<br>*默认为 `10`。*<br> **数据类型：** Integer - 以秒为单位。
| `remove_entry_exit_signals` | 在接收数据框时从数据框中删除信号列（将它们设置为 0）。<br>*默认为 `false`。*<br> **数据类型：** Boolean。
| `initial_candle_limit` | 从生产者期望的初始蜡烛图数量。<br>*默认为 `1500`。*<br> **数据类型：** Integer - 蜡烛图数量。
| `message_size_limit` | 每条消息的大小限制<br>*默认为 `8`。*<br> **数据类型：** Integer - 兆字节。

消费者实例不是（或除了）在 `populate_indicators()` 中计算指标，而是监听与生产者实例消息的连接（或在高级配置中的多个生产者实例），并为活动白名单中的每个交易对请求生产者最近分析的数据框。

然后，消费者实例将拥有分析数据框的完整副本，而无需自己计算它们。

## 示例

### 示例 - 生产者策略

一个具有多个指标的简单策略。策略本身不需要特殊考虑。

```py
class ProducerStrategy(IStrategy):
    #...
    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        以标准 freqtrade 方式计算指标，然后可以广播到其他实例
        """
        dataframe['rsi'] = ta.RSI(dataframe)
        bollinger = qtpylib.bollinger_bands(qtpylib.typical_price(dataframe), window=20, stds=2)
        dataframe['bb_lowerband'] = bollinger['lower']
        dataframe['bb_middleband'] = bollinger['mid']
        dataframe['bb_upperband'] = bollinger['upper']
        dataframe['tema'] = ta.TEMA(dataframe, timeperiod=9)

        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        为给定数据框填充入场信号
        """
        dataframe.loc[
            (
                (qtpylib.crossed_above(dataframe['rsi'], self.buy_rsi.value)) &
                (dataframe['tema'] <= dataframe['bb_middleband']) &
                (dataframe['tema'] > dataframe['tema'].shift(1)) &
                (dataframe['volume'] > 0)
            ),
            'enter_long'] = 1

        return dataframe
```

!!! Tip "FreqAI"
    您可以使用此功能在强大的机器上设置 [FreqAI](freqai.md)，同时在简单的机器（如树莓派）上运行消费者，这些消费者可以以不同的方式解释从生产者生成的信号。

### 示例 - 消费者策略

消费者策略可以使用来自生产者的数据，而无需重新计算指标。

```py
class ConsumerStrategy(IStrategy):
    #...
    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        不需要计算指标 - 它们来自生产者
        """
        # 可选：添加仅消费者特定的指标
        # dataframe['consumer_specific'] = some_calculation(dataframe)
        
        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        使用来自生产者的指标
        """
        dataframe.loc[
            (
                (dataframe['rsi'] > 30) &  # 来自生产者的 RSI
                (dataframe['tema'] > dataframe['bb_lowerband']) &  # 来自生产者的指标
                (dataframe['volume'] > 0)
            ),
            'enter_long'] = 1

        return dataframe
```

## 高级用法

### 多个生产者

您可以配置多个生产者来获取不同的数据：

```json
{
   "external_message_consumer": {
        "enabled": true,
        "producers": [
            {
                "name": "signals_producer",
                "host": "192.168.1.100",
                "port": 8080,
                "ws_token": "producer1_token"
            },
            {
                "name": "indicators_producer", 
                "host": "192.168.1.101",
                "port": 8080,
                "ws_token": "producer2_token"
            }
        ]
    }
}
```

在策略中使用特定生产者：

```py
def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
    # 从特定生产者获取数据
    producer_df = self.dp.get_producer_df(metadata['pair'], producer_name="indicators_producer")
    if producer_df is not None:
        dataframe = producer_df
    return dataframe
```

### 数据提供者方法

消费者策略可以使用以下方法访问生产者数据：

```py
# 获取生产者的交易对列表
pairs = self.dp.get_producer_pairs(producer_name="default")

# 获取特定交易对的数据框
df = self.dp.get_producer_df(pair="BTC/USDT", producer_name="default")
```

## 故障排除

### 常见问题

1. **连接失败**
   - 检查网络连接
   - 验证主机和端口设置
   - 确认 ws_token 正确

2. **数据不同步**
   - 检查生产者是否正在运行
   - 验证交易对列表匹配
   - 检查消息大小限制

3. **性能问题**
   - 调整 ping_timeout 和 wait_timeout
   - 减少 message_size_limit
   - 优化网络连接

### 调试技巧

- 启用详细日志记录
- 监控 websocket 连接状态
- 检查消息队列大小
- 验证数据完整性

## 使用场景

### 1. 计算资源优化

在一台强大的服务器上运行生产者，在多台轻量级机器上运行消费者。

### 2. 策略分离

生产者专注于指标计算，消费者专注于交易逻辑。

### 3. 风险分散

使用不同的消费者策略处理相同的市场信号。

### 4. FreqAI 部署

在 GPU 服务器上运行 FreqAI 生产者，在边缘设备上运行消费者。
