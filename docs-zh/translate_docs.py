#!/usr/bin/env python3
"""
Freqtrade 文档翻译脚本
用于批量翻译英文文档为中文文档
"""

import os
import shutil
from pathlib import Path

# 需要翻译的重要文档列表
IMPORTANT_DOCS = [
    'bot-basics.md',
    'bot-usage.md', 
    'data-analysis.md',
    'data-download.md',
    'exchanges.md',
    'faq.md',
    'freq-ui.md',
    'freqai.md',
    'freqai-configuration.md',
    'freqai-running.md',
    'hyperopt.md',
    'leverage.md',
    'plotting.md',
    'rest-api.md',
    'stoploss.md',
    'strategy-advanced.md',
    'strategy-customization.md',
    'telegram-usage.md',
    'utils.md',
    'windows_installation.md'
]

# 命令文档列表
COMMAND_DOCS = [
    'commands/backtesting.md',
    'commands/download-data.md',
    'commands/hyperopt.md',
    'commands/new-config.md',
    'commands/new-strategy.md',
    'commands/list-strategies.md',
    'commands/show-config.md',
    'commands/webserver.md'
]

def copy_assets():
    """复制资源文件"""
    source_assets = Path('docs/assets')
    target_assets = Path('docs-zh/assets')
    
    if source_assets.exists():
        if target_assets.exists():
            shutil.rmtree(target_assets)
        shutil.copytree(source_assets, target_assets)
        print(f"已复制资源文件到 {target_assets}")

def create_placeholder_docs():
    """为重要文档创建占位符"""
    docs_zh = Path('docs-zh')
    
    # 创建主要文档的占位符
    for doc in IMPORTANT_DOCS:
        target_file = docs_zh / doc
        target_file.parent.mkdir(parents=True, exist_ok=True)
        
        if not target_file.exists():
            with open(target_file, 'w', encoding='utf-8') as f:
                f.write(f"# {doc.replace('.md', '').replace('-', ' ').title()}\n\n")
                f.write("<!-- 此文档正在翻译中，请参考英文原版 -->\n\n")
                f.write(f"请参考英文原版文档：[{doc}](../docs/{doc})\n\n")
                f.write("## 翻译状态\n\n")
                f.write("- [ ] 待翻译\n")
                f.write("- [ ] 翻译中\n") 
                f.write("- [ ] 已完成\n")
            print(f"已创建占位符：{target_file}")
    
    # 创建命令文档的占位符
    for doc in COMMAND_DOCS:
        target_file = docs_zh / doc
        target_file.parent.mkdir(parents=True, exist_ok=True)
        
        if not target_file.exists():
            with open(target_file, 'w', encoding='utf-8') as f:
                doc_name = doc.split('/')[-1].replace('.md', '').replace('-', ' ').title()
                f.write(f"# {doc_name}\n\n")
                f.write("<!-- 此命令文档正在翻译中，请参考英文原版 -->\n\n")
                f.write(f"请参考英文原版文档：[{doc}](../../docs/{doc})\n\n")
                f.write("## 翻译状态\n\n")
                f.write("- [ ] 待翻译\n")
                f.write("- [ ] 翻译中\n")
                f.write("- [ ] 已完成\n")
            print(f"已创建命令占位符：{target_file}")

def create_mkdocs_config():
    """创建 MkDocs 配置文件用于中文文档"""
    config_content = """
site_name: Freqtrade 中文文档
site_description: Freqtrade 加密货币交易机器人中文文档
site_url: https://freqtrade.io/zh/

nav:
  - 主页: index.md
  - 快速开始:
    - Docker 快速入门: docker_quickstart.md
    - 安装指南: installation.md
    - Windows 安装: windows_installation.md
  - 配置:
    - 机器人配置: configuration.md
    - 机器人基础: bot-basics.md
    - 机器人使用: bot-usage.md
  - 策略开发:
    - 策略入门 101: strategy-101.md
    - 策略自定义: strategy-customization.md
    - 策略高级功能: strategy-advanced.md
  - 回测和分析:
    - 回测: backtesting.md
    - 数据分析: data-analysis.md
    - 数据下载: data-download.md
    - 绘图: plotting.md
  - FreqAI 机器学习:
    - FreqAI 介绍: freqai.md
    - FreqAI 配置: freqai-configuration.md
    - FreqAI 运行: freqai-running.md
  - 优化:
    - 超参数优化: hyperopt.md
  - 交易所和交易:
    - 支持的交易所: exchanges.md
    - 杠杆交易: leverage.md
    - 止损: stoploss.md
  - 用户界面和 API:
    - FreqUI: freq-ui.md
    - REST API: rest-api.md
    - Telegram 使用: telegram-usage.md
  - 工具和实用程序:
    - 命令行工具: commands/trade.md
    - 实用程序: utils.md
  - 参考:
    - 常见问题: faq.md

theme:
  name: material
  language: zh
  features:
    - navigation.tabs
    - navigation.sections
    - navigation.expand
    - navigation.top
    - search.highlight
    - search.share
  palette:
    - scheme: default
      primary: blue
      accent: blue
      toggle:
        icon: material/brightness-7
        name: 切换到深色模式
    - scheme: slate
      primary: blue
      accent: blue
      toggle:
        icon: material/brightness-4
        name: 切换到浅色模式

markdown_extensions:
  - admonition
  - pymdownx.details
  - pymdownx.superfences
  - pymdownx.tabbed
  - pymdownx.highlight
  - pymdownx.inlinehilite
  - pymdownx.snippets
  - toc:
      permalink: true

plugins:
  - search:
      lang: zh
"""
    
    with open('docs-zh/mkdocs.yml', 'w', encoding='utf-8') as f:
        f.write(config_content.strip())
    print("已创建 MkDocs 配置文件")

def main():
    """主函数"""
    print("开始创建 Freqtrade 中文文档结构...")
    
    # 复制资源文件
    copy_assets()
    
    # 创建占位符文档
    create_placeholder_docs()
    
    # 创建 MkDocs 配置
    create_mkdocs_config()
    
    print("\n文档结构创建完成！")
    print("\n已创建的文档：")
    print("- 主页 (index.md)")
    print("- Docker 快速入门 (docker_quickstart.md)")
    print("- 安装指南 (installation.md)")
    print("- 配置文档 (configuration.md)")
    print("- 策略入门 (strategy-101.md)")
    print("- 回测文档 (backtesting.md)")
    print("- 交易命令 (commands/trade.md)")
    print("- 其他重要文档的占位符")
    
    print("\n下一步：")
    print("1. 逐个翻译占位符文档")
    print("2. 运行 'mkdocs serve' 预览文档")
    print("3. 完善翻译内容")

if __name__ == "__main__":
    main()
