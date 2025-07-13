# FreqUI

Freqtrade 提供了一个内置的网络服务器，可以提供 [FreqUI](https://github.com/freqtrade/frequi)，即 freqtrade 前端。

默认情况下，UI 会作为安装的一部分自动安装（脚本、docker）。
freqUI 也可以通过使用 `freqtrade install-ui` 命令手动安装。
同样的命令也可以用来将 freqUI 更新到新版本。

一旦机器人在交易/模拟运行模式下启动（使用 `freqtrade trade`）- UI 将在配置的 API 端口下可用（默认为 `http://127.0.0.1:8080`）。

??? Note "想要为 freqUI 做贡献？"
    开发者不应该使用这种方法，而应该克隆相应的仓库，使用 [freqUI 仓库](https://github.com/freqtrade/frequi) 中描述的方法来获取 freqUI 的源代码。需要一个可工作的 node 安装来构建前端。

!!! tip "freqUI 不是运行 freqtrade 的必需品"
    freqUI 是 freqtrade 的可选组件，不是运行机器人的必需品。
    它是一个可以用来监控机器人并与之交互的前端 - 但 freqtrade 本身在没有它的情况下也能完美运行。

## 配置

FreqUI 没有自己的配置文件 - 但假设 [rest-api](rest-api.md) 有一个可工作的设置。
请参考相应的文档页面来设置 freqUI

## 用户界面

FreqUI 是一个现代的、响应式的网络应用程序，可以用来监控和与您的机器人交互。

FreqUI 提供浅色和深色主题。
主题可以通过页面顶部的显著按钮轻松切换。
本页面截图的主题将适应所选的文档主题，因此要查看深色（或浅色）版本，请切换文档的主题。

### 登录

下面的截图显示了 freqUI 的登录界面。

![FreqUI - login](../docs/assets/frequi-login-CORS.png#only-dark)
![FreqUI - login](../docs/assets/frequi-login-CORS-light.png#only-light)

!!! Hint "CORS"
    此截图中显示的 Cors 错误是由于 UI 运行在与 API 不同的端口上，并且 [CORS](#cors) 尚未正确设置。

### 交易视图

交易视图允许您可视化机器人正在进行的交易并与机器人交互。
在此页面上，您还可以通过启动和停止机器人与机器人交互，如果配置了，还可以强制交易入场和出场。

![FreqUI - trade view](../docs/assets/freqUI-trade-pane-dark.png#only-dark)
![FreqUI - trade view](../docs/assets/freqUI-trade-pane-light.png#only-light)

### 绘图配置器

FreqUI 绘图可以通过策略中的 `plot_config` 配置对象（可以通过"从策略"按钮加载）或通过 UI 进行配置。
可以创建多个绘图配置并随意切换 - 允许对您的图表进行灵活、不同的视图。

绘图配置可以通过交易视图右上角的"绘图配置器"（齿轮图标）按钮访问。

![FreqUI - plot configuration](../docs/assets/freqUI-plot-configurator-dark.png#only-dark)
![FreqUI - plot configuration](../docs/assets/freqUI-plot-configurator-light.png#only-light)

### 设置

可以通过访问设置页面更改几个与 UI 相关的设置。

您可以更改的内容（除其他外）：

* UI 的时区
* 将开放交易可视化为网站图标的一部分（浏览器标签）
* 蜡烛图颜色（上涨/下跌 -> 红色/绿色）
* 启用/禁用应用内通知类型

![FreqUI - Settings view](../docs/assets/frequi-settings-dark.png#only-dark)
![FreqUI - Settings view](../docs/assets/frequi-settings-light.png#only-light)

## 回测

当 freqtrade 在 [网络服务器模式](utils.md#webserver-mode) 下启动时（freqtrade 使用 `freqtrade webserver` 启动），回测视图变为可用。
此视图允许您回测策略并可视化结果。

您还可以加载和可视化以前的回测结果，以及将结果相互比较。

![FreqUI - Backtesting](../docs/assets/freqUI-backtesting-dark.png#only-dark)
![FreqUI - Backtesting](../docs/assets/freqUI-backtesting-light.png#only-light)

## CORS

FreqUI 使用与 freqtrade 后端不同的端口运行。
因此，需要配置 CORS（跨源资源共享）以允许前端与后端通信。

在大多数情况下，您应该将 `"http://localhost:3000"` 添加到 `CORS_origins` 列表中。

```json
{
    "api_server": {
        "enabled": true,
        "listen_ip_address": "127.0.0.1",
        "listen_port": 8080,
        "CORS_origins": ["http://localhost:3000"],
        "username": "freqtrader",
        "password": "SuperSecretPassword"
    }
}
```

!!! Note
    您也可以使用 `"*"` 允许所有来源 - 但这不推荐用于生产环境。

确保在更改配置后重启 freqtrade。
