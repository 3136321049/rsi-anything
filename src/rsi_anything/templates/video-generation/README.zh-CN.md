# D07：真实视频生成

[English](README.md)

助手只改 `generation.json` 的生成描述、反向描述和种子。准备步骤调用 Lightricks 官方公开 Space，真正生成短片；评委查看均匀抽取的静帧，反馈后再尝试改进。

默认服务是 [LTX Video Fast](https://huggingface.co/spaces/Lightricks/ltx-video-distilled)，上游说明为 LTX 0.9.8 13B distilled。2026-10-24 的真实实验已取得初始片段与第一轮生成片段；后两轮服务返回错误，没有新视频，标为质量未知。当前按资源例外保留部分实测，公开服务可能限额、排队或暂停，本包不自动切换付费服务。

## 启动

需要 Python、项目本身、FFmpeg/ffprobe 和一个能看图的个人模型评委。

```sh
rsi init video-generation demo-video-generation
cd demo-video-generation
export RSI_VIDEO_CACHE="$HOME/.cache/rsi-anything/video-generation"
rsi run --rounds 5
```

`python3 judge/prepare.py` 也会真实提交生成，不是离线预览命令。若要离线验证程序，运行仓库中的单元测试。只更换 `judge/brief.md` 的主题时，应同时修改初始描述与评分细则，然后开新运行；尺寸与时长由准备脚本固定为 704×512、约两秒。

## 评价与输出

程序确认服务返回了视频，并用 ffprobe 检查视频轨、尺寸和时长。模型从静帧判断杯子、材质、环境、蒸汽与构图，不评价音频，也不能确认完整运动是否顺滑。`pairwise: false`，本例按同一评分规则的分数保留较好版本，最终仍需播放检查。

`out/video.mp4` 是下载的真实服务结果，`preview.html` 可播放；`request.json`、`metadata.json`、`events.txt` 记录输入、事件编号、返回种子、视频哈希、服务版本和复用状态。`outputs: [out]` 保存逐轮产物。失败时输出 `error.json`，明确标记作品质量未知，不生成替代视频。

## 缓存与恢复

请求按服务地址、固定参数、描述与种子计算哈希。`RSI_VIDEO_CACHE` 可指定项目外的持久目录；未设置时使用用户缓存目录下的 `rsi-anything/video-generation`。缓存不能放在评分用的临时目录里。

提交前写入状态，取得事件编号后立即保存。等待中断时，下次继续等待同一事件；下载中断时复用已经完成的结果地址；已完成的相同请求直接复用经过哈希核对的成片。系统文件锁避免并发提交同一请求，进程结束会释放锁。

如果提交后没有拿到事件编号，程序保留 `submission_unknown` 或 `submission_pending`，不会自动重发。需要人根据缓存记录确认服务是否受理，再决定如何处理该项缓存。此限制避免超时重试悄悄重复生成。

## 接口与来源

- `RSI_VIDEO_ENDPOINT` 可覆盖公开服务基址，但目标必须提供相同的输入顺序与 `text_to_video` 接口；没有账号或付费回退。
- `RSI_VIDEO_TIMEOUT` 控制本次等待秒数，默认 480；主评审步骤上限为 900 秒。
- 先 `POST /gradio_api/call/text_to_video` 获得事件编号，再 `GET /gradio_api/call/text_to_video/<event_id>` 读取事件流；只接受 `event: complete` 的视频地址。
- [Gradio 官方调用说明](https://gradio.app/4.44.1/guides/querying-gradio-apps-with-curl) 提供两步调用协议；服务实测为 Gradio 5.42.0，使用该实例的 `/gradio_api` 前缀。
- [上游 README](https://huggingface.co/spaces/Lightricks/ltx-video-distilled/blob/main/README.md)、[上游实现](https://huggingface.co/spaces/Lightricks/ltx-video-distilled/blob/main/app.py) 与公开 `/config` 已于 2026-10-24 核查。每次新提交会核对输入顺序并保存服务版本；不能把上游声明型号当成远端运行时额外返回的模型证明。

本适配只使用 Python 标准库及 FFmpeg。离线接口和恢复测试已通过；真实片段、请求、错误凭证与视频解码结果保存在仓库 `examples/video-generation/`。完整多轮仍待可用生成资源；测试中的模拟响应仅用于单元测试。
