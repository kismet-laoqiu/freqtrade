# Freqtrade Bitget三倍杠杆回测和实盘交易脚本

本目录包含用于Bitget交易所三倍杠杆回测和实盘交易的辅助脚本。这些脚本可以帮助您自动化获取所有USDT合约交易对、执行批量回测、分析结果、筛选优质币种，以及监控实盘交易。

## 脚本列表

1. **bitget_3x_leverage_backtest.sh** - 自动化执行Bitget所有USDT合约币种的三倍杠杆回测
2. **analyze_backtest_results.py** - 分析回测结果并筛选出表现最好的币种
3. **monitor_live_trading.py** - 实盘交易监控和报告生成

## 使用方法

### 1. 三倍杠杆回测脚本 (bitget_3x_leverage_backtest.sh)

这个脚本自动执行以下步骤：
- 获取Bitget所有USDT合约交易对
- 创建三倍杠杆回测配置
- 下载历史数据
- 执行回测
- 分析结果
- 筛选优质币种
- 创建实盘配置

使用方法：

```bash
# 添加执行权限
chmod +x bitget_3x_leverage_backtest.sh

# 在freqtrade根目录下执行
./docs-zh/scripts/bitget_3x_leverage_backtest.sh
```

### 2. 回测结果分析脚本 (analyze_backtest_results.py)

这个Python脚本可以分析回测结果，计算各种性能指标，并筛选出表现最好的币种。

使用方法：

```bash
# 添加执行权限
chmod +x analyze_backtest_results.py

# 基本用法
python docs-zh/scripts/analyze_backtest_results.py user_data/backtest_results/all_pairs_3x_leverage_20240630.json

# 自定义筛选条件
python docs-zh/scripts/analyze_backtest_results.py user_data/backtest_results/all_pairs_3x_leverage_20240630.json \
    --min-trades 10 \
    --min-win-rate 0.5 \
    --min-profit 0.1 \
    --max-drawdown -0.2 \
    --min-sharpe 1.0 \
    --top-n 10
```

参数说明：
- `--min-trades` - 最少交易次数（默认：5）
- `--min-win-rate` - 最低胜率（默认：0.4）
- `--min-profit` - 最低总收益率（默认：0.05）
- `--max-drawdown` - 最大回撤（默认：-0.3）
- `--min-sharpe` - 最低夏普比率（默认：0.5）
- `--top-n` - 选择前N个币种（默认：20）

### 3. 实盘交易监控脚本 (monitor_live_trading.py)

这个Python脚本可以监控实盘交易状态、账户余额和风险指标，并生成监控报告。

使用方法：

```bash
# 添加执行权限
chmod +x monitor_live_trading.py

# 基本用法（单次监控）
python docs-zh/scripts/monitor_live_trading.py

# 持续监控（每5分钟）
python docs-zh/scripts/monitor_live_trading.py --continuous --interval 300

# 自定义API地址和认证
python docs-zh/scripts/monitor_live_trading.py \
    --api-url http://your-server:8080 \
    --username your_username \
    --password your_password
```

参数说明：
- `--api-url` - FreqUI API地址（默认：http://localhost:8080）
- `--username` - API用户名
- `--password` - API密码
- `--output-dir` - 报告输出目录（默认：user_data/reports）
- `--interval` - 监控间隔（秒）（默认：300）
- `--continuous` - 持续监控模式

## 完整工作流程

以下是使用这些脚本的完整工作流程：

1. **准备环境**：
   ```bash
   # 确保freqtrade已安装并配置
   cd freqtrade
   ./setup.sh -i
   ```

2. **获取所有交易对并执行回测**：
   ```bash
   # 执行自动化回测脚本
   ./docs-zh/scripts/bitget_3x_leverage_backtest.sh
   ```

3. **详细分析回测结果**：
   ```bash
   # 分析最新的回测结果
   python docs-zh/scripts/analyze_backtest_results.py \
       user_data/backtest_results/all_pairs_3x_leverage_$(date +%Y%m%d).json
   ```

4. **更新优质币种列表**：
   根据分析结果，更新`user_data/pairlists/bitget_best_performers.json`文件。

5. **配置实盘交易**：
   编辑`user_data/config_live_3x.json`，添加API密钥和其他必要配置。

6. **启动实盘交易**：
   ```bash
   # 启动实盘交易
   freqtrade trade \
       --strategy ClucHAnix_5m \
       --config user_data/config_live_3x.json
   ```

7. **监控实盘交易**：
   ```bash
   # 持续监控实盘交易
   python docs-zh/scripts/monitor_live_trading.py --continuous
   ```

## 注意事项

- 这些脚本需要在freqtrade根目录下运行
- 确保已安装所需的Python依赖（pandas, numpy等）
- 合约交易具有高风险，请谨慎使用杠杆
- 实盘交易前，务必充分测试策略
- 定期检查和更新优质币种列表

## 自定义和扩展

您可以根据自己的需求自定义这些脚本：

- 修改筛选条件以适应不同的风险偏好
- 添加更多的性能指标和分析方法
- 集成电子邮件或其他通知方式
- 添加自动止损和风险管理功能

## 贡献

欢迎提交改进建议和bug报告。您可以通过以下方式贡献：

1. Fork仓库
2. 创建功能分支
3. 提交更改
4. 推送到分支
5. 创建Pull Request

## 许可

这些脚本遵循与Freqtrade相同的许可协议。
