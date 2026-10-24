"""检查固定安排、任务覆盖及时间偏好，并输出一周日程。"""
import html
import json
import os
import re
from collections import Counter
from datetime import datetime
from pathlib import Path

DAYS = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]


def minute(value):
    if not isinstance(value, str) or not re.fullmatch(r"\d{2}:\d{2}", value):
        raise ValueError("时间必须为 HH:MM")
    parsed = datetime.strptime(value, "%H:%M")
    return parsed.hour * 60 + parsed.minute


def evaluate(requirements, schedule):
    tasks = {task["id"]: task for task in requirements["tasks"]}
    events, problems, counts, preferences = [], [], Counter(), Counter()
    for fixed in requirements["fixed"]:
        for day in fixed["days"]:
            events.append({"day": day, "start": fixed["start"], "end": fixed["end"],
                           "title": fixed["title"], "fixed": True})
    gates = {"valid_schedule": True, "no_conflicts": True, "within_awake_hours": True,
             "allowed_days": True, "correct_duration": True, "session_limits": True, "daily_load": True}
    sessions = schedule.get("sessions") if isinstance(schedule, dict) else None
    if not isinstance(sessions, list):
        sessions = []
        gates["valid_schedule"] = False
        problems.append("schedule.json 需要 sessions 数组。")
    daily = Counter()
    for index, session in enumerate(sessions, start=1):
        try:
            task = tasks[session["task"]]
            day = session["day"]
            if isinstance(day, bool) or not isinstance(day, int) or not 1 <= day <= 7:
                raise ValueError("day 必须为 1..7 的整数")
            start, end = minute(session["start"]), minute(session["end"])
            if end <= start:
                raise ValueError("结束时间必须晚于开始时间，不跨午夜")
        except (TypeError, KeyError, ValueError) as exc:
            gates["valid_schedule"] = False
            problems.append(f"第 {index} 项格式错误：{exc}")
            continue
        counts[task["id"]] += 1
        daily[day] += end - start
        if not minute(requirements["awake"]["start"]) <= start < end <= minute(requirements["awake"]["end"]):
            gates["within_awake_hours"] = False
            problems.append(f"{DAYS[day - 1]} {task['title']} 超出清醒时段。")
        if day not in task["days"]:
            gates["allowed_days"] = False
            problems.append(f"{task['title']} 不能安排在 {DAYS[day - 1]}。")
        if end - start != task["minutes"]:
            gates["correct_duration"] = False
            problems.append(f"{task['title']} 每次需要 {task['minutes']} 分钟，当前 {end - start} 分钟。")
        preferred = any(day in window["days"] and minute(window["start"]) <= start
                        and end <= minute(window["end"]) for window in task["preferred"])
        preferences[task["id"]] += int(preferred)
        events.append({"day": day, "start": session["start"], "end": session["end"],
                       "task": task["id"], "title": task["title"], "fixed": False, "preferred": preferred})
    for task_id, task in tasks.items():
        if counts[task_id] > task["sessions"]:
            gates["session_limits"] = False
            problems.append(f"{task['title']} 超过所需 {task['sessions']} 次。")
    for day, minutes in daily.items():
        if minutes > requirements["max_flexible_minutes_per_day"]:
            gates["daily_load"] = False
            problems.append(f"{DAYS[day - 1]} 活动共 {minutes} 分钟，超过每日上限。")
    events.sort(key=lambda event: (event["day"], event["start"], event["end"]))
    for index, event in enumerate(events):
        for other in events[index + 1:]:
            if other["day"] != event["day"]:
                break
            if minute(other["start"]) >= minute(event["end"]):
                break
            gates["no_conflicts"] = False
            problems.append(f"{DAYS[event['day'] - 1]} {event['title']} 与 {other['title']} 冲突。")
    total_weight = sum(task["sessions"] * task["weight"] for task in tasks.values())
    if not total_weight:
        raise ValueError("至少需要一个权重大于零的任务")
    coverage = sum(min(counts[key], task["sessions"]) * task["weight"] for key, task in tasks.items()) / total_weight
    preference = sum(min(preferences[key], task["sessions"]) * task["weight"] for key, task in tasks.items()) / total_weight
    details = [{"task": key, "title": task["title"], "required": task["sessions"], "scheduled": counts[key],
                "preferred": preferences[key], "weight": task["weight"]} for key, task in tasks.items()]
    missing = [f"{row['title']}还缺 {row['required'] - row['scheduled']} 次" for row in details if row["scheduled"] < row["required"]]
    mismatch = [f"{row['title']}有 {row['scheduled'] - row['preferred']} 次不在偏好时段"
                for row in details if row["scheduled"] > row["preferred"]]
    feedback = (f"任务覆盖 {coverage:.1%}，偏好覆盖 {preference:.1%}。\n"
                + "\n".join(problems + missing + mismatch or ["固定约束、任务次数和偏好全部满足。 "]))
    return {"score": round(70 * coverage + 30 * preference, 2), "gates": gates, "feedback": feedback,
            "metrics": {"coverage": round(coverage, 4), "preference_coverage": round(preference, 4),
                        "tasks": details, "conflicts_and_errors": problems, "daily_minutes": dict(daily)}}, events


def write_outputs(out, requirements, payload, events):
    title = requirements.get("title", "一周日程")
    md = [f"# {title}", "", payload["feedback"], ""]
    cards = []
    for day, name in enumerate(DAYS, start=1):
        md.extend([f"## {name}", "", "| 时间 | 安排 | 说明 |", "|---|---|---|"])
        items = []
        for event in (row for row in events if row["day"] == day):
            note = "固定安排" if event["fixed"] else "符合偏好" if event["preferred"] else "可调时间"
            time_range = event["start"] + "–" + event["end"]
            md.append(f"| {time_range} | {event['title']} | {note} |")
            items.append(f"<li class='{'fixed' if event['fixed'] else 'planned'}'><time>{html.escape(time_range)}</time>"
                         f"<strong>{html.escape(event['title'])}</strong><small>{note}</small></li>")
        md.append("")
        cards.append(f"<section><h2>{name}</h2><ul>{''.join(items)}</ul></section>")
    (out / "schedule.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    page = ("<!doctype html><html lang='zh-CN'><meta charset='utf-8'><meta name='viewport' content='width=device-width, initial-scale=1'>"
            f"<title>{html.escape(title)}</title><style>body{{margin:0;background:#f5f6f8;color:#1d2939;font:16px/1.5 system-ui}}"
            "main{max-width:1200px;margin:auto;padding:32px 20px}.week{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:16px}"
            "section{background:white;border-radius:14px;padding:16px}h2{margin:0 0 14px;font-size:19px}ul{padding:0;list-style:none}"
            "li{padding:10px 12px;margin:8px 0;border-left:3px solid #96a0b0;background:#f5f6f8}.planned{border-color:#287758;background:#edf7f2}"
            "time,small{display:block;color:#586579;font-size:13px}pre{white-space:pre-wrap;background:white;padding:16px;border-radius:12px}</style>"
            f"<main><h1>{html.escape(title)}</h1><p>得分 {payload['score']} · 约束{'全部满足' if all(payload['gates'].values()) else '尚未满足'}</p>"
            f"<pre>{html.escape(payload['feedback'])}</pre><div class='week'>{''.join(cards)}</div></main></html>")
    (out / "schedule.html").write_text(page, encoding="utf-8")
    (out / "schedule.json").write_text(json.dumps(events, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (out / "metrics.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main():
    out = Path("out")
    out.mkdir(exist_ok=True)
    requirements = {"title": "一周日程"}
    try:
        requirements = json.loads(Path("judge/requirements.json").read_text(encoding="utf-8"))
        schedule = json.loads(Path("schedule.json").read_text(encoding="utf-8"))
        payload, events = evaluate(requirements, schedule)
    except (OSError, ValueError, TypeError, KeyError) as exc:
        payload, events = {"score": 0, "gates": {"valid_schedule": False}, "feedback": f"日程无法评审：{exc}", "metrics": {}}, []
    write_outputs(out, requirements, payload, events)
    if os.environ.get("RSI_RESULT"):
        Path(os.environ["RSI_RESULT"]).write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    else:
        print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
