# D15：本机环境检查记录

[English](README.md)

2026-10-24 在当前 Mac arm64 真实执行 `python judge/check.py --probe` 和默认检查，两次都退出 2，状态为 `environment_unavailable`，分数为空。模板要求 Linux x86_64 与 NVIDIA CUDA GPU，因此没有编译候选、运行数值测试或产生性能数字。

[环境信息](environment.json) · [检查结果](metrics.json) · [报告](report.md) · [验证记录](verification.json)

这份记录只证明无 GPU 环境能明确停止，不计作 D15 实验完成。后续需要已经获准用于本个人项目的兼容 GPU，按模板 README 安装依赖，再运行数值检查、真实多轮优化和小模块替换对照。没有自动租用设备或连接公司服务器。
