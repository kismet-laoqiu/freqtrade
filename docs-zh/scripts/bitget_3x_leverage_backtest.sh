#!/bin/bash

# Bitget三倍杠杆回测全币种脚本
# 作者：Freqtrade用户
# 版本：1.0
# 描述：自动化执行Bitget所有USDT合约币种的三倍杠杆回测，并筛选出表现最好的币种

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查必要的环境
check_environment() {
    log_info "检查环境..."
    
    # 检查freqtrade是否安装
    if ! command -v freqtrade &> /dev/null; then
        log_error "Freqtrade未安装或不在PATH中"
        exit 1
    fi
    
    # 检查必要的目录
    if [ ! -d "user_data" ]; then
        log_error "user_data目录不存在，请确保在freqtrade根目录下运行此脚本"
        exit 1
    fi
    
    # 创建必要的目录
    mkdir -p user_data/pairlists
    mkdir -p user_data/backtest_results
    mkdir -p user_data/logs
    
    log_success "环境检查完成"
}

# 获取所有Bitget USDT合约交易对
get_all_pairs() {
    log_info "获取Bitget所有USDT合约交易对..."
    
    # 创建临时配置文件
    cat > user_data/config_bitget_temp.json << 'EOF'
{
    "$schema": "https://schema.freqtrade.io/schema.json",
    "trading_mode": "futures",
    "margin_mode": "isolated",
    "stake_currency": "USDT",
    "exchange": {
        "name": "bitget",
        "ccxt_config": {
            "enableRateLimit": true,
            "options": {
                "defaultType": "swap"
            }
        }
    },
    "pairlists": [
        {
            "method": "VolumePairList",
            "number_assets": 200,
            "sort_key": "quoteVolume"
        }
    ]
}
EOF

    # 获取交易对列表
    freqtrade test-pairlist -c user_data/config_bitget_temp.json --quote USDT --print-json > user_data/pairlists/bitget_all_futures.json
    
    # 检查是否成功获取
    if [ ! -s user_data/pairlists/bitget_all_futures.json ]; then
        log_error "获取交易对失败，请检查网络连接和配置"
        exit 1
    fi
    
    # 统计交易对数量
    PAIR_COUNT=$(jq length user_data/pairlists/bitget_all_futures.json)
    log_success "成功获取 $PAIR_COUNT 个USDT合约交易对"
    
    # 清理临时文件
    rm user_data/config_bitget_temp.json
}

# 创建三倍杠杆回测配置
create_backtest_config() {
    log_info "创建三倍杠杆回测配置..."
    
    cat > user_data/config_backtest_3x.json << 'EOF'
{
    "$schema": "https://schema.freqtrade.io/schema.json",
    "trading_mode": "futures",
    "margin_mode": "isolated",
    "max_open_trades": 5,
    "stake_currency": "USDT",
    "stake_amount": "unlimited",
    "tradable_balance_ratio": 0.99,
    "fiat_display_currency": "CNY",
    "dry_run_wallet": 1000,
    "timeframe": "5m",
    "dry_run": true,
    "cancel_open_orders_on_exit": true,
    "use_exit_signal": true,
    "exit_profit_only": false,
    "ignore_roi_if_entry_signal": false,
    "leverage": 3,
    "exchange": {
        "name": "bitget",
        "ccxt_config": {
            "enableRateLimit": true,
            "options": {
                "defaultType": "swap"
            }
        },
        "ccxt_async_config": {
            "enableRateLimit": true,
            "rateLimit": 200
        }
    },
    "order_types": {
        "entry": "limit",
        "exit": "limit",
        "emergency_exit": "market",
        "force_entry": "market",
        "force_exit": "market",
        "stoploss": "market",
        "stoploss_on_exchange": true,
        "stoploss_on_exchange_interval": 60,
        "stoploss_on_exchange_limit_ratio": 0.99
    },
    "entry_pricing": {
        "price_side": "same",
        "use_order_book": true,
        "order_book_top": 1,
        "price_last_balance": 0.0,
        "check_depth_of_market": {
            "enabled": false,
            "bids_to_ask_delta": 1
        }
    },
    "exit_pricing": {
        "price_side": "same",
        "use_order_book": true,
        "order_book_top": 1
    },
    "pairlists": [
        {
            "method": "StaticPairList"
        }
    ],
    "telegram": {
        "enabled": false
    },
    "api_server": {
        "enabled": false
    }
}
EOF
    
    log_success "三倍杠杆回测配置创建完成"
}

# 下载历史数据
download_data() {
    log_info "下载历史数据..."
    
    # 获取时间范围（最近90天）
    START_DATE=$(date -d "90 days ago" +%Y%m%d)
    END_DATE=$(date +%Y%m%d)
    
    log_info "下载时间范围：$START_DATE 到 $END_DATE"
    
    # 下载数据
    freqtrade download-data \
        --exchange bitget \
        --pairs-file user_data/pairlists/bitget_all_futures.json \
        --timeframes 5m 1h \
        --days 90 \
        -c user_data/config_backtest_3x.json
    
    log_success "历史数据下载完成"
}

# 执行回测
run_backtest() {
    log_info "开始执行三倍杠杆回测..."
    
    # 获取时间范围
    START_DATE=$(date -d "60 days ago" +%Y%m%d)
    END_DATE=$(date +%Y%m%d)
    
    log_info "回测时间范围：$START_DATE 到 $END_DATE"
    
    # 执行回测
    freqtrade backtesting \
        --strategy ClucHAnix_5m \
        --config user_data/config_backtest_3x.json \
        --timerange ${START_DATE}-${END_DATE} \
        --timeframe 5m \
        --pairs-file user_data/pairlists/bitget_all_futures.json \
        --export trades \
        --export-filename user_data/backtest_results/all_pairs_3x_leverage_$(date +%Y%m%d).json
    
    log_success "回测执行完成"
}

# 分析回测结果
analyze_results() {
    log_info "分析回测结果..."
    
    RESULT_FILE="user_data/backtest_results/all_pairs_3x_leverage_$(date +%Y%m%d).json"
    
    # 显示回测结果摘要
    log_info "回测结果摘要："
    freqtrade backtesting-show --export-filename $RESULT_FILE
    
    # 分析每个交易对的表现
    log_info "分析各交易对表现..."
    freqtrade backtesting-analysis \
        --export-filename $RESULT_FILE \
        --analysis-groups pair > user_data/backtest_results/analysis_$(date +%Y%m%d).txt
    
    log_success "结果分析完成，详细报告保存在 user_data/backtest_results/analysis_$(date +%Y%m%d).txt"
}

# 筛选优质币种
select_best_pairs() {
    log_info "筛选表现最好的币种..."
    
    # 这里可以根据实际需要调整筛选条件
    # 示例：选择收益率最高的前10个币种
    cat > user_data/pairlists/bitget_best_performers.json << 'EOF'
[
    "BTC/USDT:USDT",
    "ETH/USDT:USDT",
    "SOL/USDT:USDT",
    "XRP/USDT:USDT",
    "AVAX/USDT:USDT",
    "MATIC/USDT:USDT",
    "LINK/USDT:USDT",
    "DOGE/USDT:USDT",
    "ADA/USDT:USDT",
    "DOT/USDT:USDT"
]
EOF
    
    log_warning "注意：当前使用的是示例币种列表，请根据实际回测结果手动更新 user_data/pairlists/bitget_best_performers.json"
    log_success "优质币种列表已创建"
}

# 创建实盘配置
create_live_config() {
    log_info "创建实盘交易配置..."
    
    cp user_data/config_backtest_3x.json user_data/config_live_3x.json
    
    # 修改实盘配置
    jq '.dry_run = false | .max_open_trades = 3 | .tradable_balance_ratio = 0.90' \
        user_data/config_live_3x.json > user_data/config_live_3x_temp.json
    mv user_data/config_live_3x_temp.json user_data/config_live_3x.json
    
    log_success "实盘配置创建完成"
    log_warning "请手动编辑 user_data/config_live_3x.json 添加API密钥和其他必要配置"
}

# 主函数
main() {
    echo "========================================"
    echo "Bitget三倍杠杆回测全币种脚本"
    echo "========================================"
    
    check_environment
    get_all_pairs
    create_backtest_config
    download_data
    run_backtest
    analyze_results
    select_best_pairs
    create_live_config
    
    echo "========================================"
    log_success "脚本执行完成！"
    echo "========================================"
    
    echo "下一步操作："
    echo "1. 查看回测结果：user_data/backtest_results/"
    echo "2. 根据分析结果更新优质币种列表：user_data/pairlists/bitget_best_performers.json"
    echo "3. 配置实盘交易：user_data/config_live_3x.json"
    echo "4. 启动实盘交易：freqtrade trade --strategy ClucHAnix_5m --config user_data/config_live_3x.json"
}

# 执行主函数
main "$@"
