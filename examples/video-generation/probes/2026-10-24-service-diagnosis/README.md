# 一次匿名服务诊断

[English](README.en.md)

2026-10-24 只提交一次生成请求：复用先前成功的 24 字符描述、种子、尺寸、两秒时长和其他参数。POST 返回 HTTP 200 和事件编号，事件流也返回 HTTP 200，但内容为 `event: error`、`data: null`。没有重试，也没有切换账号、IP 或付费入口。

- `request.json`：本次实际输入。
- `receipt.json`、`events.txt`：实际受理与失败事件。
- `service.json`：现场接口输入顺序、Gradio 版本、`show_error`、公开上游提交号与代码哈希。

这说明短描述也遇到服务错误；它不能证明具体是额度不足、GPU 不可用或某种内部异常。没有生成作品，因此质量分保持未知。
