#!/usr/bin/env python3
"""
Bitget三倍杠杆回测结果分析脚本
自动分析回测结果，筛选出表现最好的币种
"""

import json
import pandas as pd
import numpy as np
from pathlib import Path
import argparse
from typing import Dict, List, Tuple
import sys

class BacktestAnalyzer:
    """回测结果分析器"""
    
    def __init__(self, backtest_file: str):
        """
        初始化分析器
        
        Args:
            backtest_file: 回测结果文件路径
        """
        self.backtest_file = Path(backtest_file)
        self.data = None
        self.trades_df = None
        self.pair_stats = None
        
    def load_data(self) -> bool:
        """加载回测数据"""
        try:
            with open(self.backtest_file, 'r', encoding='utf-8') as f:
                self.data = json.load(f)
            
            # 提取交易数据
            if 'trades' in self.data:
                self.trades_df = pd.DataFrame(self.data['trades'])
                if not self.trades_df.empty:
                    self.trades_df['open_date'] = pd.to_datetime(self.trades_df['open_date'])
                    self.trades_df['close_date'] = pd.to_datetime(self.trades_df['close_date'])
                    self.trades_df['profit_ratio'] = self.trades_df['profit_ratio'].astype(float)
                    self.trades_df['profit_abs'] = self.trades_df['profit_abs'].astype(float)
                    return True
            
            print("错误：回测文件中没有找到交易数据")
            return False
            
        except Exception as e:
            print(f"错误：加载回测文件失败 - {e}")
            return False
    
    def calculate_pair_statistics(self) -> pd.DataFrame:
        """计算每个交易对的统计数据"""
        if self.trades_df is None or self.trades_df.empty:
            print("错误：没有交易数据可分析")
            return pd.DataFrame()
        
        # 按交易对分组计算统计数据
        pair_stats = []
        
        for pair in self.trades_df['pair'].unique():
            pair_trades = self.trades_df[self.trades_df['pair'] == pair]
            
            # 基本统计
            total_trades = len(pair_trades)
            winning_trades = len(pair_trades[pair_trades['profit_ratio'] > 0])
            losing_trades = len(pair_trades[pair_trades['profit_ratio'] < 0])
            
            # 收益统计
            total_profit_ratio = pair_trades['profit_ratio'].sum()
            total_profit_abs = pair_trades['profit_abs'].sum()
            avg_profit_ratio = pair_trades['profit_ratio'].mean()
            
            # 胜率
            win_rate = winning_trades / total_trades if total_trades > 0 else 0
            
            # 最大单笔盈利和亏损
            max_profit = pair_trades['profit_ratio'].max()
            max_loss = pair_trades['profit_ratio'].min()
            
            # 平均持仓时间（小时）
            pair_trades['duration_hours'] = (pair_trades['close_date'] - pair_trades['open_date']).dt.total_seconds() / 3600
            avg_duration = pair_trades['duration_hours'].mean()
            
            # 计算夏普比率（简化版本）
            if pair_trades['profit_ratio'].std() > 0:
                sharpe_ratio = pair_trades['profit_ratio'].mean() / pair_trades['profit_ratio'].std()
            else:
                sharpe_ratio = 0
            
            # 计算最大回撤
            cumulative_returns = (1 + pair_trades['profit_ratio']).cumprod()
            running_max = cumulative_returns.expanding().max()
            drawdown = (cumulative_returns - running_max) / running_max
            max_drawdown = drawdown.min()
            
            pair_stats.append({
                'pair': pair,
                'total_trades': total_trades,
                'winning_trades': winning_trades,
                'losing_trades': losing_trades,
                'win_rate': win_rate,
                'total_profit_ratio': total_profit_ratio,
                'total_profit_abs': total_profit_abs,
                'avg_profit_ratio': avg_profit_ratio,
                'max_profit': max_profit,
                'max_loss': max_loss,
                'avg_duration_hours': avg_duration,
                'sharpe_ratio': sharpe_ratio,
                'max_drawdown': max_drawdown
            })
        
        self.pair_stats = pd.DataFrame(pair_stats)
        return self.pair_stats
    
    def filter_best_pairs(self, 
                         min_trades: int = 5,
                         min_win_rate: float = 0.4,
                         min_profit_ratio: float = 0.05,
                         max_drawdown: float = -0.3,
                         min_sharpe: float = 0.5,
                         top_n: int = 20) -> List[str]:
        """
        筛选最佳表现的交易对
        
        Args:
            min_trades: 最少交易次数
            min_win_rate: 最低胜率
            min_profit_ratio: 最低总收益率
            max_drawdown: 最大回撤（负数）
            min_sharpe: 最低夏普比率
            top_n: 返回前N个币种
            
        Returns:
            筛选出的交易对列表
        """
        if self.pair_stats is None:
            self.calculate_pair_statistics()
        
        # 应用筛选条件
        filtered = self.pair_stats[
            (self.pair_stats['total_trades'] >= min_trades) &
            (self.pair_stats['win_rate'] >= min_win_rate) &
            (self.pair_stats['total_profit_ratio'] >= min_profit_ratio) &
            (self.pair_stats['max_drawdown'] >= max_drawdown) &
            (self.pair_stats['sharpe_ratio'] >= min_sharpe)
        ]
        
        # 按总收益率排序，取前N个
        best_pairs = filtered.nlargest(top_n, 'total_profit_ratio')
        
        return best_pairs['pair'].tolist()
    
    def generate_report(self, output_file: str = None) -> str:
        """生成分析报告"""
        if self.pair_stats is None:
            self.calculate_pair_statistics()
        
        report = []
        report.append("=" * 80)
        report.append("Bitget三倍杠杆回测结果分析报告")
        report.append("=" * 80)
        report.append("")
        
        # 总体统计
        total_trades = len(self.trades_df)
        total_pairs = len(self.pair_stats)
        overall_profit = self.trades_df['profit_ratio'].sum()
        overall_win_rate = len(self.trades_df[self.trades_df['profit_ratio'] > 0]) / total_trades
        
        report.append("总体统计:")
        report.append(f"  交易对数量: {total_pairs}")
        report.append(f"  总交易次数: {total_trades}")
        report.append(f"  总收益率: {overall_profit:.4f} ({overall_profit*100:.2f}%)")
        report.append(f"  总体胜率: {overall_win_rate:.4f} ({overall_win_rate*100:.2f}%)")
        report.append("")
        
        # 前20名表现最好的交易对
        top_20 = self.pair_stats.nlargest(20, 'total_profit_ratio')
        report.append("前20名表现最好的交易对:")
        report.append("-" * 80)
        report.append(f"{'排名':<4} {'交易对':<15} {'交易次数':<8} {'胜率':<8} {'总收益率':<12} {'夏普比率':<10} {'最大回撤':<10}")
        report.append("-" * 80)
        
        for i, (_, row) in enumerate(top_20.iterrows(), 1):
            report.append(f"{i:<4} {row['pair']:<15} {row['total_trades']:<8} "
                         f"{row['win_rate']:.2%}   {row['total_profit_ratio']:.4f}     "
                         f"{row['sharpe_ratio']:.2f}      {row['max_drawdown']:.2%}")
        
        report.append("")
        
        # 筛选建议
        best_pairs = self.filter_best_pairs()
        report.append(f"推荐的优质交易对 (共{len(best_pairs)}个):")
        report.append("-" * 40)
        for pair in best_pairs:
            report.append(f"  {pair}")
        
        report_text = "\n".join(report)
        
        # 保存报告
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(report_text)
            print(f"分析报告已保存到: {output_file}")
        
        return report_text
    
    def save_best_pairs_json(self, output_file: str, **filter_kwargs):
        """保存最佳交易对到JSON文件"""
        best_pairs = self.filter_best_pairs(**filter_kwargs)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(best_pairs, f, indent=2, ensure_ascii=False)
        
        print(f"最佳交易对列表已保存到: {output_file}")
        print(f"共筛选出 {len(best_pairs)} 个优质交易对")

def main():
    parser = argparse.ArgumentParser(description='分析Freqtrade回测结果')
    parser.add_argument('backtest_file', help='回测结果JSON文件路径')
    parser.add_argument('--output-dir', default='user_data/analysis', help='输出目录')
    parser.add_argument('--min-trades', type=int, default=5, help='最少交易次数')
    parser.add_argument('--min-win-rate', type=float, default=0.4, help='最低胜率')
    parser.add_argument('--min-profit', type=float, default=0.05, help='最低总收益率')
    parser.add_argument('--max-drawdown', type=float, default=-0.3, help='最大回撤')
    parser.add_argument('--min-sharpe', type=float, default=0.5, help='最低夏普比率')
    parser.add_argument('--top-n', type=int, default=20, help='选择前N个币种')
    
    args = parser.parse_args()
    
    # 创建输出目录
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 初始化分析器
    analyzer = BacktestAnalyzer(args.backtest_file)
    
    # 加载数据
    if not analyzer.load_data():
        sys.exit(1)
    
    # 生成报告
    report_file = output_dir / f"analysis_report_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.txt"
    report = analyzer.generate_report(str(report_file))
    print(report)
    
    # 保存最佳交易对
    best_pairs_file = output_dir / "bitget_best_performers.json"
    analyzer.save_best_pairs_json(
        str(best_pairs_file),
        min_trades=args.min_trades,
        min_win_rate=args.min_win_rate,
        min_profit_ratio=args.min_profit,
        max_drawdown=args.max_drawdown,
        min_sharpe=args.min_sharpe,
        top_n=args.top_n
    )

if __name__ == "__main__":
    main()
