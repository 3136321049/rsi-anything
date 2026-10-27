# D15：GPU 算子优化，待实测

[English](README.en.md)

模板以 Softmax 为例：助手修改 Triton 算子，先与 PyTorch 参考结果做数值比较，再测单算子与小型推理模块的耗时。默认输入、设备要求和启动命令见 [模板说明](../../src/rsi_anything/templates/kernel-speed/README.md)，公开参考与许可证见 [第三方说明](../../src/rsi_anything/templates/kernel-speed/THIRD_PARTY.md)。

当前没有个人 NVIDIA GPU。真实本机探测返回 `environment_unavailable`，退出码 2，分数为空；没有导入候选或执行 GPU 测量。见 [探测说明](probes/2026-10-24-local/README.md)及[验证凭证](probes/2026-10-24-local/verification.json)。

按资源例外交付模板、固定输入、无设备提示和补跑入口，不计入 13 个完整多轮领域。后续取得个人 GPU 后，先执行模板中的基线检查，再用个人助手做多轮优化，保存设备信息、正确性、算子耗时和小模块对照。当前不租设备，也不使用公司资源。
