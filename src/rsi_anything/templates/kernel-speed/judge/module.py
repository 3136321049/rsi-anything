"""随机初始化的两次矩阵乘法与 Softmax，独立于任何语言模型或服务。"""
import math
import torch


def inputs(spec, seed):
    generator = torch.Generator(device="cuda").manual_seed(seed)
    x = torch.randn(spec["batch"], spec["features"], generator=generator, device="cuda", dtype=torch.float32)
    weight = torch.randn(spec["features"], spec["choices"], generator=generator, device="cuda", dtype=torch.float32) / math.sqrt(spec["features"])
    values = torch.randn(spec["choices"], spec["outputs"], generator=generator, device="cuda", dtype=torch.float32)
    return x, weight, values


def forward(x, weight, values, softmax):
    probabilities = softmax(x @ weight)
    return probabilities @ values
