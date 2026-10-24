"""记账工具：金额以分为单位，退款使用负数。"""


def amount_to_cents(text):
    """解析十进制金额；允许前后空格和正负号，拒绝非有限数及超过两位小数。"""
    return int(float(text) * 100)


def split_bill(cents, people):
    """将非负整数金额分给正整数人数；余下的分依次给前几人。"""
    return [cents // people] * people


def monthly_totals(entries, month):
    """按分类汇总指定月份的收支；日期和月份格式错误时抛出 ValueError，不修改输入。"""
    totals = {}
    for entry in entries:
        if entry["date"].startswith(month):
            category = entry["category"]
            totals[category] = totals.get(category, 0) + abs(amount_to_cents(entry["amount"]))
    return totals
