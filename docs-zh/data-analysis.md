# 使用 Jupyter notebooks 分析机器人数据

您可以使用 Jupyter notebooks 轻松分析回测结果和交易历史。在使用 `freqtrade create-userdir --userdir user_data` 初始化用户目录后，示例 notebooks 位于 `user_data/notebooks/`。

## 使用 docker 快速开始

Freqtrade 提供了一个 docker-compose 文件，可以启动 jupyter lab 服务器。
您可以使用以下命令运行此服务器：`docker compose -f docker/docker-compose-jupyter.yml up`

这将创建一个运行 jupyter lab 的 docker 容器，可以通过 `https://127.0.0.1:8888/lab` 访问。
请使用启动后在控制台中打印的链接以简化登录。

有关更多信息，请访问[使用 Docker 进行数据分析](docker_quickstart.md#使用-docker-compose-进行数据分析)部分。

### 专业提示

* 有关使用说明，请参见 [jupyter.org](https://jupyter.org/documentation)。
* 不要忘记从您的 conda 或 venv 环境中启动 Jupyter notebook 服务器，或使用 [nb_conda_kernels](https://github.com/Anaconda-Platform/nb_conda_kernels)*
* 在使用前复制示例 notebook，这样您的更改不会在下次 freqtrade 更新时被覆盖。

### 在系统范围的 Jupyter 安装中使用虚拟环境

有时可能希望使用系统范围的 Jupyter notebook 安装，并使用来自虚拟环境的 jupyter 内核。
这可以防止您在每个系统上多次安装完整的 jupyter 套件，并提供在任务之间轻松切换的方法（freqtrade / 其他分析任务）。

为了使其工作，首先激活您的虚拟环境并运行以下命令：

``` bash
# 激活虚拟环境
source .venv/bin/activate

pip install ipykernel
ipython kernel install --user --name=freqtrade
# 重启 jupyter (lab / notebook)
# 在 notebook 中选择内核 "freqtrade"
```

!!! Note
    提供此部分是为了完整性，Freqtrade 团队不会为此设置的问题提供完全支持，并将建议直接在虚拟环境中安装 Jupyter，因为这是启动和运行 jupyter notebooks 的最简单方法。有关此设置的帮助，请参考 [Project Jupyter](https://jupyter.org/) [文档](https://jupyter.org/documentation)或[帮助频道](https://jupyter.org/community)。

!!! Warning
    某些任务在 notebooks 中不能很好地工作。例如，任何使用异步执行的东西对 Jupyter 来说都是问题。此外，freqtrade 的主要入口点是 shell cli，因此在 notebook 中使用纯 python 会绕过为辅助函数提供所需对象和参数的参数。您可能需要手动设置这些值或创建预期的对象。

## 推荐的工作流程

| 任务 | 工具 |
  --- | ---
机器人操作 | CLI
重复性任务 | Shell 脚本
数据分析和可视化 | Notebook

1. 使用 CLI 来

    * 下载历史数据
    * 运行回测
    * 使用实时数据运行
    * 导出结果

1. 将这些操作收集在 shell 脚本中

    * 保存带参数的复杂命令
    * 执行多步操作
    * 自动化测试策略和准备分析数据

1. 使用 notebook 来

    * 可视化数据
    * 处理和绘图以生成洞察

## 示例实用代码片段

### 更改目录到根目录

Jupyter notebooks 从 notebook 目录执行。以下代码片段搜索项目根目录，以便相对路径保持一致。

```python
import os
from pathlib import Path

# 更改目录
# 修改此单元格以确保输出显示正确的路径。
# 定义相对于单元格输出中显示的项目根目录的所有路径
project_root = "somedir/freqtrade"
i=0
try:
    os.chdir(project_root)
    assert Path('LICENSE').is_file()
except:
    while i<4 and (not Path('LICENSE').is_file()):
        os.chdir(Path(Path.cwd(), '../'))
        i+=1
    project_root = Path.cwd()
print(Path.cwd())
```

### 加载多个配置文件

此选项对于检查传入多个配置的结果很有用。
这也将运行整个配置初始化，因此配置完全初始化以传递给其他方法。

```python
import json
from freqtrade.configuration import Configuration

# 从多个文件加载配置
config = Configuration.from_files(["config1.json", "config2.json"])

# 显示内存中的配置
print(json.dumps(config['original_config'], indent=2))
```

对于交互式环境，有一个额外的配置指定 `user_data_dir` 并最后传入，这样您就不必在运行机器人时更改目录。
最好避免相对路径，因为这从 jupyter notebook 的存储位置开始，除非目录被更改。

```json
{
    "user_data_dir": "~/.freqtrade/"
}
```

### 进一步的数据分析文档

* [策略调试](strategy_analysis_example.md) - 也可作为 Jupyter notebook 使用 (`user_data/notebooks/strategy_analysis_example.ipynb`)
* [绘图](plotting.md)
* [标签分析](advanced-backtesting.md)

如果您想分享如何最好地分析数据的想法，请随时提交问题或拉取请求来增强此文档。

## 示例实用代码片段

### 更改目录到根目录

Jupyter notebooks 从 notebook 目录执行。以下代码片段搜索项目根目录，因此相对路径保持一致。

```python
import os
from pathlib import Path

# 更改目录
# 修改此单元格以确保输出显示正确的路径。
# 定义相对于单元格输出中显示的项目根目录的所有路径
project_root = "somedir/freqtrade"
i=0
try:
    os.chdir(project_root)
    assert Path('LICENSE').is_file()
except:
    while i<4 and (not Path('LICENSE').is_file()):
        os.chdir(Path(Path.cwd(), '../'))
        i+=1
    project_root = Path.cwd()
print(Path.cwd())
```

### 加载多个配置文件

此选项对于检查传入多个配置的结果很有用。
这也将运行整个配置初始化，因此配置完全初始化以传递给其他方法。

```python
from freqtrade.configuration import Configuration

# 加载配置 - 这将加载所有配置文件
config = Configuration.from_files(['config1.json', 'config2.json'])

# 您现在可以使用配置对象
print(config['exchange']['name'])
```
