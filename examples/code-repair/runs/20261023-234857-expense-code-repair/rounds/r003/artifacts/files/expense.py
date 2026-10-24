"""记账工具：金额以分为单位，退款使用负数。"""

import re
from datetime import date


def amount_to_cents(text):
    """解析十进制金额；允许前后空格和正负号，拒绝非有限数及超过两位小数。"""
    match = re.fullmatch(r"([+-]?)([0-9]*)(?:\.([0-9]{0,2}))?", text.strip())
    if match is None:
        raise ValueError("金额必须是最多两位小数的有限十进制数")
    sign, whole, fraction = match.groups()
    if not whole and not fraction:
        raise ValueError("金额必须包含数字")
    cents = int(whole or "0") * 100 + int((fraction or "").ljust(2, "0"))
    return -cents if sign == "-" else cents


def split_bill(cents, people):
    """将非负整数金额分给正整数人数；余下的分依次给前几人。"""
    if type(cents) is not int or cents < 0:
        raise ValueError("金额必须是非负整数分")
    if type(people) is not int or people <= 0:
        raise ValueError("人数必须是正整数")
    share, remainder = divmod(cents, people)
    return [share + (index < remainder) for index in range(people)]


def monthly_totals(entries, month):
    """按分类汇总指定月份的收支；日期和月份格式错误时抛出 ValueError，不修改输入。"""
    if not isinstance(month, str) or re.fullmatch(r"[0-9]{4}-[0-9]{2}", month) is None:
        raise ValueError("月份必须是有效的 YYYY-MM")
    date.fromisoformat(month + "-01")
    totals = {}
    for entry in entries:
        entry_date = entry["date"]
        if not isinstance(entry_date, str) or re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", entry_date) is None:
            raise ValueError("日期必须是有效的 YYYY-MM-DD")
        date.fromisoformat(entry_date)
        if entry_date[:7] == month:
            category = entry["category"]
            totals[category] = totals.get(category, 0) + amount_to_cents(entry["amount"])
    return totals
