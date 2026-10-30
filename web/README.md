# DARWIN 网站

DARWIN 用 Open RSI 已保存的正式实验生成中英文两套静态网站：首页、代码优化、模型实验、视频创作、视觉作品、全部实验和开始使用。所有交互都在浏览器读取静态数据，不调用模型。

```bash
python scripts/build_site.py
python -m http.server 8765 --bind 127.0.0.1 --directory build/site
```

英文为默认语言（`/`），中文在 `/zh/`。两种语言的页面结构相同，页头可互相切换；首次以中文浏览器访问英文页时，右下角提示切换，不自动跳转。正式入口为 `https://www.riseai.top/darwin/`，只部署 `build/site`，不要把源码仓库根目录作为网站根目录。

## 文件分工

- `page.html`：共用页头、页脚与元数据；`home.html`、`code.html`、`experiments.html`、`video.html`、`visual.html`、`cases.html`、`start.html` 为各页内容。
- `i18n/en.json`、`i18n/zh.json`：界面文字。模板用 `{{键名}}` 引用，脚本用 `t("键名")`；两份文件的键必须一致，缺键时构建失败。
- `i18n/records.en.json`、`i18n/records.zh.json`：实验记录（领域标题、修改思路、评委反馈等）的译文，键为原文。英文页缺译文时构建失败；`python scripts/site_i18n.py --missing en` 可列出待翻译文字。作品文件本身保持原语言。
- 说明文档中英各一份：`docs/X.zh-CN.md` 对应 `docs/X.md`，模板、案例和环境探测的 `README.md` 对应同目录 `README.en.md`（`THIRD_PARTY.md` 同理）。英文页的文档按钮与案例链接自动打开英文版；修改中文说明时同步英文版，新增说明须带译文，否则测试失败。
- `assets/site.css`：设计变量、组件与窄屏布局。浅色底配深色放映区，强调色只用于“保留”的版本，拒绝用橙色。
- `assets/app.js`：首页进化回放、四个实验室、全部实验浏览与比较、文档预览和语言切换。视觉实验室按轮翻看截图、分项分数与当时最好版本的对比，可连播保留的版本。
- `assets/fonts/`：自托管的 Inter 与 JetBrains Mono 拉丁子集（SIL OFL），避免依赖国内无法访问的字体服务；中文使用系统字体。

## 数据与公开范围

`scripts/build_site.py` 固定使用四份已验收运行生成前三个实验室的数据（`CASES`）；视觉实验室按 `VISUAL` 读取鹈鹕的两次运行和落地页的一次运行，后一次运行的起点若与前一次的最终作品逐字节相同，就接成一条时间线。全部实验页由 `examples/catalog.json` 与原始运行汇总，文件正文按需读取。构建只复制公开需要的内容：`examples/`、模板目录、四份说明文档（中英文）、中英文 README、许可证和 wheel 安装包；源码包含内部开发文档，不放到网站；协作约定、接手说明、开发记录和发布审计不会进入网站。旧的 `examples/index.html` 地址在网站中转到全部实验页。

源码仓库暂未公开，页面不链接仓库，开始使用页通过网站上的 wheel 安装。视频卡片与封面取自真实成片，时间点、裁切和哈希见 `assets/media-sources.json`；`assets/og.png` 是按页面设计绘制的分享图，不代表某次实验数据。

## 修改后检查

运行 `python -m pytest -q`。`tests/test_site.py` 检查两种语言的全部页面链接、语言互链、界面文字键、英文数据无漏译、说明文档的英文版及其链接、未评审轮次边界、视频字幕时间、结果包与公开文件范围。之后在浏览器检查桌面与 390px 窄屏：首页回放、轮次切换、代码差异、矩阵筛选、视频字幕跳转、视觉实验室的截图切换与连播、全部实验的版本比较与下载。
