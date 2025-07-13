# 安装

本页面解释如何为运行机器人准备您的环境。

freqtrade 文档描述了安装 freqtrade 的各种方法

* [Docker 镜像](docker_quickstart.md)（单独页面）
* [脚本安装](#脚本安装)
* [手动安装](#手动安装)
* [使用 Conda 安装](#使用-conda-安装)

请考虑使用预构建的 [docker 镜像](docker_quickstart.md) 来快速开始，同时评估 freqtrade 的工作方式。

------

## 信息

对于 Windows 安装，请使用 [Windows 安装指南](windows_installation.md)。

安装和运行 Freqtrade 最简单的方法是克隆机器人 Github 仓库，然后运行 `./setup.sh` 脚本（如果您的平台支持）。

!!! Note "版本考虑"
    克隆仓库时，默认工作分支名为 `develop`。此分支包含所有最新功能（由于自动化测试，可以认为相对稳定）。
    `stable` 分支包含最新发布版本的代码（通常每月在 `develop` 分支大约一周前的快照上发布一次，以防止打包错误，因此可能更稳定）。

!!! Note
    假设 Python3.11 或更高版本和相应的 `pip` 可用。如果不是这种情况，安装脚本会警告您并停止。还需要 `git` 来克隆 Freqtrade 仓库。
    此外，python 头文件（`python<yourversion>-dev` / `python<yourversion>-devel`）必须可用才能成功完成安装。

!!! Warning "最新时钟"
    运行机器人的系统上的时钟必须准确，经常与 NTP 服务器同步，以避免与交易所通信时出现问题。

------

## 系统要求

这些要求适用于[脚本安装](#脚本安装)和[手动安装](#手动安装)。

!!! Note "ARM64 系统"
    如果您运行的是 ARM64 系统（如 MacOS M1 或 Oracle VM），请使用 [docker](docker_quickstart.md) 运行 freqtrade。
    虽然通过一些手动努力可以进行本机安装，但目前不支持这种方式。

### 安装指南

* [Python >= 3.11](http://docs.python-guide.org/en/latest/starting/installation/)
* [pip](https://pip.pypa.io/en/stable/installing/)
* [git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git)
* [virtualenv](https://virtualenv.pypa.io/en/stable/installation.html)（推荐）
* [TA-Lib](https://ta-lib.github.io/ta-lib-python/)（安装说明[见下文](#安装-ta-lib)）

### 安装代码

我们包含/收集了 Ubuntu、MacOS 和 Windows 的安装说明。这些是指导原则，您在其他发行版上的成功可能会有所不同。
首先列出特定于操作系统的步骤，下面的通用部分对所有系统都是必需的。

!!! Note
    假设 Python3.11 或更高版本和相应的 pip 可用。

=== "Debian/Ubuntu"
    #### 安装必要的依赖项

    ```bash
    # 更新仓库
    sudo apt-get update

    # 安装包
    sudo apt install -y python3-pip python3-venv python3-dev python3-pandas git curl
    ```

=== "MacOS"
    #### 安装必要的依赖项

    如果您还没有安装 [Homebrew](https://brew.sh/)，请先安装。

    ```bash
    # 安装包
    brew install gettext libomp
    ```
    !!! Note
        `setup.sh` 脚本将为您安装这些依赖项 - 假设您的系统上已安装 brew。

=== "RaspberryPi/Raspbian"
    以下假设使用最新的 [Raspbian Buster lite 镜像](https://www.raspberrypi.org/downloads/raspbian/)。
    此镜像预装了 python3.11，使得启动和运行 freqtrade 变得容易。

    使用 Raspberry Pi 3 和 Raspbian Buster lite 镜像进行测试，应用了所有更新。

    ```bash
    sudo apt-get install python3-venv libatlas-base-dev cmake curl libffi-dev
    # 使用 piwheels.org 加速安装
    sudo echo "[global]\nextra-index-url=https://www.piwheels.org/simple" > tee /etc/pip.conf

    git clone https://github.com/freqtrade/freqtrade.git
    cd freqtrade

    bash setup.sh -i
    ```

    !!! Note "安装持续时间"
        根据您的网络速度和 Raspberry Pi 版本，安装可能需要数小时才能完成。
        因此，我们建议按照 [Docker 快速入门文档](docker_quickstart.md) 为 Raspberry 使用预构建的 docker 镜像

    !!! Note
        上述操作不会安装 hyperopt 依赖项。要安装这些，请使用 `python3 -m pip install -e .[hyperopt]`。
        我们不建议在 Raspberry Pi 上运行 hyperopt，因为这是一个非常耗费资源的操作，应该在强大的机器上完成。

------

## Freqtrade 仓库

Freqtrade 是一个开源加密货币交易机器人，其代码托管在 `github.com` 上

```bash
# 下载 freqtrade 仓库的 `develop` 分支
git clone https://github.com/freqtrade/freqtrade.git

# 进入下载的目录
cd freqtrade

# 您的选择 (1)：新手用户
git checkout stable

# 您的选择 (2)：高级用户
git checkout develop
```

(1) 此命令将克隆的仓库切换到使用 `stable` 分支。如果您希望保持在 (2) `develop` 分支上，则不需要此命令。

您可以随时使用 `git checkout stable`/`git checkout develop` 命令在分支之间切换。

??? Note "从 pypi 安装"
    安装 Freqtrade 的另一种方法是从 [pypi](https://pypi.org/project/freqtrade/)。缺点是此方法需要事先正确安装 ta-lib，因此目前不是安装 Freqtrade 的推荐方法。

    ``` bash
    pip install freqtrade
    ```

------

## 脚本安装

安装 Freqtrade 的第一种方法是使用提供的 Linux/MacOS `./setup.sh` 脚本，该脚本安装所有依赖项并帮助您配置机器人。

确保您满足[系统要求](#系统要求)并已下载 [Freqtrade 仓库](#freqtrade-仓库)。

### 使用 /setup.sh -install (Linux/MacOS)

如果您使用的是 Debian、Ubuntu 或 MacOS，freqtrade 提供了安装 freqtrade 的脚本。

```bash
# --install，从头开始安装 freqtrade
./setup.sh -i
```

### 激活您的虚拟环境

每次打开新终端时，您必须运行 `source .venv/bin/activate` 来激活您的虚拟环境。

```bash
# 激活虚拟环境
source ./.venv/bin/activate
```

[您现在已准备就绪](#您已准备就绪) 运行机器人。

### /setup.sh 脚本的其他选项

您也可以使用 `./script.sh` 更新、配置和重置机器人的代码库

```bash
# --update，命令 git pull 进行更新。
./setup.sh -u
# --reset，硬重置您的 develop/stable 分支。
./setup.sh -r
```

```
** --install **

使用此选项，脚本将安装机器人和大多数依赖项：
您需要事先安装 git 和 python3.11+ 才能正常工作。

* 必需软件如：`ta-lib`
* 在 `.venv/` 下设置您的 virtualenv

此选项是安装任务和 `--reset` 的组合

** --update **

此选项将拉取当前分支的最新版本并更新您的 virtualenv。定期使用此选项运行脚本以更新您的机器人。

** --reset **

此选项将硬重置您的分支（仅当您在 `stable` 或 `develop` 分支上时）并重新创建您的 virtualenv。
```

-----

## 手动安装

确保您满足[系统要求](#系统要求)并已下载 [Freqtrade 仓库](#freqtrade-仓库)。

### 安装 TA-Lib

#### TA-Lib 脚本安装

```bash
sudo ./build_helpers/install_ta-lib.sh
```

!!! Note
    这将使用此仓库中包含的 ta-lib tar.gz。

##### TA-Lib 手动安装

[官方安装指南](https://ta-lib.github.io/ta-lib-python/install.html)

```bash
wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz
tar xvzf ta-lib-0.4.0-src.tar.gz
cd ta-lib
sed -i.bak "s|0.00000001|0.000000000000000001 |g" src/ta_func/ta_utility.h
./configure --prefix=/usr/local
make
sudo make install
# 在基于 debian 的系统上（debian、ubuntu、...）- 可能需要更新 ldconfig。
sudo ldconfig
cd ..
rm -rf ./ta-lib*
```

### 设置 Python 虚拟环境 (virtualenv)

您将在独立的 `虚拟环境` 中运行 freqtrade

```bash
# 在目录 /freqtrade/.venv 中创建 virtualenv
python3 -m venv .venv

# 运行 virtualenv
source .venv/bin/activate
```

### 安装 python 依赖项

```bash
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt
# 安装 freqtrade
python3 -m pip install -e .
```
