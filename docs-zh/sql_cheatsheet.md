# SQL 帮助

本页面包含一些帮助，如果您想查询您的 sqlite 数据库。

!!! Tip "其他数据库系统"
    要使用其他数据库系统如 PostgreSQL 或 MariaDB，您可以使用相同的查询，但您需要使用相应数据库系统的客户端。[点击这里](advanced-setup.md#使用不同的数据库系统) 了解如何使用 freqtrade 设置不同的数据库系统。

!!! Warning
    如果您不熟悉 SQL，在数据库上运行查询时应该非常小心。
    在运行任何查询之前，请务必确保备份您的数据库。

## 安装 sqlite3

Sqlite3 是一个基于终端的 sqlite 应用程序。
如果您觉得更舒适，可以随意使用可视化数据库编辑器如 SqliteBrowser。

### Ubuntu/Debian 安装

```bash
sudo apt-get install sqlite3
```

### 通过 docker 使用 sqlite3

freqtrade docker 镜像包含 sqlite3，因此您可以编辑数据库而无需在主机系统上安装任何东西。

``` bash
docker compose exec freqtrade /bin/bash
sqlite3 <database-file>.sqlite
```

## 打开数据库

```bash
sqlite3
.open <filepath>
```

## 表结构

### 列出表

```bash
.tables
```

### 显示表结构

```bash
.schema <table_name>
```

### 获取表中的所有交易

```sql
SELECT * FROM trades;
```

## 破坏性查询

写入数据库的查询。
这些查询通常不应该是必需的，因为 freqtrade 尝试自己处理所有数据库操作 - 或通过 API 或 telegram 命令公开它们。

!!! Warning
    请确保在运行以下任何查询之前备份您的数据库。

!!! Danger
    您也应该**永远不要**在机器人连接到数据库时运行任何写入查询（`update`、`insert`、`delete`）。
    这可能并且将导致数据损坏 - 很可能没有恢复的可能性。

### 修复在交易所手动退出后仍然开放的交易

!!! Warning
    在交易所手动卖出交易对不会被机器人检测到，它仍然会尝试卖出。只要可能，应该使用 /forceexit <tradeid> 来完成同样的事情。
    强烈建议在进行任何手动更改之前备份您的数据库文件。

!!! Note
    在 /forceexit 之后这应该不是必需的，因为强制退出订单在机器人的下一次迭代中会自动关闭。

```sql
UPDATE trades
SET is_open=0,
  close_date=<close_date>,
  close_rate=<close_rate>,
  close_profit = close_rate / open_rate - 1,
  close_profit_abs = (amount * <close_rate> * (1 - fee_close) - (amount * (open_rate * (1 - fee_open)))),
  exit_reason=<exit_reason>
WHERE id=<trade_ID_to_update>;
```

#### 示例

```sql
UPDATE trades
SET is_open=0,
  close_date='2020-06-20 03:08:45.103418',
  close_rate=0.19638016,
  close_profit=0.0496,
  close_profit_abs = (amount * 0.19638016 * (1 - fee_close) - (amount * (open_rate * (1 - fee_open)))),
  exit_reason='force_exit'
WHERE id=31;
```

### 删除交易

```sql
DELETE FROM trades WHERE id = <trade_ID_to_delete>;
```

!!! Warning "删除交易"
    删除交易将永久从数据库中删除交易记录。这个操作无法撤销。

### 更新交易信息

```sql
UPDATE trades 
SET stake_amount = <new_stake_amount>
WHERE id = <trade_ID_to_update>;
```

## 有用的查询

### 查看最近的交易

```sql
SELECT * FROM trades 
ORDER BY open_date DESC 
LIMIT 10;
```

### 查看盈利的交易

```sql
SELECT * FROM trades 
WHERE close_profit > 0 
ORDER BY close_profit DESC;
```

### 查看亏损的交易

```sql
SELECT * FROM trades 
WHERE close_profit < 0 
ORDER BY close_profit ASC;
```

### 按交易对统计

```sql
SELECT pair, 
       COUNT(*) as trade_count,
       AVG(close_profit) as avg_profit,
       SUM(close_profit_abs) as total_profit
FROM trades 
WHERE is_open = 0
GROUP BY pair
ORDER BY total_profit DESC;
```

### 查看开放的交易

```sql
SELECT * FROM trades 
WHERE is_open = 1;
```

### 按月份统计利润

```sql
SELECT strftime('%Y-%m', close_date) as month,
       COUNT(*) as trade_count,
       SUM(close_profit_abs) as total_profit
FROM trades 
WHERE is_open = 0
GROUP BY month
ORDER BY month;
```

## 数据库维护

### 备份数据库

```bash
# 创建数据库备份
cp tradesv3.sqlite tradesv3_backup_$(date +%Y%m%d).sqlite
```

### 检查数据库完整性

```sql
PRAGMA integrity_check;
```

### 优化数据库

```sql
VACUUM;
```

!!! Note "定期维护"
    建议定期备份数据库并运行完整性检查，特别是在进行任何手动修改之前。
