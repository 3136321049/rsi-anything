"""Find the names closest to a query by edit distance (case-insensitive)."""


def edit_distance(a: str, b: str) -> int:
    rows = [[0] * (len(b) + 1) for _ in range(len(a) + 1)]
    for i in range(len(a) + 1):
        rows[i][0] = i
    for j in range(len(b) + 1):
        rows[0][j] = j
    for i in range(1, len(a) + 1):
        for j in range(1, len(b) + 1):
            cost = 0 if a[i - 1] == b[j - 1] else 1
            rows[i][j] = min(rows[i - 1][j] + 1, rows[i][j - 1] + 1, rows[i - 1][j - 1] + cost)
    return rows[len(a)][len(b)]


def search(query: str, names: list[str], k: int = 5) -> list[str]:
    """Return the k names with the smallest edit distance to query; ties go to the alphabetically smaller name."""
    scored = []
    for name in names:
        scored.append((edit_distance(query.lower(), name.lower()), name))
    scored.sort()
    return [name for _, name in scored[:k]]
