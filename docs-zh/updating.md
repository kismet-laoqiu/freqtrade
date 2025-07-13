# 如何更新

要更新您的 freqtrade 安装，请使用以下方法之一，对应您的安装方法。

!!! Note "跟踪变更"
    破坏性变更/行为变更将在每个版本发布时的变更日志中记录。
    对于开发分支，请关注 PR 以避免被变更惊讶。

## Docker

!!! Note "使用 `master` 镜像的旧版安装"
    我们正在从 master 切换到 stable 用于发布镜像 - 请调整您的 docker 文件并将 `freqtradeorg/freqtrade:master` 替换为 `freqtradeorg/freqtrade:stable`

``` bash
docker compose pull
docker compose up -d
```

## 通过设置脚本安装

``` bash
./setup.sh --update
```

!!! Note
    确保在禁用虚拟环境的情况下运行此命令！

## 纯原生安装

请确保您也在更新依赖项 - 否则可能会在您不注意的情况下出现问题。

``` bash
git pull
pip install -U -r requirements.txt
pip install -e .

# 确保 freqUI 是最新版本
freqtrade install-ui 
```

### 更新问题

更新问题通常来自缺少依赖项（您没有遵循上述说明）- 或来自更新的依赖项，这些依赖项安装失败（例如 TA-lib）。
请参考相应的安装部分（下面链接了常见问题）

常见问题及其解决方案：

* [Windows 上的 ta-lib 更新](windows_installation.md#安装-ta-lib)
