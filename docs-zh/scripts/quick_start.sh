#!/bin/bash

# Freqtrade Bitget三倍杠杆交易快速启动脚本
# 这个脚本提供了一个交互式菜单，帮助用户快速执行各种操作

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 显示标题
show_title() {
    clear
    echo -e "${CYAN}========================================"
    echo -e "  Freqtrade Bitget三倍杠杆交易工具"
    echo -e "========================================"
    echo -e "${NC}"
}

# 显示菜单
show_menu() {
    echo -e "${YELLOW}请选择要执行的操作：${NC}"
    echo ""
    echo -e "${GREEN}1.${NC} 执行完整的三倍杠杆回测流程"
    echo -e "${GREEN}2.${NC} 分析现有回测结果"
    echo -e "${GREEN}3.${NC} 监控实盘交易（单次）"
    echo -e "${GREEN}4.${NC} 启动持续监控"
    echo -e "${GREEN}5.${NC} 获取所有Bitget合约交易对"
    echo -e "${GREEN}6.${NC} 创建实盘交易配置"
    echo -e "${GREEN}7.${NC} 启动实盘交易"
    echo -e "${GREEN}8.${NC} 查看帮助文档"
    echo -e "${RED}0.${NC} 退出"
    echo ""
    echo -n -e "${BLUE}请输入选项 [0-8]: ${NC}"
}

# 检查环境
check_environment() {
    echo -e "${BLUE}[INFO]${NC} 检查环境..."
    
    if ! command -v freqtrade &> /dev/null; then
        echo -e "${RED}[ERROR]${NC} Freqtrade未安装或不在PATH中"
        exit 1
    fi
    
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}[ERROR]${NC} Python3未安装或不在PATH中"
        exit 1
    fi
    
    if [ ! -d "user_data" ]; then
        echo -e "${RED}[ERROR]${NC} user_data目录不存在，请确保在freqtrade根目录下运行此脚本"
        exit 1
    fi
    
    echo -e "${GREEN}[SUCCESS]${NC} 环境检查通过"
}

# 执行完整回测流程
run_full_backtest() {
    echo -e "${BLUE}[INFO]${NC} 开始执行完整的三倍杠杆回测流程..."
    echo ""
    
    if [ -f "docs-zh/scripts/bitget_3x_leverage_backtest.sh" ]; then
        ./docs-zh/scripts/bitget_3x_leverage_backtest.sh
    else
        echo -e "${RED}[ERROR]${NC} 回测脚本不存在"
        return 1
    fi
    
    echo ""
    echo -e "${GREEN}[SUCCESS]${NC} 回测流程完成"
    read -p "按任意键继续..."
}

# 分析回测结果
analyze_results() {
    echo -e "${BLUE}[INFO]${NC} 分析回测结果..."
    echo ""
    
    # 查找最新的回测结果文件
    LATEST_FILE=$(find user_data/backtest_results -name "all_pairs_3x_leverage_*.json" -type f -printf '%T@ %p\n' 2>/dev/null | sort -n | tail -1 | cut -d' ' -f2-)
    
    if [ -z "$LATEST_FILE" ]; then
        echo -e "${RED}[ERROR]${NC} 未找到回测结果文件"
        echo "请先执行回测或手动指定文件路径"
        read -p "请输入回测结果文件路径: " MANUAL_FILE
        if [ -f "$MANUAL_FILE" ]; then
            LATEST_FILE="$MANUAL_FILE"
        else
            echo -e "${RED}[ERROR]${NC} 文件不存在"
            return 1
        fi
    fi
    
    echo -e "${BLUE}[INFO]${NC} 使用文件: $LATEST_FILE"
    
    if [ -f "docs-zh/scripts/analyze_backtest_results.py" ]; then
        python3 docs-zh/scripts/analyze_backtest_results.py "$LATEST_FILE"
    else
        echo -e "${RED}[ERROR]${NC} 分析脚本不存在"
        return 1
    fi
    
    echo ""
    read -p "按任意键继续..."
}

# 监控实盘交易
monitor_trading() {
    echo -e "${BLUE}[INFO]${NC} 监控实盘交易..."
    echo ""
    
    if [ -f "docs-zh/scripts/monitor_live_trading.py" ]; then
        python3 docs-zh/scripts/monitor_live_trading.py
    else
        echo -e "${RED}[ERROR]${NC} 监控脚本不存在"
        return 1
    fi
    
    echo ""
    read -p "按任意键继续..."
}

# 启动持续监控
start_continuous_monitoring() {
    echo -e "${BLUE}[INFO]${NC} 启动持续监控..."
    echo ""
    
    read -p "请输入监控间隔（秒，默认300）: " INTERVAL
    INTERVAL=${INTERVAL:-300}
    
    if [ -f "docs-zh/scripts/monitor_live_trading.py" ]; then
        echo -e "${YELLOW}[INFO]${NC} 开始持续监控，按Ctrl+C停止..."
        python3 docs-zh/scripts/monitor_live_trading.py --continuous --interval "$INTERVAL"
    else
        echo -e "${RED}[ERROR]${NC} 监控脚本不存在"
        return 1
    fi
}

# 获取所有交易对
get_all_pairs() {
    echo -e "${BLUE}[INFO]${NC} 获取所有Bitget合约交易对..."
    echo ""
    
    # 创建临时配置
    cat > user_data/config_temp.json << 'EOF'
{
    "trading_mode": "futures",
    "stake_currency": "USDT",
    "exchange": {
        "name": "bitget",
        "ccxt_config": {
            "options": {
                "defaultType": "swap"
            }
        }
    },
    "pairlists": [
        {
            "method": "VolumePairList",
            "number_assets": 200
        }
    ]
}
EOF
    
    freqtrade test-pairlist -c user_data/config_temp.json --quote USDT --print-json > user_data/pairlists/bitget_all_futures.json
    
    PAIR_COUNT=$(jq length user_data/pairlists/bitget_all_futures.json 2>/dev/null || echo "0")
    echo -e "${GREEN}[SUCCESS]${NC} 成功获取 $PAIR_COUNT 个USDT合约交易对"
    echo "保存位置: user_data/pairlists/bitget_all_futures.json"
    
    # 清理临时文件
    rm -f user_data/config_temp.json
    
    echo ""
    read -p "按任意键继续..."
}

# 创建实盘配置
create_live_config() {
    echo -e "${BLUE}[INFO]${NC} 创建实盘交易配置..."
    echo ""
    
    if [ ! -f "user_data/config_backtest_3x.json" ]; then
        echo -e "${RED}[ERROR]${NC} 回测配置文件不存在，请先执行回测"
        return 1
    fi
    
    cp user_data/config_backtest_3x.json user_data/config_live_3x.json
    
    echo -e "${YELLOW}[WARNING]${NC} 请手动编辑以下配置："
    echo "1. 添加API密钥信息"
    echo "2. 设置 dry_run: false"
    echo "3. 配置Telegram通知"
    echo "4. 设置合适的交易对列表"
    echo ""
    echo "配置文件位置: user_data/config_live_3x.json"
    
    read -p "是否现在打开配置文件进行编辑？(y/n): " EDIT_CONFIG
    if [[ $EDIT_CONFIG =~ ^[Yy]$ ]]; then
        ${EDITOR:-nano} user_data/config_live_3x.json
    fi
    
    echo ""
    read -p "按任意键继续..."
}

# 启动实盘交易
start_live_trading() {
    echo -e "${BLUE}[INFO]${NC} 启动实盘交易..."
    echo ""
    
    if [ ! -f "user_data/config_live_3x.json" ]; then
        echo -e "${RED}[ERROR]${NC} 实盘配置文件不存在，请先创建配置"
        return 1
    fi
    
    echo -e "${RED}[WARNING]${NC} 即将启动实盘交易！"
    echo "请确保："
    echo "1. 已正确配置API密钥"
    echo "2. 已设置合理的风险参数"
    echo "3. 账户中有足够的资金"
    echo "4. 已充分测试策略"
    echo ""
    
    read -p "确认启动实盘交易？(yes/no): " CONFIRM
    if [[ $CONFIRM == "yes" ]]; then
        freqtrade trade \
            --strategy ClucHAnix_5m \
            --config user_data/config_live_3x.json \
            --logfile user_data/logs/freqtrade_live_3x.log
    else
        echo "已取消启动"
    fi
    
    echo ""
    read -p "按任意键继续..."
}

# 显示帮助
show_help() {
    echo -e "${BLUE}[INFO]${NC} 帮助文档"
    echo ""
    echo "详细文档位置："
    echo "- 完整指南: docs-zh/freqtrade-complete-guide.md"
    echo "- 脚本说明: docs-zh/scripts/README.md"
    echo ""
    echo "主要文件位置："
    echo "- 配置文件: user_data/config_*.json"
    echo "- 交易对列表: user_data/pairlists/"
    echo "- 回测结果: user_data/backtest_results/"
    echo "- 日志文件: user_data/logs/"
    echo ""
    echo "常用命令："
    echo "- 回测: freqtrade backtesting --strategy ClucHAnix_5m -c config.json"
    echo "- 实盘: freqtrade trade --strategy ClucHAnix_5m -c config.json"
    echo "- 监控: python docs-zh/scripts/monitor_live_trading.py"
    echo ""
    read -p "按任意键继续..."
}

# 主循环
main() {
    check_environment
    
    while true; do
        show_title
        show_menu
        read choice
        
        case $choice in
            1) run_full_backtest ;;
            2) analyze_results ;;
            3) monitor_trading ;;
            4) start_continuous_monitoring ;;
            5) get_all_pairs ;;
            6) create_live_config ;;
            7) start_live_trading ;;
            8) show_help ;;
            0) echo -e "${GREEN}再见！${NC}"; exit 0 ;;
            *) echo -e "${RED}无效选项，请重新选择${NC}"; sleep 2 ;;
        esac
    done
}

# 运行主程序
main "$@"
