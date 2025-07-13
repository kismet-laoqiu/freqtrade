# Windows 安装

我们**强烈**建议 Windows 用户使用 [Docker](docker_quickstart.md)，因为这样会更容易、更顺畅（也更安全）。

如果无法使用 Docker，请尝试使用 Windows Linux 子系统 (WSL) - Ubuntu 说明应该适用。
否则，请按照以下说明操作。

所有说明都假设已安装 Python 3.11+ 并且可用。

## 克隆 git 仓库

首先通过运行以下命令克隆仓库：

``` powershell
git clone https://github.com/freqtrade/freqtrade.git
```

现在，选择您的安装方法，可以通过脚本自动安装（推荐）或按照相应说明手动安装。

## 自动安装 freqtrade

### 运行安装脚本

脚本会询问您几个问题以确定应该安装哪些部分。

```powershell
Set-ExecutionPolicy -ExecutionPolicy Bypass
cd freqtrade
. .\setup.ps1
```

## 手动安装 freqtrade

!!! Note "64位 Python 版本"
    请确保使用 64位 Windows 和 64位 Python，以避免由于 Windows 下 32位应用程序的内存限制而导致的回测或超参数优化问题。
    Windows 下不再支持 32位 python 版本。

!!! Hint
    在 Windows 下使用 [Anaconda 发行版](https://www.anaconda.com/distribution/) 可以极大地帮助解决安装问题。查看文档中的 [Anaconda 安装部分](installation.md#使用-conda-安装) 获取更多信息。

### 安装 ta-lib

根据 [ta-lib 文档](https://github.com/TA-Lib/ta-lib-python#windows) 安装 ta-lib。

由于在 Windows 上从源代码编译有很重的依赖项（需要部分 Visual Studio 安装），Freqtrade 为最新的 3 个 Python 版本（3.11、3.12 和 3.13）和 64位 Windows 提供了这些依赖项（以二进制 wheel 格式）。
这些 Wheels 也被在 Windows 上运行的 CI 使用，因此与 freqtrade 一起测试。

其他版本必须从上述链接下载。

``` powershell
cd \path\freqtrade
python -m venv .venv
.venv\Scripts\activate.ps1
# 可选择从 wheel 安装 ta-lib
# 最终调整下面的文件名以匹配下载的 wheel
pip install --find-links build_helpers\ TA-Lib -U
pip install -r requirements.txt
pip install -e .
freqtrade
```

!!! Note "使用 Powershell"
    上述安装脚本假设您在 64位 Windows 上使用 powershell。
    传统 CMD Windows 控制台的命令可能有所不同。

### Windows 安装期间的错误

``` bash
error: Microsoft Visual C++ 14.0 is required. Get it with "Microsoft Visual C++ Build Tools": http://landinghub.visualstudio.com/visual-cpp-build-tools
```

不幸的是，许多需要编译的包不提供预构建的 wheel。因此，必须为您的 python 环境安装并提供 C/C++ 编译器。

您可以从 [这里](https://visualstudio.microsoft.com/visual-cpp-build-tools/) 下载 Visual C++ 构建工具，并在其默认配置中安装"使用 C++ 的桌面开发"。不幸的是，这是一个很大的下载/依赖项，所以您可能想要首先考虑 WSL2 或 [docker compose](docker_quickstart.md)。

![Windows 安装](assets/windows_install.png)
