# 本地首发候选

> 2026-10-30：当前安装包为 [`rsi_anything-0.3.0.dev0`](../dist/rsi_anything-0.3.0.dev0-py3-none-any.whl)（18 个模板，含 `rsi new`、`rsi setup`、角色与插件），验证见 [构建校验](build-validation-0.3.0.dev0.json) 与 [干净安装回执](install-receipt-0.3.0.dev0.json)。以下为首发 `0.2.0.dev0` 的原始记录，保持不变。

版本 `0.2.0.dev0`，日期 2026-10-24。提供 15 个领域、16 个模板；13 个领域有完整真实多轮，D07 为部分视频生成实测，D15 待个人 GPU。当前开发与接力以 `rebuild` 分支和[跨电脑协作](../docs/COLLABORATION.zh-CN.md)为准。

| 入口 | 内容 |
|---|---|
| [案例集合](../examples/index.html) | 按领域查看初始、逐轮和最终作品，比较代码、文本、图表、视频和日程 |
| [35 秒演示](../examples/showcase-media/openrsi-demo.mp4) | 已保存真实作品的无声剪辑，可直接播放 |
| [命令行安装包](../dist/rsi_anything-0.2.0.dev0-py3-none-any.whl) | 全部 16 个模板；不含大型案例媒体 |
| [轻量源码包](../dist/rsi_anything-0.2.0.dev0.tar.gz) | 源码、模板、测试及文档；不含案例媒体 |
| [安装说明](../docs/INSTALL.zh-CN.md) | 个人账号配置、初始化、运行、换输入和查看结果 |
| [接手说明](../docs/HANDOFF.zh-CN.md) | 当前实现、实验位置、资源缺项和下一步 |
| [逐项审计](../docs/RELEASE-AUDIT.zh-CN.md) | 领域与共用能力的验收依据和适用范围 |

验证凭证： [构建](build-validation.json)、[干净安装](install-receipt.json)、[展示文件与既有视觉检查范围](showcase-validation.json)。114 项程序测试通过；模型实验的原始结果在各案例目录，不混入安装测试。

两份安装产物与原回执保留首发构建快照；最新协作文档读取仓库文件。完整本地 ZIP 归档不提交，`package-validation.json` 与 `SHA256SUMS` 中的 ZIP 条目记录原归档校验，并非远端下载入口。当前上传范围与复核见 `github-sync-audit.json`，上传前完整回归为 115 项通过。

完整分享时保留源码、`examples/` 与文档之间的相对位置。页面通过本地 HTTP 服务查看更方便，命令见安装说明；单独发送 HTML 不会包含所有媒体。第三方资料条件见 [开源与来源](../docs/OPEN-SOURCE.zh-CN.md)，本项目代码许可不覆盖所有视频、行情或原始资料。
