"""Find the names closest to a query by edit distance (case-insensitive)."""

from bisect import insort
from collections import Counter
from functools import lru_cache


@lru_cache(maxsize=4)
def _prepare_names(names: tuple[str, ...]):
    texts = [name.lower() for name in names]
    counts = [Counter(text) for text in texts]
    widths = {}
    for count in counts:
        for char, frequency in count.items():
            widths[char] = max(widths.get(char, 0), frequency)
    slots = {}
    offset = 0
    for char, width in widths.items():
        slots[char] = (offset, width)
        offset += width
    prepared = []
    for name, text, count in zip(names, texts, counts):
        signature = 0
        for char, frequency in count.items():
            signature |= ((1 << frequency) - 1) << slots[char][0]
        prepared.append((name, text, len(text), signature))
    return slots, prepared


def _character_masks(pattern: str) -> dict[str, int]:
    masks = {}
    for i, char in enumerate(pattern):
        masks[char] = masks.get(char, 0) | (1 << i)
    return masks


def _distance(masks: dict[str, int], length: int, text: str) -> int:
    if not length:
        return len(text)

    # Myers 位向量算法：用整数的各个位保存相邻行之间的距离差。
    positive = ~0
    negative = 0
    score = length
    last = 1 << (length - 1)
    for char in text:
        equal = masks.get(char, 0)
        vertical = equal | negative
        horizontal = (((equal & positive) + positive) ^ positive) | equal
        plus = negative | ~(horizontal | positive)
        minus = positive & horizontal
        if plus & last:
            score += 1
        elif minus & last:
            score -= 1
        plus = (plus << 1) | 1
        positive = (minus << 1) | ~(vertical | plus)
        negative = vertical & plus
    return score


def edit_distance(a: str, b: str) -> int:
    return _distance(_character_masks(a), len(a), b)


def search(query: str, names: list[str], k: int = 5) -> list[str]:
    """Return the k names with the smallest edit distance to query; ties go to the alphabetically smaller name."""
    pattern = query.lower()
    masks = _character_masks(pattern)
    length = len(pattern)
    if isinstance(k, int) and 0 <= k < len(names):
        if k == 0:
            return []
        slots, prepared = _prepare_names(tuple(names))
        signature = 0
        for char, frequency in Counter(pattern).items():
            slot = slots.get(char)
            if slot is not None:
                offset, width = slot
                signature |= ((1 << min(frequency, width)) - 1) << offset
        best = []
        for name, text, text_length, text_signature in prepared:
            if len(best) == k:
                worst = best[-1]
                if (abs(length - text_length), name) >= worst:
                    continue
                # 每个字符按出现次数占位，交集位数就是可匹配字符数的上限。
                matches = bin(signature & text_signature).count("1")
                if (max(length, text_length) - matches, name) >= worst:
                    continue
            item = (_distance(masks, length, text), name)
            if len(best) < k:
                insort(best, item)
            elif item < best[-1]:
                insort(best, item)
                best.pop()
        return [name for _, name in best]
    scored = []
    for name in names:
        scored.append((_distance(masks, length, name.lower()), name))
    scored.sort()
    return [name for _, name in scored[:k]]
