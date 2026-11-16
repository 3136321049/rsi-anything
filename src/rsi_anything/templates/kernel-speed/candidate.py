"""Row softmax for contiguous 2-D tensors; the basic implementation uses one Triton program per row."""
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
    """Return a fresh output; never modify the input or reuse results across calls."""
    if x.ndim != 2 or not x.is_cuda or not x.is_contiguous():
        raise ValueError("input must be a contiguous 2-D CUDA tensor")
    if x.dtype not in (torch.float16, torch.float32) or min(x.shape) < 1 or x.shape[1] > 8192:
        raise ValueError("only non-empty float16/float32 tensors with at most 8192 items per row are supported")
    output = torch.empty_like(x)
    _row_softmax[(x.shape[0],)](x, output, x.shape[1], triton.next_power_of_2(x.shape[1]), num_warps=4)
    return output
