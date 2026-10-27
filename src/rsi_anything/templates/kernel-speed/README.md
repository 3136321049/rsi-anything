# D15：GPU Softmax 与小型推理模块

[English](README.en.md)

本包让 AI 修改 `candidate.py`，优化一个二维行 Softmax GPU 算子。初始候选由一个 Triton program 处理一行：读取、减去最大值、取指数、求和、归一化并写回。没有预先编写后续优化版本。可探索并行划分、启动参数和内存访问，效果需由实际设备测量决定。

**当前状态：模板与无 GPU 分支已实现；没有 GPU 实测或真实模型优化记录。** Mac 的 MPS 和 CPU 不用于此项计时。缺设备时状态为 `environment_unavailable`，分数为空；不要将模板测试通过当作算子提速结果。

## 先检查个人设备

首版限定 Linux x86_64、NVIDIA 计算能力 8.0 及以上、兼容 CUDA 的驱动，建议 Python 3.11。只在已经获准用于本个人项目的设备上执行；模板不会自动连接远程机器或租用资源。

```bash
rsi init kernel-speed my-kernel
cd my-kernel
python judge/check.py --probe
```

探测只读系统与依赖信息，不导入候选、不编译算子。它写入 `out/environment.json` 和 `out/report.md`：设备不可用退出码为 2，可用但未测量为 0。无 GPU 环境无需安装下面的大型依赖。

在已授权 GPU 机器上，按 [PyTorch 2.6 官方安装表](https://pytorch.org/get-started/previous-versions/) 选择驱动兼容的 CUDA 版本。此模板固定的起始组合是 PyTorch 2.6.0、Triton 3.2.0；例如 CUDA 12.4 构建：

```bash
python -m pip install torch==2.6.0 --index-url https://download.pytorch.org/whl/cu124
python -m pip install triton==3.2.0
python judge/check.py --probe
python judge/check.py
rsi check
rsi run --agent codex --rounds 6
```

必须使用与 `rsi` 相同的 Python。依赖版本也列于 `requirements-linux.txt`，不应在 Mac 上强行安装 CUDA 路径。上述 GPU 组合仍需在可用机器上验证，不保证某块设备有固定加速倍数。

## 输入、评价和产物

`judge/cases.json` 固定随机种子、形状、精度、数值容差、预热次数和计时配置。默认检查单元素、不规则列数、零值、大幅度数值、float32/float16；只接收连续二维非空 CUDA 张量，每行最多 8192 项。候选输出需保持形状、类型与设备，不能修改输入。

只有数值检查通过才计时。每种实现先编译与预热，然后使用 CUDA Event、结束同步、15 组各 20 次调用的中位数；同时保存包含同步的 CPU 墙钟时间。各实现轮换测量顺序，避免始终先测同一个。编译与首次检查耗时单列，不混入稳态耗时。输入在 GPU 上预先生成，不包含主机到设备拷贝，候选函数的输出分配属于计时范围。

三种单算子对照分别为：冻结的原始 PyTorch 组合实现、框架内置 `torch.softmax`、当前候选。得分只取三个固定性能用例上“内置耗时 / 候选耗时”的几何平均，至少提高 3% 才保留。更快的组合实现对照不能替代内置实现的比较结果。

另外把同一个候选放入 `输入矩阵乘法 → Softmax → 输出矩阵乘法` 的小型推理模块，检查完整输出并分别测内置版与替换版。模块输入和参数随机初始化、固定种子，float32，关闭 TF32；它没有语言模型权重、文本生成或服务请求。模块倍数单列，不能由单算子倍数推算，也不是端到端服务指标。

`out/metrics.json` 保存状态、数值误差、每次计时样本、中位数、单算子和模块倍数、候选/用例 SHA256；`out/environment.json` 保存硬件、CUDA、驱动和库版本；`out/report.md` 展示表格。`outputs: [out]` 供引擎保存每轮产物。无 GPU 或执行异常时，不产生虚构成绩，命令式评审报告失败并停止基线启动。

替换输入时，在新实验开始前修改冻结的 `judge/cases.json`，保持参考和候选接口一致，再提交并新开记录。一次运行内不得改变用例、精度、容差和计时配置。

## 公开来源与许可

2026-10-24 查阅并固定以下公开来源：

- [Triton v3.2.0 Softmax 教程](https://github.com/triton-lang/triton/blob/v3.2.0/python/tutorials/02-fused-softmax.py)：提供融合计算、归约与掩码的公开方法。`candidate.py` 使用相同的公开数学与 Triton 原语，本包独立编排最小的一行一程序实现；未采用上游持久化调度或宣传性能数字。上游 [MIT 许可证](https://github.com/triton-lang/triton/blob/v3.2.0/LICENSE) 的版权与许可保留在 `THIRD_PARTY.md`。
- [PyTorch CUDA Event](https://docs.pytorch.org/docs/stable/generated/torch.cuda.Event.html)：`judge/check.py` 使用其事件计时、等待和时间差接口；[PyTorch v2.6.0 许可](https://github.com/pytorch/pytorch/blob/v2.6.0/LICENSE) 为 BSD 风格许可，本包调用依赖，不复制其实现。
- [KernelBench](https://github.com/ScalingIntelligence/KernelBench) 的正确性与性能分开检查作为设计参考；没有导入其题目、数据或代码。小型推理模块和测试用例由本项目编写。

后续 GPU 基线与多轮记录应独立存入 `examples/kernel-speed/runs/`，同时保留失败和未提升轮次。
