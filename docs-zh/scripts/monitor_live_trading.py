#!/usr/bin/env python3
"""
Bitget三倍杠杆实盘交易监控脚本
实时监控交易状态、账户余额和风险指标
"""

import requests
import json
import time
import pandas as pd
from datetime import datetime, timedelta
import argparse
import sys
from pathlib import Path
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class TradingMonitor:
    """交易监控器"""
    
    def __init__(self, api_url: str = "http://localhost:8080", 
                 username: str = None, password: str = None):
        """
        初始化监控器
        
        Args:
            api_url: FreqUI API地址
            username: API用户名
            password: API密码
        """
        self.api_url = api_url.rstrip('/')
        self.username = username
        self.password = password
        self.session = requests.Session()
        self.token = None
        
    def login(self) -> bool:
        """登录API"""
        if not self.username or not self.password:
            print("警告：未提供API认证信息，将尝试无认证访问")
            return True
            
        try:
            response = self.session.post(
                f"{self.api_url}/api/v1/token/login",
                json={"username": self.username, "password": self.password}
            )
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("access_token")
                self.session.headers.update({"Authorization": f"Bearer {self.token}"})
                print("API登录成功")
                return True
            else:
                print(f"API登录失败: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"API登录错误: {e}")
            return False
    
    def get_status(self) -> dict:
        """获取交易状态"""
        try:
            response = self.session.get(f"{self.api_url}/api/v1/status")
            if response.status_code == 200:
                return response.json()
            else:
                print(f"获取状态失败: {response.status_code}")
                return {}
        except Exception as e:
            print(f"获取状态错误: {e}")
            return {}
    
    def get_balance(self) -> dict:
        """获取账户余额"""
        try:
            response = self.session.get(f"{self.api_url}/api/v1/balance")
            if response.status_code == 200:
                return response.json()
            else:
                print(f"获取余额失败: {response.status_code}")
                return {}
        except Exception as e:
            print(f"获取余额错误: {e}")
            return {}
    
    def get_trades(self, limit: int = 50) -> list:
        """获取交易记录"""
        try:
            response = self.session.get(f"{self.api_url}/api/v1/trades?limit={limit}")
            if response.status_code == 200:
                data = response.json()
                return data.get("trades", [])
            else:
                print(f"获取交易记录失败: {response.status_code}")
                return []
        except Exception as e:
            print(f"获取交易记录错误: {e}")
            return []
    
    def get_profit(self) -> dict:
        """获取盈利统计"""
        try:
            response = self.session.get(f"{self.api_url}/api/v1/profit")
            if response.status_code == 200:
                return response.json()
            else:
                print(f"获取盈利统计失败: {response.status_code}")
                return {}
        except Exception as e:
            print(f"获取盈利统计错误: {e}")
            return {}
    
    def calculate_risk_metrics(self, trades: list) -> dict:
        """计算风险指标"""
        if not trades:
            return {}
        
        df = pd.DataFrame(trades)
        if df.empty:
            return {}
        
        # 转换数据类型
        df['profit_ratio'] = pd.to_numeric(df['profit_ratio'], errors='coerce')
        df['profit_abs'] = pd.to_numeric(df['profit_abs'], errors='coerce')
        
        # 计算风险指标
        total_trades = len(df)
        winning_trades = len(df[df['profit_ratio'] > 0])
        losing_trades = len(df[df['profit_ratio'] < 0])
        win_rate = winning_trades / total_trades if total_trades > 0 else 0
        
        # 计算最大回撤
        cumulative_returns = (1 + df['profit_ratio']).cumprod()
        running_max = cumulative_returns.expanding().max()
        drawdown = (cumulative_returns - running_max) / running_max
        max_drawdown = drawdown.min() if not drawdown.empty else 0
        
        # 计算夏普比率
        if df['profit_ratio'].std() > 0:
            sharpe_ratio = df['profit_ratio'].mean() / df['profit_ratio'].std()
        else:
            sharpe_ratio = 0
        
        return {
            'total_trades': total_trades,
            'winning_trades': winning_trades,
            'losing_trades': losing_trades,
            'win_rate': win_rate,
            'max_drawdown': max_drawdown,
            'sharpe_ratio': sharpe_ratio,
            'avg_profit': df['profit_ratio'].mean(),
            'total_profit': df['profit_ratio'].sum()
        }
    
    def generate_report(self) -> str:
        """生成监控报告"""
        report = []
        report.append("=" * 60)
        report.append(f"Bitget三倍杠杆交易监控报告")
        report.append(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("=" * 60)
        
        # 获取数据
        status = self.get_status()
        balance = self.get_balance()
        trades = self.get_trades(100)  # 获取最近100笔交易
        profit = self.get_profit()
        
        # 交易状态
        report.append("\n📊 交易状态:")
        if status:
            report.append(f"  机器人状态: {status.get('state', 'Unknown')}")
            report.append(f"  当前开仓数: {len(status.get('open_trades', []))}")
            report.append(f"  最大开仓数: {status.get('max_open_trades', 'Unknown')}")
            report.append(f"  策略: {status.get('strategy', 'Unknown')}")
        else:
            report.append("  ❌ 无法获取交易状态")
        
        # 账户余额
        report.append("\n💰 账户余额:")
        if balance:
            for currency, amount in balance.get('currencies', {}).items():
                if amount.get('total', 0) > 0:
                    report.append(f"  {currency}: {amount.get('total', 0):.4f}")
        else:
            report.append("  ❌ 无法获取账户余额")
        
        # 盈利统计
        report.append("\n📈 盈利统计:")
        if profit:
            report.append(f"  今日盈利: {profit.get('profit_today_abs', 0):.4f} USDT")
            report.append(f"  总盈利: {profit.get('profit_all_abs', 0):.4f} USDT")
            report.append(f"  总收益率: {profit.get('profit_all_ratio', 0)*100:.2f}%")
        else:
            report.append("  ❌ 无法获取盈利统计")
        
        # 风险指标
        report.append("\n⚠️ 风险指标:")
        risk_metrics = self.calculate_risk_metrics(trades)
        if risk_metrics:
            report.append(f"  总交易次数: {risk_metrics['total_trades']}")
            report.append(f"  胜率: {risk_metrics['win_rate']*100:.2f}%")
            report.append(f"  最大回撤: {risk_metrics['max_drawdown']*100:.2f}%")
            report.append(f"  夏普比率: {risk_metrics['sharpe_ratio']:.2f}")
            report.append(f"  平均收益率: {risk_metrics['avg_profit']*100:.2f}%")
        else:
            report.append("  ❌ 无法计算风险指标")
        
        # 当前持仓
        report.append("\n🔄 当前持仓:")
        if status and status.get('open_trades'):
            for trade in status['open_trades']:
                pair = trade.get('pair', 'Unknown')
                profit_ratio = trade.get('profit_ratio', 0) * 100
                profit_abs = trade.get('profit_abs', 0)
                report.append(f"  {pair}: {profit_ratio:.2f}% ({profit_abs:.4f} USDT)")
        else:
            report.append("  无当前持仓")
        
        # 风险警告
        report.append("\n🚨 风险警告:")
        warnings = []
        
        if risk_metrics.get('max_drawdown', 0) < -0.2:
            warnings.append("  ⚠️ 最大回撤超过20%，建议检查策略")
        
        if risk_metrics.get('win_rate', 1) < 0.3:
            warnings.append("  ⚠️ 胜率低于30%，建议检查策略参数")
        
        if len(status.get('open_trades', [])) >= status.get('max_open_trades', 0):
            warnings.append("  ⚠️ 已达到最大开仓数限制")
        
        if not warnings:
            warnings.append("  ✅ 暂无风险警告")
        
        report.extend(warnings)
        
        report.append("\n" + "=" * 60)
        
        return "\n".join(report)
    
    def save_report(self, report: str, filename: str = None):
        """保存报告到文件"""
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"trading_report_{timestamp}.txt"
        
        # 确保目录存在
        Path(filename).parent.mkdir(parents=True, exist_ok=True)
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"报告已保存到: {filename}")

def main():
    parser = argparse.ArgumentParser(description='监控Freqtrade实盘交易')
    parser.add_argument('--api-url', default='http://localhost:8080', help='FreqUI API地址')
    parser.add_argument('--username', help='API用户名')
    parser.add_argument('--password', help='API密码')
    parser.add_argument('--output-dir', default='user_data/reports', help='报告输出目录')
    parser.add_argument('--interval', type=int, default=300, help='监控间隔（秒）')
    parser.add_argument('--continuous', action='store_true', help='持续监控模式')
    
    args = parser.parse_args()
    
    # 创建输出目录
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 初始化监控器
    monitor = TradingMonitor(args.api_url, args.username, args.password)
    
    # 登录
    if not monitor.login():
        print("登录失败，退出程序")
        sys.exit(1)
    
    try:
        while True:
            # 生成报告
            report = monitor.generate_report()
            print(report)
            
            # 保存报告
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            report_file = output_dir / f"trading_report_{timestamp}.txt"
            monitor.save_report(report, str(report_file))
            
            if not args.continuous:
                break
            
            print(f"\n等待 {args.interval} 秒后进行下次监控...")
            time.sleep(args.interval)
            
    except KeyboardInterrupt:
        print("\n监控已停止")

if __name__ == "__main__":
    main()
