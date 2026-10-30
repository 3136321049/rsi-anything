# 换电脑与助手接力

更新日期：2026-10-24。这个项目要让用户给出目标后，AI 连续修改代码、文章、提示词、视频方案等产物，执行检查并接受反馈，保留更好的版本，再继续尝试。首发优先把过程和作品展示清楚，后续再增强评价和搜索方法。

## 目前完成了什么

当前版本 `0.3.0.dev0`，开发主线为 **`rebuild`**。`main` 仍是较早版本，换电脑请明确检出 `rebuild`。

- 16 个领域、18 个模板齐全（D16 视觉为首发后新增）。14 个领域有完整真实多轮、初始/中间/最终作品与独立复验；文案领域同时含单篇和写作手册。
- 通用循环已保存逐轮作品、配置、修改、评分与接受/拒绝原因，补齐中断恢复、超时清理和媒体导出。
- `examples/index.html` 提供各领域、运行与版本比较；`examples/showcase-media/openrsi-demo.mp4` 是 35 秒真实作品短片。
- 本次上传前完整回归 115 项通过，安装包含 16 个模板，干净环境已走通初始化、评分、测试代理运行和导出。准确结果及边界见 [执行表](GOAL-PROGRESS.zh-CN.md)和[验收记录](RELEASE-AUDIT.zh-CN.md)。

D07 已取得初始与第一轮真实生成视频，后续免费服务报错，未取得新作品。D15 没有个人 GPU，仅有模板和真实设备探测，性能结果为空。这两项保留待补资源，不计入完整多轮数量。

## 另一台电脑第一次接手

使用自己的 GitHub 登录或 SSH 身份克隆：

```bash
git clone --branch rebuild git@github.com:3136321049/rsi-anything.git
cd rsi-anything
git config user.name 3136321049
git config user.email 3136321049@users.noreply.github.com
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
python -m pytest -q
```

若已克隆仓库，先 `git status --short`，保存本机未提交工作，再执行 `git fetch origin`、`git switch rebuild`、`git pull --ff-only origin rebuild`。分支出现分叉时先检查差异，不用强推或硬重置覆盖。

训练和回测案例另装各模板的 `requirements.txt`；视频案例需要 FFmpeg/ffprobe。个人助手在新电脑独立登录。CLI 路径、模型、API 和隔离配置见 [安装说明](INSTALL.zh-CN.md)，不要复制另一台电脑的凭据或全局配置。

只看已完成结果无需模型账号：

```bash
python scripts/build_showcase.py
python -m http.server 8765 --bind 127.0.0.1
```

在自己的浏览器打开 `http://127.0.0.1:8765/examples/index.html`。GitHub 文件预览不能直接运行这张交互页面。

## Codex 与 Claude Code 如何接力

两者共用根目录 [AGENTS.md](../AGENTS.md)，Claude Code 通过 [CLAUDE.md](../CLAUDE.md) 引入相同约定。工作内容通过 Git 和共享文档传递，不依赖任何一台电脑的聊天历史。

同一时间由一台电脑负责 `rebuild` 上的改动。开始前拉取最新提交；结束时核查上传范围，提交并推送；换电脑后再拉取。需要同时开发时按主题使用独立分支，通过普通合并整理，避免两台电脑同时改同一份原始实验。

每次交接更新 `docs/DEVLOG.zh-CN.md`，写清日期、使用的助手、改了什么、验证结果、仍存在的问题和下一步。领域状态有变化时更新 `docs/GOAL-PROGRESS.zh-CN.md`；具体任务的命令、作品和复验记录放在对应 `examples/<模板>/README.md`。

可以把这段话交给新电脑上的助手：

> 先读根目录 AGENTS.md、docs/COLLABORATION.zh-CN.md、docs/HANDOFF.zh-CN.md 和 docs/GOAL-PROGRESS.zh-CN.md，检查当前分支、远端和未提交修改。按仓库当前源码与原始实验接手，保留失败和未知结果。不要重跑已经完成的全部模型实验；先说明本次要推进的一个具体问题，再按已有实现完成并验证，更新共享开发记录。

## 哪些会同步，哪些留在原电脑

Git 同步源码、模板、公开研究、项目文档、测试、已导出的案例和媒体。`dist/` 仅随明确审查过的安装产物提交，压缩版完整交付包保留为本地归档；构建方法见安装说明。

`.rsi/` 的实验仓库、运行分支和缓存不上传。另一台电脑可阅读 `examples/` 的导出结果，但无法直接恢复这台电脑的运行分支。要继续同一次中断运行，须在原电脑按接手说明恢复；在新电脑上通常从模板开始新实验，使用新运行号并保留与旧实验的关系。

账号、密钥、浏览器登录、个人 CLI 配置、虚拟环境、机器路径和原始会话各自留在本机。本仓库只保存独立个人项目与公开或获准资料；上传前检查暂存文件和历史，不借共享规则文件同步无关工作背景。

## 下一步优先做什么

先围绕代码修复、写作手册和视频剪辑制作主展示，用用户自己的公开或获准素材替换通用输入，展示初稿、代表性中间版、最终稿和保留理由。现有主循环已够首版使用，优先解决实际使用中遇到的问题。

D07 等可用个人生成服务后另开完整多轮；D15 等个人 GPU 后补数值检查、真实计时和小模块对照。当前不租用设备或自动付费。对外正式发布、部署或合并主分支另按明确授权执行。
