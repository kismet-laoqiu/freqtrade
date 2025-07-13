## CORS

整个部分仅在跨域情况下才需要（您在 `localhost:8081`、`localhost:8082`、... 上运行多个机器人 API），并希望将它们合并到一个 FreqUI 实例中。

??? info "技术说明"
    所有基于 Web 的前端都受到 [CORS](https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS) - 跨域资源共享的约束。
    由于对 Freqtrade API 的大多数请求都必须经过身份验证，因此正确的 CORS 策略是避免安全问题的关键。
    此外，标准不允许对带有凭据的请求使用 `*` CORS 策略，因此必须适当设置此设置。

用户可以通过 `CORS_origins` 配置设置允许来自不同源 URL 的访问机器人 API。
它包含允许使用机器人 API 资源的允许 URL 列表。

假设您的应用程序部署为 `https://frequi.freqtrade.io/home/` - 这意味着需要以下配置：

```jsonc
{
    //...
    "jwt_secret_key": "somethingrandom",
    "CORS_origins": ["https://frequi.freqtrade.io"],
    //...
}
```

在以下（相当常见的）情况下，FreqUI 可在 `http://localhost:8080/trade` 上访问（这是您导航到 freqUI 时在导航栏中看到的内容）。
![freqUI url](assets/frequi_url.png)

此情况的正确配置是 `http://localhost:8080` - URL 的主要部分包括端口。

```jsonc
{
    //...
    "jwt_secret_key": "somethingrandom",
    "CORS_origins": ["http://localhost:8080"],
    //...
}
```

!!! Tip "尾随斜杠"
    在 `CORS_origins` 配置中不允许尾随斜杠（例如 `"http://localhots:8080/"`）。
    这样的配置不会生效，cors 错误将保持。

!!! Note
    我们强烈建议也将 `jwt_secret_key` 设置为只有您自己知道的随机内容，以避免未经授权访问您的机器人。
