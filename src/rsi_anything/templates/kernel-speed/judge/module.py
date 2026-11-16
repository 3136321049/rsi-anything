"""Two randomly initialized matrix multiplications around a softmax, independent of any language model or service."""
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
