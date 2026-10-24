"""二维连续张量的行 Softmax；基本实现采用一个 Triton program 处理一行。"""
import torch
import triton
import triton.language as tl


@triton.jit
def _row_softmax(src, dst, WIDTH: tl.constexpr, BLOCK: tl.constexpr):
    row = tl.program_id(0)
    columns = tl.arange(0, BLOCK)
    offsets = row * WIDTH + columns
    values = tl.load(src + offsets, mask=columns < WIDTH, other=-float("inf")).to(tl.float32)
    shifted = values - tl.max(values, axis=0)
    weights = tl.exp(shifted)
    normalized = weights / tl.sum(weights, axis=0)
    tl.store(dst + offsets, normalized, mask=columns < WIDTH)


def softmax(x):
    """返回独立输出；不改变输入，不复用跨调用结果。"""
    if x.ndim != 2 or not x.is_cuda or not x.is_contiguous():
        raise ValueError("输入需要连续二维 CUDA 张量")
    if x.dtype not in (torch.float16, torch.float32) or min(x.shape) < 1 or x.shape[1] > 8192:
        raise ValueError("仅支持 float16/float32、非空且每行至多 8192 项")
    output = torch.empty_like(x)
    _row_softmax[(x.shape[0],)](x, output, x.shape[1], triton.next_power_of_2(x.shape[1]), num_warps=4)
    return output
