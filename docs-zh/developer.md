# 开发帮助

本页面面向 Freqtrade 的开发者、希望为 Freqtrade 代码库或文档做出贡献的人员，或希望了解他们正在运行的应用程序源代码的人员。

我们欢迎所有贡献、错误报告、错误修复、文档改进、增强功能和想法。我们在 [GitHub](https://github.com) 上[跟踪问题](https://github.com/freqtrade/freqtrade/issues)，并在 [discord](https://discord.gg/p7nuUNVfP7) 上有一个开发频道，您可以在那里提问。

## 文档

文档可在 [https://freqtrade.io](https://www.freqtrade.io/) 获得，每个新功能 PR 都需要提供文档。

文档的特殊字段（如注释框等）可以在[这里](https://squidfunk.github.io/mkdocs-material/reference/admonitions/)找到。

要在本地测试文档，请使用以下命令。

``` bash
pip install -r docs/requirements-docs.txt
mkdocs serve
```

这将启动一个本地服务器（通常在端口 8000 上），这样您就可以看到一切是否如您所愿。

## 开发者设置

要配置开发环境，您可以使用提供的 [DevContainer](#devcontainer-设置)，或使用 `setup.sh` 脚本并在询问"您想安装开发依赖项吗 [y/N]？"时回答"y"。
或者（例如，如果您的系统不受 setup.sh 脚本支持），请遵循手动安装过程并运行 `pip3 install -r requirements-dev.txt` - 然后运行 `pip3 install -e .[all]`。

这将安装开发所需的所有工具，包括 `pytest`、`ruff`、`mypy` 和 `coveralls`。

然后通过运行 `pre-commit install` 安装 git 钩子脚本，这样您的更改将在提交前在本地验证。
这避免了大量等待 CI 的时间，因为一些基本的格式检查在您的机器上本地完成。

在打开拉取请求之前，请熟悉我们的[贡献指南](https://github.com/freqtrade/freqtrade/blob/develop/CONTRIBUTING.md)。

### Devcontainer 设置

最快最简单的入门方法是使用带有远程容器扩展的 [VSCode](https://code.visualstudio.com/)。
这使开发者能够启动机器人及其所有必需的依赖项，而*无需*在本地机器上安装任何 freqtrade 特定的依赖项。

#### Devcontainer 依赖项

* [VSCode](https://code.visualstudio.com/)
* [docker](https://docs.docker.com/install/)
* [远程容器扩展文档](https://code.visualstudio.com/docs/remote)

有关[远程容器扩展](https://code.visualstudio.com/docs/remote)的更多信息，最好查阅文档。

### 测试

新代码应该被基本的单元测试覆盖。根据功能的复杂性，审查者可能会要求更深入的单元测试。
如有必要，Freqtrade 团队可以协助并指导编写好的测试（但请不要期望任何人为您编写测试）。

#### 如何运行测试

在根文件夹中使用 `pytest` 运行所有可用的测试用例并确认您的本地环境设置正确

!!! Note "功能分支"
    测试预期在 `develop` 和 `stable` 分支上通过。其他分支可能是正在进行的工作，测试可能还不工作。

#### 在测试中检查日志内容

Freqtrade 使用 2 种主要方法在测试中检查日志内容，`log_has()` 和 `log_has_re()`（用于使用正则表达式检查，在动态日志消息的情况下）。
这些可从 `conftest.py` 获得，可以在任何测试模块中导入。

示例检查如下所示：

``` python
from tests.conftest import log_has, log_has_re

def test_method_to_test(caplog):
    method_to_test()

    assert log_has("This event happened", caplog)
    # 检查带有尾随数字的正则表达式...
    assert log_has_re(r"This dynamic event happened and produced \d+", caplog)

```

### 调试配置

要调试 freqtrade，我们推荐使用带有 Python 扩展的 VSCode，配置如下启动配置（位于 `.vscode/launch.json`）。
详细信息显然会因设置而异 - 但这应该可以帮助您入门。

``` json
{
    "name": "freqtrade trade",
    "type": "debugpy",
    "request": "launch",
    "module": "freqtrade",
    "console": "integratedTerminal",
    "args": [
        "trade",
        // 可选:
        // "--userdir", "user_data",
        "--strategy", 
        "MyAwesomeStrategy",
    ]
},
```

命令行参数可以在 `"args"` 数组中添加。

## 代码风格

Freqtrade 使用 [ruff](https://docs.astral.sh/ruff/) 进行代码格式化和 linting。

### 运行代码检查

```bash
# 运行 ruff 检查
ruff check .

# 自动修复可修复的问题
ruff check --fix .

# 格式化代码
ruff format .
```

### 类型检查

Freqtrade 使用 [mypy](http://mypy-lang.org/) 进行类型检查。

```bash
# 运行类型检查
mypy freqtrade
```

## 贡献指南

### 拉取请求流程

1. Fork 仓库
2. 创建功能分支
3. 进行更改
4. 添加测试
5. 运行测试套件
6. 提交拉取请求

### 提交消息格式

使用清晰、描述性的提交消息：

```
feat: 添加新的策略回调功能

- 实现 custom_stake_amount 回调
- 添加相应的测试
- 更新文档
```

### 代码审查

所有拉取请求都需要代码审查。审查者将检查：

- 代码质量和风格
- 测试覆盖率
- 文档完整性
- 向后兼容性

## 发布流程

### 版本控制

Freqtrade 使用语义版本控制：

- `MAJOR.MINOR.PATCH`
- 主要版本：破坏性更改
- 次要版本：新功能
- 补丁版本：错误修复

### 发布分支

- `develop`: 开发分支
- `stable`: 稳定发布分支
- `master`: 已弃用，使用 `stable`

## 架构概述

### 核心组件

```
freqtrade/
├── configuration/     # 配置管理
├── data/             # 数据处理
├── exchange/         # 交易所接口
├── optimize/         # 优化模块
├── persistence/      # 数据持久化
├── plugins/          # 插件系统
├── resolvers/        # 解析器
├── rpc/             # RPC 接口
├── strategy/        # 策略基类
└── worker.py        # 主工作进程
```

### 错误处理

Freqtrade 异常都继承自 `FreqtradeException`。
但是，不应直接使用这个通用错误类。相反，存在多个专门的子异常。

以下是异常继承层次结构的概述：

```
+ FreqtradeException
|
+---+ OperationalException
|   |
|   +---+ ConfigurationError
|
+---+ DependencyException
|   |
|   +---+ PricingError
|   |
|   +---+ ExchangeError
|       |
|       +---+ TemporaryError
|       |
|       +---+ DDosProtection
|       |
|       +---+ InvalidOrderException
|           |
|           +---+ RetryableOrderError
|           |
|           +---+ InsufficientFundsError
|
+---+ StrategyError
```

## 插件开发

### 交易对列表处理器

您有一个新的交易对选择算法的好想法想要尝试吗？太好了。
希望您也想将其贡献回上游。

无论您的动机是什么 - 这应该能让您开始尝试开发新的交易对列表处理器。

首先，看看 [VolumePairList](https://github.com/freqtrade/freqtrade/blob/develop/freqtrade/plugins/pairlist/VolumePairList.py) 处理器，最好复制这个文件并使用您的新交易对列表处理器的名称。

这是一个简单的处理器，但是作为如何开始开发的好例子。

接下来，修改处理器的类名（理想情况下与模块文件名对齐）。

#### 必需方法

##### short_desc

这应该包含交易对列表处理器的名称，以及包含资产数量的简短描述。请遵循格式 `"PairlistName - top/bottom X pairs"`。

##### gen_pairlist

如果交易对列表处理器可以用作链中的领导交易对列表处理器，定义初始交易对列表，然后由链中的所有交易对列表处理器处理，则覆盖此方法。例如 `StaticPairList` 和 `VolumePairList`。

这在机器人的每次迭代中调用（仅当交易对列表处理器在第一个位置时） - 因此考虑为计算/网络繁重的计算实现缓存。

它必须返回结果交易对列表（然后可能传递到交易对列表处理器链中）。

##### filter_pairlist

如果交易对列表处理器应该用作过滤器，则覆盖此方法，从传入的交易对列表中移除交易对。

这在机器人的每次迭代中调用 - 因此考虑为计算/网络繁重的计算实现缓存。

它接收传入的交易对列表（来自前一个交易对列表处理器），并返回过滤后的交易对列表。

### 保护机制

最好阅读[保护文档](plugins.md#保护机制)以了解保护机制。
本指南面向想要开发新保护机制的开发者。

没有保护机制应该直接使用 datetime，而应该使用提供的 `date_now` 变量进行日期计算。这保留了回测保护机制的能力。

!!! Tip "编写新的保护机制"
    最好复制现有的保护机制之一作为好例子。

#### 必需方法

##### short_desc

返回保护机制的简短描述。

##### global_stop

如果应该全局停止交易，则返回 `True`。

##### stop_per_pair

如果应该为特定交易对停止交易，则返回 `True`。

## 测试新交易所

!!! Note
    本节是一个正在进行的工作，不是如何使用 Freqtrade 测试新交易所的完整指南。

!!! Note
    在运行以下任何测试之前，请确保使用最新版本的 CCXT。
    您可以通过在激活的虚拟环境中运行 `pip install -U ccxt` 来获取最新版本的 ccxt。
    这些测试不支持原生 docker，但是可用的 dev-container 将支持所有必需的操作和最终必要的更改。

### 手动测试

您应该手动测试以下内容：

* 验证 `fetch_ohlcv()` 提供的数据 - 并最终为此交易所调整 `ohlcv_candle_limit`
* 检查 L2 订单簿限制范围（API 文档） - 并根据需要设置
* 检查余额是否正确显示 (*)
* 创建市价订单 (*)
* 创建限价订单 (*)
* 取消订单 (*)
* 完成交易（入场 + 出场）(*)
  * 比较交易所和机器人之间的结果计算
  * 确保费用正确应用（检查数据库与交易所）

(*) 需要 API 密钥和交易所余额。

### 交易所止损

检查新交易所是否通过其 API 支持交易所止损订单。

由于 CCXT 尚未为交易所止损提供统一，我们需要自己实现特定于交易所的参数。最好看看 `binance.py` 作为此实现的示例。您需要深入研究交易所 API 的文档，了解如何准确地做到这一点。[CCXT Issues](https://github.com/ccxt/ccxt/issues) 也可能提供很大帮助，因为其他人可能已经为他们的项目实现了类似的东西。

### 不完整蜡烛图

检查交易所是否返回不完整的蜡烛图。

您可以使用以下脚本来检查这一点（调整交易所和交易对以匹配您的设置）：

```python
import ccxt
from datetime import datetime, timezone
from freqtrade.data.converter import ohlcv_to_dataframe
ct = ccxt.binance()  # 使用您正在测试的交易所
timeframe = "1d"
pair = "BTC/USDT"  # 确保使用该交易所存在的交易对！
raw = ct.fetch_ohlcv(pair, timeframe=timeframe)

# 转换为数据框
df1 = ohlcv_to_dataframe(raw, timeframe, pair=pair, drop_incomplete=False)

print(df1.tail(1))
print(datetime.now(timezone.utc))
```

输出将显示交易所的最后一个条目以及当前 UTC 日期。
如果日期显示同一天，则最后一个蜡烛图可以假定为不完整，应该被丢弃（保留交易所类中的设置 `"ohlcv_partial_candle"` 不变 / True）。否则，将 `"ohlcv_partial_candle"` 设置为 `False` 以不丢弃蜡烛图。

另一种方法是连续多次运行此命令并观察成交量是否在变化（而日期保持不变）。

## 持续集成

这记录了为 CI 管道做出的一些决定。

* CI 在所有操作系统变体上运行，Linux（ubuntu）、macOS 和 Windows。
* Docker 镜像为分支 `stable` 和 `develop` 构建，并作为多架构构建构建，通过相同标签支持多个平台。
* 包含绘图依赖项的 Docker 镜像也可作为 `stable_plot` 和 `develop_plot` 使用。
* Docker 镜像包含一个文件 `/freqtrade/freqtrade_commit`，包含此镜像基于的提交。
* 完整的 docker 镜像重建通过计划每周运行一次。
* 部署在 ubuntu 上运行。
* ta-lib 二进制文件包含在 build_helpers 目录中，以避免与外部不可用性相关的失败。
* 所有测试必须通过才能将 PR 合并到 `stable` 或 `develop`。

## 创建发布

文档的这一部分面向维护者，并展示如何创建发布。

### 创建发布分支

!!! Note
    确保 `stable` 分支是最新的！

首先，选择一个大约一周前的提交（不包括最新添加到发布中的内容）。

```bash
# 创建新分支
git checkout -b new_release <commitid>
```

确定在此提交和当前状态之间是否进行了关键错误修复，并最终挑选这些。

* 将发布分支（stable）合并到此分支中。
* 编辑 `freqtrade/__init__.py` 并添加与当前日期匹配的版本（例如 2019 年 7 月的 `2019.7`）。如果我们需要在该月进行第二次发布，次要版本可以是 `2019.7.1`。版本号必须遵循 PEP0440 允许的版本，以避免推送到 pypi 时失败。
* 提交这部分。
* 将该分支推送到远程并创建针对 **stable 分支** 的 PR。
* 将开发版本更新为遵循模式 `2019.8-dev` 的下一个版本。

### 从 git 提交创建更改日志

```bash
# 需要在合并/拉取该分支之前完成。
git log --oneline --no-decorate --no-merges stable..new_release
```

为了保持发布日志简短，最好将完整的 git 更改日志包装到可折叠的详细信息部分中。

### 创建 github 发布/标签

一旦针对 stable 的 PR 被合并（最好在合并后立即）：

* 在 Github UI 中使用"Draft a new release"按钮（子部分发布）。
* 使用指定的版本号作为标签。
* 使用"stable"作为参考（此步骤在上述 PR 合并后进行）。
* 使用上述更改日志作为发布评论（作为代码块）。

通过遵循这些开发指南，您可以有效地为 Freqtrade 项目做出贡献。我们感谢所有形式的贡献！

1. **策略引擎**: 处理交易逻辑
2. **数据提供者**: 管理市场数据
3. **交易所接口**: 与交易所通信
4. **持久化层**: 数据库操作
5. **API 服务器**: REST API 和 WebSocket

### 数据流

```
市场数据 -> 策略分析 -> 交易信号 -> 订单执行 -> 结果记录
```

### 插件系统

Freqtrade 支持插件扩展：

- 交易对列表处理器
- 保护机制
- 自定义指标
- 数据提供者

## 常见开发任务

### 添加新的交易所

1. 继承 `Exchange` 基类
2. 实现必需的方法
3. 添加交易所特定配置
4. 编写测试
5. 更新文档

### 创建新的策略回调

1. 在 `IStrategy` 中定义接口
2. 在策略引擎中调用
3. 添加类型提示
4. 编写测试和文档

### 添加新的命令

1. 在 `commands/` 目录中创建模块
2. 实现命令逻辑
3. 添加到主命令解析器
4. 编写测试和文档

## 性能考虑

### 回测优化

- 使用向量化操作
- 避免循环
- 缓存计算结果
- 优化数据访问

### 内存管理

- 及时释放大对象
- 使用生成器处理大数据集
- 监控内存使用

### 并发处理

- 使用异步操作
- 避免阻塞调用
- 合理使用线程池

## 故障排除

### 常见问题

1. **导入错误**: 检查依赖项安装
2. **测试失败**: 确保环境配置正确
3. **类型错误**: 运行 mypy 检查
4. **格式问题**: 运行 ruff 格式化

### 调试技巧

- 使用 VSCode 调试器
- 添加日志输出
- 使用 pytest 的 `-s` 选项
- 检查测试覆盖率

## 社区

### 获取帮助

- [Discord 开发频道](https://discord.gg/p7nuUNVfP7)
- [GitHub 讨论](https://github.com/freqtrade/freqtrade/discussions)
- [GitHub Issues](https://github.com/freqtrade/freqtrade/issues)

### 贡献机会

- 错误修复
- 功能开发
- 文档改进
- 测试编写
- 代码审查
