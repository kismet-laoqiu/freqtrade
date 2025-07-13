# 订单流数据

本指南将引导您在 Freqtrade 中利用公共交易数据进行高级订单流分析。

!!! Warning "实验性功能"
    订单流功能目前处于测试阶段，在未来版本中可能会发生变化。请在 [Freqtrade GitHub 仓库](https://github.com/freqtrade/freqtrade/issues)上报告任何问题或反馈。
    目前也尚未与 freqAI 进行测试 - 在此阶段，将这两个功能结合使用被认为超出了范围。

!!! Warning "性能"
    订单流需要原始交易数据。这些数据相当庞大，当 freqtrade 需要下载最近 X 个蜡烛图的交易数据时，可能会导致初始启动缓慢。此外，启用此功能将导致内存使用量增加。请确保有足够的资源可用。

## 入门指南

### 启用公共交易

在您的 `config.json` 文件中，在 `exchange` 部分将 `use_public_trades` 选项设置为 true。

```json
"exchange": {
   ...
   "use_public_trades": true,
}
```

### 配置订单流处理

在 config.json 的 orderflow 部分定义您所需的订单流处理设置。在这里，您可以调整以下因素：

- `cache_size`：有多少个之前的订单流蜡烛图保存到缓存中，而不是每个新蜡烛图都重新计算
- `max_candles`：过滤您想要获取交易数据的蜡烛图数量
- `scale`：这控制足迹图表的价格区间大小
- `stacked_imbalance_range`：定义考虑所需的最小连续不平衡价格水平
- `imbalance_volume`：过滤掉低于此阈值的不平衡成交量
- `imbalance_ratio`：过滤掉比率（买卖成交量之间的差异）低于此值的不平衡

```json
"orderflow": {
    "cache_size": 1000, 
    "max_candles": 1500, 
    "scale": 0.5, 
    "stacked_imbalance_range": 3, //  需要至少这么多相邻的不平衡
    "imbalance_volume": 1, //  过滤掉低于此值的
    "imbalance_ratio": 3 //  过滤掉比率低于此值的
  },
```

## 下载回测的交易数据

要下载用于回测的历史交易数据，请在 freqtrade download-data 命令中使用 --dl-trades 标志。

```bash
freqtrade download-data --exchange binance --pairs BTC/USDT ETH/USDT --timeframes 5m --dl-trades
```

这将下载指定交易对的交易数据，这些数据将用于订单流分析。

!!! Note "数据存储"
    交易数据将存储在 `user_data/data/<exchange>/trades/` 目录中。这些文件可能会变得相当大，特别是对于高成交量的交易对。

## 在策略中使用订单流数据

### 基本订单流指标

一旦启用了订单流，您就可以在策略中访问各种订单流指标：

```python
from freqtrade.strategy import IStrategy
import pandas as pd

class OrderflowStrategy(IStrategy):
    
    timeframe = '5m'
    
    def populate_indicators(self, dataframe: pd.DataFrame, metadata: dict) -> pd.DataFrame:
        # 订单流数据将自动添加到数据框中
        # 可用的列包括：
        
        # 基本订单流指标
        dataframe['of_delta'] = dataframe.get('of_delta', 0)  # 买卖压力差
        dataframe['of_total_volume'] = dataframe.get('of_total_volume', 0)  # 总成交量
        dataframe['of_buy_volume'] = dataframe.get('of_buy_volume', 0)  # 买入成交量
        dataframe['of_sell_volume'] = dataframe.get('of_sell_volume', 0)  # 卖出成交量
        
        # 不平衡指标
        dataframe['of_imbalances'] = dataframe.get('of_imbalances', 0)  # 不平衡数量
        dataframe['of_stacked_imbalances_buy'] = dataframe.get('of_stacked_imbalances_buy', 0)
        dataframe['of_stacked_imbalances_sell'] = dataframe.get('of_stacked_imbalances_sell', 0)
        
        # 最小/最大价格
        dataframe['of_min_price'] = dataframe.get('of_min_price', dataframe['low'])
        dataframe['of_max_price'] = dataframe.get('of_max_price', dataframe['high'])
        
        return dataframe
    
    def populate_entry_trend(self, dataframe: pd.DataFrame, metadata: dict) -> pd.DataFrame:
        dataframe.loc[
            (
                # 强烈的买入压力
                (dataframe['of_delta'] > 0) &
                (dataframe['of_buy_volume'] > dataframe['of_sell_volume'] * 1.5) &
                # 有堆叠的买入不平衡
                (dataframe['of_stacked_imbalances_buy'] >= 3) &
                # 基本技术条件
                (dataframe['volume'] > 0)
            ),
            ['enter_long', 'enter_tag']] = (1, 'orderflow_buy_pressure')
        
        return dataframe
    
    def populate_exit_trend(self, dataframe: pd.DataFrame, metadata: dict) -> pd.DataFrame:
        dataframe.loc[
            (
                # 强烈的卖出压力
                (dataframe['of_delta'] < 0) &
                (dataframe['of_sell_volume'] > dataframe['of_buy_volume'] * 1.5) &
                # 有堆叠的卖出不平衡
                (dataframe['of_stacked_imbalances_sell'] >= 3)
            ),
            ['exit_long', 'exit_tag']] = (1, 'orderflow_sell_pressure')
        
        return dataframe
```

### 高级订单流分析

您可以创建更复杂的订单流分析：

```python
def populate_indicators(self, dataframe: pd.DataFrame, metadata: dict) -> pd.DataFrame:
    # 计算订单流比率
    dataframe['of_buy_sell_ratio'] = (
        dataframe['of_buy_volume'] / 
        (dataframe['of_sell_volume'] + 1e-8)  # 避免除零
    )
    
    # 计算累积 delta
    dataframe['of_cumulative_delta'] = dataframe['of_delta'].cumsum()
    
    # 计算 delta 的移动平均
    dataframe['of_delta_sma'] = dataframe['of_delta'].rolling(window=20).mean()
    
    # 检测 delta 背离
    dataframe['price_higher'] = dataframe['close'] > dataframe['close'].shift(1)
    dataframe['delta_lower'] = dataframe['of_delta'] < dataframe['of_delta'].shift(1)
    dataframe['bearish_divergence'] = dataframe['price_higher'] & dataframe['delta_lower']
    
    # 成交量加权平均价格 (VWAP) 使用订单流数据
    dataframe['of_vwap'] = (
        (dataframe['of_total_volume'] * dataframe['close']).cumsum() / 
        dataframe['of_total_volume'].cumsum()
    )
    
    # 不平衡强度
    dataframe['imbalance_strength'] = (
        dataframe['of_stacked_imbalances_buy'] - 
        dataframe['of_stacked_imbalances_sell']
    )
    
    return dataframe
```

### 订单流足迹图分析

订单流还提供足迹图数据，可用于更详细的价格水平分析：

```python
def analyze_footprint(self, dataframe: pd.DataFrame) -> pd.DataFrame:
    """
    分析足迹图数据以识别关键价格水平
    """
    # 足迹图数据包含每个价格水平的买卖成交量
    # 这些数据存储在 'of_footprint' 列中（如果可用）
    
    if 'of_footprint' in dataframe.columns:
        # 识别高成交量节点 (HVN)
        dataframe['hvn_level'] = dataframe['of_footprint'].apply(
            lambda x: self.find_high_volume_nodes(x) if x else None
        )
        
        # 识别低成交量节点 (LVN)
        dataframe['lvn_level'] = dataframe['of_footprint'].apply(
            lambda x: self.find_low_volume_nodes(x) if x else None
        )
        
        # 识别点控制 (POC) - 最高成交量的价格水平
        dataframe['poc_level'] = dataframe['of_footprint'].apply(
            lambda x: self.find_point_of_control(x) if x else None
        )
    
    return dataframe

def find_high_volume_nodes(self, footprint_data):
    """识别高成交量节点"""
    if not footprint_data:
        return None
    
    # 这里实现您的 HVN 识别逻辑
    # footprint_data 是一个包含价格水平和成交量的字典
    volumes = [data.get('total_volume', 0) for data in footprint_data.values()]
    if volumes:
        avg_volume = sum(volumes) / len(volumes)
        hvn_threshold = avg_volume * 1.5  # 高于平均成交量 50%
        
        hvn_levels = []
        for price, data in footprint_data.items():
            if data.get('total_volume', 0) > hvn_threshold:
                hvn_levels.append(float(price))
        
        return hvn_levels
    return None

def find_point_of_control(self, footprint_data):
    """识别点控制 (POC)"""
    if not footprint_data:
        return None
    
    max_volume = 0
    poc_price = None
    
    for price, data in footprint_data.items():
        volume = data.get('total_volume', 0)
        if volume > max_volume:
            max_volume = volume
            poc_price = float(price)
    
    return poc_price
```

## 订单流配置参数详解

### cache_size
控制缓存的订单流蜡烛图数量。较大的值会使用更多内存，但可以减少重复计算。

```json
"cache_size": 1000  // 推荐值：500-2000
```

### max_candles
限制获取交易数据的蜡烛图数量。这直接影响启动时间和内存使用。

```json
"max_candles": 1500  // 推荐值：1000-3000
```

### scale
控制足迹图的价格区间大小。较小的值提供更细粒度的分析，但会增加计算复杂度。

```json
"scale": 0.5  // 对于 BTC: 0.5-1.0, 对于山寨币: 0.001-0.01
```

### 不平衡参数

```json
"stacked_imbalance_range": 3,  // 连续不平衡的最小数量
"imbalance_volume": 1,         // 最小不平衡成交量
"imbalance_ratio": 3           // 最小不平衡比率
```

## 性能优化建议

1. **合理设置 max_candles**：不要设置过高的值，除非确实需要
2. **使用适当的 scale**：根据交易对的价格范围调整
3. **监控内存使用**：订单流会显著增加内存使用
4. **缓存管理**：适当的 cache_size 可以提高性能

```python
# 在策略中检查订单流数据可用性
def populate_indicators(self, dataframe: pd.DataFrame, metadata: dict) -> pd.DataFrame:
    # 检查订单流数据是否可用
    if 'of_delta' not in dataframe.columns:
        self.logger.warning(f"订单流数据不可用于 {metadata['pair']}")
        # 使用传统指标作为后备
        dataframe['rsi'] = ta.RSI(dataframe, 14)
        return dataframe
    
    # 使用订单流数据
    # ... 您的订单流逻辑
    
    return dataframe
```

## 故障排除

### 常见问题

1. **启动缓慢**
   - 减少 `max_candles` 值
   - 确保网络连接稳定
   - 考虑预先下载交易数据

2. **内存不足**
   - 减少 `cache_size` 和 `max_candles`
   - 增加系统内存
   - 使用较少的交易对

3. **数据缺失**
   - 确保交易所支持公共交易数据
   - 检查交易对是否活跃
   - 验证网络连接

4. **性能问题**
   - 调整 `scale` 参数
   - 优化策略逻辑
   - 考虑使用更快的硬件

订单流分析是一个强大的工具，可以提供传统技术分析无法获得的市场洞察。通过正确配置和使用，它可以显著提高您的交易策略的有效性。
