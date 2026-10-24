"""Find the names closest to a query by edit distance (case-insensitive)."""

from bisect import insort


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
        best = []
        for name in names:
            text = name.lower()
            if len(best) == k:
                worst = best[-1]
                if (abs(length - len(text)), name) >= worst:
                    continue
                # 匹配字符数不会超过此上限，因此其余字符至少各需一次编辑。
                matches = min(length, sum(char in masks for char in text))
                if (max(length, len(text)) - matches, name) >= worst:
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
