```
用法: freqtrade backtesting [-h] [-v] [--no-color] [--logfile FILE] [-V]
                             [-c PATH] [-d PATH] [--userdir PATH] [-s NAME]
                             [--strategy-path PATH]
                             [--recursive-strategy-search]
                             [--freqaimodel NAME] [--freqaimodel-path PATH]
                             [-i TIMEFRAME] [--timerange TIMERANGE]
                             [--data-format-ohlcv {json,jsongz,feather,parquet}]
                             [--max-open-trades INT]
                             [--stake-amount STAKE_AMOUNT] [--fee FLOAT]
                             [-p PAIRS [PAIRS ...]] [--eps]
                             [--enable-protections]
                             [--dry-run-wallet DRY_RUN_WALLET]
                             [--timeframe-detail TIMEFRAME_DETAIL]
                             [--strategy-list STRATEGY_LIST [STRATEGY_LIST ...]]
                             [--export {none,trades,signals}]
                             [--export-filename PATH]
                             [--breakdown {day,week,month,year} [{day,week,month,year} ...]]
                             [--cache {none,day,week,month}]
                             [--freqai-backtest-live-models] [--notes TEXT]

选项:
  -h, --help            显示此帮助信息并退出
  -i TIMEFRAME, --timeframe TIMEFRAME
                        指定时间框架 (`1m`, `5m`, `30m`, `1h`, `1d`)。
  --timerange TIMERANGE
                        指定要使用的数据时间范围。
  --data-format-ohlcv {json,jsongz,feather,parquet}
                        下载的蜡烛图 (OHLCV) 数据的存储格式。
                        (默认: `feather`)。
  --max-open-trades INT
                        覆盖 `max_open_trades` 配置设置的值。
  --stake-amount STAKE_AMOUNT
                        覆盖 `stake_amount` 配置设置的值。
  --fee FLOAT           指定费率比例。将应用两次（交易入场和出场）。
  -p PAIRS [PAIRS ...], --pairs PAIRS [PAIRS ...]
                        将命令限制为这些交易对。交易对用空格分隔。
  --eps, --enable-position-stacking
                        允许多次购买同一交易对（头寸堆叠）。
  --enable-protections, --enableprotections
                        为回测启用保护机制。这将大大减慢回测速度，
                        但会包含配置的保护机制
  --dry-run-wallet DRY_RUN_WALLET, --starting-balance DRY_RUN_WALLET
                        起始余额，用于回测/超参数优化和模拟运行。
  --timeframe-detail TIMEFRAME_DETAIL
                        指定用于入场/出场分析的详细时间框架。
  --strategy-list STRATEGY_LIST [STRATEGY_LIST ...]
                        提供要回测的策略列表。
  --export {none,trades,signals}
                        导出回测结果 (默认: trades)。
  --export-filename PATH
                        将回测结果保存到指定文件。
  --breakdown {day,week,month,year} [{day,week,month,year} ...]
                        显示指定时间段的回测结果细分。
  --cache {none,day,week,month}
                        使用缓存的回测结果 (默认: day)。
  --freqai-backtest-live-models
                        在回测期间运行 FreqAI 实时模型。
  --notes TEXT          为此回测运行添加注释。
```
