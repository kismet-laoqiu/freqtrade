# 使用 Docker 运行 Freqtrade

本页面解释如何使用 Docker 运行机器人。它不是开箱即用的。您仍然需要阅读文档并了解如何正确配置它。

## 安装 Docker

首先为您的平台下载并安装 Docker / Docker Desktop：

* [Mac](https://docs.docker.com/docker-for-mac/install/)
* [Windows](https://docs.docker.com/docker-for-windows/install/)
* [Linux](https://docs.docker.com/install/)

!!! Info "Docker compose 安装"
    Freqtrade 文档假设使用 Docker desktop（或 docker compose 插件）。
    虽然 docker-compose 独立安装仍然有效，但需要将所有 `docker compose` 命令从 `docker compose` 更改为 `docker-compose` 才能工作（例如 `docker compose up -d` 将变成 `docker-compose up -d`）。

??? Warning "Windows 上的 Docker"
    如果您刚在 Windows 系统上安装了 docker，请确保重启系统，否则您可能会遇到与 docker 容器网络连接相关的无法解释的问题。

## 使用 docker 运行 Freqtrade

Freqtrade 在 [Dockerhub](https://hub.docker.com/r/freqtradeorg/freqtrade/) 上提供官方 Docker 镜像，以及一个可供使用的 [docker compose 文件](https://github.com/freqtrade/freqtrade/blob/stable/docker-compose.yml)。

!!! Note
    - 以下部分假设 `docker` 已安装并可供登录用户使用。
    - 下面的所有命令都使用相对目录，必须从包含 `docker-compose.yml` 文件的目录执行。

### Docker 快速入门

创建一个新目录并将 [docker-compose 文件](https://raw.githubusercontent.com/freqtrade/freqtrade/stable/docker-compose.yml) 放在此目录中。

``` bash
mkdir ft_userdata
cd ft_userdata/
# 从仓库下载 docker-compose 文件
curl https://raw.githubusercontent.com/freqtrade/freqtrade/stable/docker-compose.yml -o docker-compose.yml

# 拉取 freqtrade 镜像
docker compose pull

# 创建用户目录结构
docker compose run --rm freqtrade create-userdir --userdir user_data

# 创建配置 - 需要回答交互式问题
docker compose run --rm freqtrade new-config --config user_data/config.json
```

上述代码片段创建一个名为 `ft_userdata` 的新目录，下载最新的 compose 文件并拉取 freqtrade 镜像。
代码片段中的最后 2 个步骤创建包含 `user_data` 的目录，以及（交互式地）基于您的选择的默认配置。

!!! Question "如何编辑机器人配置？"
    您可以随时编辑配置，使用上述配置时，配置文件位于 `user_data/config.json`（在目录 `ft_userdata` 内）。

    您还可以通过编辑 `docker-compose.yml` 文件的命令部分来更改策略和命令。

#### 添加自定义策略

1. 配置现在可作为 `user_data/config.json` 使用
2. 将自定义策略复制到目录 `user_data/strategies/`
3. 将策略的类名添加到 `docker-compose.yml` 文件中

默认运行 `SampleStrategy`。

!!! Danger "`SampleStrategy` 只是一个演示！"
    `SampleStrategy` 仅供您参考并为您的自己的策略提供想法。
    在冒险使用真实资金之前，请始终回测您的策略并使用模拟运行一段时间！
    您将在[策略文档](strategy-customization.md)中找到有关策略开发的更多信息。

完成此操作后，您就可以在交易模式下启动机器人了（模拟运行或实盘交易，取决于您对上述相应问题的回答）。

``` bash
docker compose up -d
```

!!! Warning "默认配置"
    虽然生成的配置大部分是功能性的，但在启动机器人之前，您仍需要验证所有选项是否符合您的要求（如定价、交易对列表等）。

#### 访问 UI

如果您在 `new-config` 步骤中选择启用 FreqUI，您将在端口 `localhost:8080` 上可以使用 freqUI。

您现在可以通过在浏览器中输入 localhost:8080 来访问 UI。

??? Note "远程服务器上的 UI 访问"
    如果您在 VPS 上运行，您应该考虑使用 ssh 隧道或设置 VPN（openVPN、wireguard）来连接到您的机器人。
    这将确保 freqUI 不会直接暴露在互联网上，出于安全原因不建议这样做（freqUI 开箱即用不支持 https）。
    这些工具的设置不是本教程的一部分，但是在互联网上可以找到许多好的教程。
    请同时阅读 [使用 docker 的 API 配置](rest-api.md#使用-docker-的配置) 部分以了解有关此配置的更多信息。

#### 监控机器人

您可以使用 `docker compose ps` 检查正在运行的实例。
这应该将服务 `freqtrade` 列为 `running`。如果不是这种情况，最好检查日志（见下一点）。

#### Docker compose 日志

日志将写入：`user_data/logs/freqtrade.log`。
您还可以使用命令 `docker compose logs -f` 检查最新日志。

#### 数据库

默认情况下，freqtrade 将使用 SQLite 数据库，该数据库将存储在 `user_data/tradesv3.dryrun.sqlite` 中用于模拟运行，或存储在 `user_data/tradesv3.sqlite` 中用于实盘运行。

!!! Note "数据库升级"
    如果您已经有一个现有的数据库，请确保在启动机器人之前备份您的数据库。
    数据库升级通常是自动的，但备份总是一个好主意。
