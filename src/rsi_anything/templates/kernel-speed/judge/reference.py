"""Frozen composed implementation and the framework built-in implementation."""
import torch


def composed_softmax(x):
    values = x.float()
    centered = values - values.max(dim=-1, keepdim=True).values
    exp = centered.exp()
    return (exp / exp.sum(dim=-1, keepdim=True)).to(x.dtype)


def native_softmax(x):
    return torch.softmax(x, dim=-1)
