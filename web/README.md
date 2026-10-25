# DARWIN 网站

DARWIN 使用 Open RSI 已保存的正式实验生成完整首页、代码优化、模型实验、视频创作和使用说明。所有交互在浏览器读取静态数据，不调用模型。原始案例集合继续保留。

在仓库根目录运行：

```bash
python scripts/build_site.py
python -m http.server 8765 --bind 127.0.0.1 --directory build/site
```

打开 `http://127.0.0.1:8765/`。已有仓库根目录预览服务时，可直接访问 `/build/site/`。生成目录可以独立托管，图片、视频、字幕、原始记录与下载包均包含在内。数据与源文件从源码仓库读取，构建不修改实验。

`page.html` 提供共用导航与页面结构；各领域有独立内容，`assets/site.css` 管理视觉与窄屏布局，`assets/app.js` 管理真实轮次比较、筛选、字幕跳转、文档预览和分享。生成器明确选取四份已验收运行，避免新增实验自动替换首页的固定展示。

视频封面取自真实成片，时间点、尺寸和哈希见 `assets/media-sources.json`。完整下载包保留该次原记录。训练案例无修改轮次不导出其内部试验指标，视频字幕用成片 SRT 转成 WebVTT。

对外服务只指向 `build/site`，不要将源码仓库根目录作为公共网站根目录。页面里的“开始使用”提供真实安装和运行步骤；网页创建或执行新实验尚未接入。构建后应运行 `python -m pytest -q`，并在浏览器检查三个领域、下载与窄屏布局。

品牌文案为 DARWIN、An evolution lab by RiseAI.、用真实反馈，持续改进作品。正式入口为 `https://www.riseai.top/darwin/`；正式部署只提供独立构建产物，模型运行环境不对外开放。
