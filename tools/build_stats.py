"""Generates the data-driven cards: activity, pulse and code time.

Run by .github/workflows/metrics.yml once a day. Without a token (or without
network) it still writes valid cards in a clearly "not synced yet" state, so
the README never shows a broken image.

    python tools/build_stats.py

Environment:
    GH_USERNAME        profile to read (default: Roylizzz)
    METRICS_TOKEN      PAT with read:user -> includes private contribution counts
    GITHUB_TOKEN       fallback, public contributions only
    WAKATIME_API_KEY   optional, turns the code time card into real data
"""

from __future__ import annotations

import base64
import json
import os
import urllib.error
import urllib.request
from datetime import date, datetime, timedelta, timezone

import pixelfont as pf
from theme import PALETTES, card, heat, mono, svg, write

USERNAME = os.environ.get("GH_USERNAME", "Roylizzz")
TIMEOUT = 25

GRAPHQL = """
query($login: String!, $from: DateTime!, $to: DateTime!) {
  user(login: $login) {
    createdAt
    followers { totalCount }
    repositories(first: 100, ownerAffiliations: OWNER, isFork: false) { totalCount }
    contributionsCollection(from: $from, to: $to) {
      totalCommitContributions
      totalPullRequestContributions
      totalIssueContributions
      restrictedContributionsCount
      contributionCalendar {
        totalContributions
        weeks { contributionDays { date weekday contributionCount } }
      }
    }
  }
}
"""


# --------------------------------------------------------------------------
# data
# --------------------------------------------------------------------------


def fetch_github(token: str) -> dict | None:
    to = datetime.now(timezone.utc)
    frm = to - timedelta(days=365)
    payload = json.dumps(
        {
            "query": GRAPHQL,
            "variables": {
                "login": USERNAME,
                "from": frm.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "to": to.strftime("%Y-%m-%dT%H:%M:%SZ"),
            },
        }
    ).encode()
    request = urllib.request.Request(
        "https://api.github.com/graphql",
        data=payload,
        headers={
            "Authorization": f"bearer {token}",
            "Content-Type": "application/json",
            "User-Agent": f"{USERNAME}-profile-metrics",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
            body = json.load(response)
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        print(f"  ! github fetch failed: {exc}")
        return None

    if body.get("errors"):
        print(f"  ! github returned errors: {body['errors'][0].get('message')}")
        return None

    user = (body.get("data") or {}).get("user")
    if not user:
        print("  ! github returned no user")
        return None

    contributions = user["contributionsCollection"]
    calendar = contributions["contributionCalendar"]
    days = [
        (day["date"], day["contributionCount"], day["weekday"])
        for week in calendar["weeks"]
        for day in week["contributionDays"]
    ]
    days.sort()

    current, longest, run = 0, 0, 0
    today = date.today()
    for iso, count, _ in days:
        if count:
            run += 1
            longest = max(longest, run)
        else:
            run = 0
    # a streak still counts if today simply has not happened yet
    for iso, count, _ in reversed(days):
        day = date.fromisoformat(iso)
        if day > today:
            continue
        if count:
            current += 1
        elif day == today:
            continue
        else:
            break

    by_weekday = [0] * 7
    for _, count, weekday in days:
        by_weekday[weekday] += count
    busiest = max(range(7), key=lambda i: by_weekday[i])

    return {
        "total": calendar["totalContributions"],
        "commits": contributions["totalCommitContributions"],
        "pull_requests": contributions["totalPullRequestContributions"],
        "issues": contributions["totalIssueContributions"],
        "private": contributions["restrictedContributionsCount"],
        "repos": user["repositories"]["totalCount"],
        "followers": user["followers"]["totalCount"],
        "active_days": sum(1 for _, count, _ in days if count),
        "current_streak": current,
        "longest_streak": longest,
        "busiest_weekday": busiest,
        "days": days,
        "since": user["createdAt"][:4],
        "synced": today.isoformat(),
    }


def fetch_wakatime(api_key: str) -> dict | None:
    token = base64.b64encode(api_key.encode()).decode()
    request = urllib.request.Request(
        "https://wakatime.com/api/v1/users/current/stats/last_7_days",
        headers={"Authorization": f"Basic {token}", "User-Agent": "profile-metrics"},
    )
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
            body = json.load(response)
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        print(f"  ! wakatime fetch failed: {exc}")
        return None

    data = body.get("data") or {}
    languages = [
        {
            "name": entry["name"],
            "percent": entry["percent"],
            "text": entry["text"],
        }
        for entry in (data.get("languages") or [])[:5]
    ]
    if not languages:
        return None
    return {
        "total": data.get("human_readable_total", "").strip() or "0 hrs",
        "daily": data.get("human_readable_daily_average", "").strip() or "0 hrs",
        "languages": languages,
    }


# --------------------------------------------------------------------------
# drawing
# --------------------------------------------------------------------------

WEEKDAYS = ["sunday", "monday", "tuesday", "wednesday", "thursday", "friday", "saturday"]


def header(pal: dict, title: str, right: str, width: int) -> str:
    return (
        pf.draw(title, 28, 24, 4, 1, pal["accent2"])
        + mono(right, width - 26, 42, 10.5, pal["dim"], anchor="end", spacing=1.4)
        + f'<path d="M26 66h{width - 52}" stroke="{pal["border"]}" stroke-width="1"/>'
    )


CARD_W, CARD_H = 480, 210


def key_value(pal: dict, x: float, y: float, key: str, value: str, width: float) -> str:
    """One dim key on the left, bright value on the right of a fixed column."""
    return mono(key, x, y, 11.5, pal["dim"]) + mono(
        value, x + width, y, 11.5, pal["hi"], weight=600, anchor="end"
    )


def side_stat(pal: dict, x: float, y: float, value: str, label: str) -> str:
    return mono(value, x, y, 21, pal["glow"], weight=700, spacing=-0.5) + pf.draw(
        label, int(x) + 8 + 13 * len(value), int(y) - 12, 2, 1, pal["accent"]
    )


def render_stats(pal: dict, data: dict | None) -> str:
    W, H = CARD_W, CARD_H
    out = [card(pal, W, H)]
    out.append(header(pal, "ACTIVITY", "last 12 months", W))

    if data is None:
        out.append(
            mono("waiting for the first sync", W // 2, 128, 13, pal["dim"], anchor="middle")
        )
        out.append(
            mono(
                "$ workflow metrics.yml",
                W // 2,
                152,
                11,
                pal["accent"],
                anchor="middle",
                opacity=0.8,
            )
        )
        return svg(W, H, "".join(out))

    # left: the headline number
    out.append(
        mono(f"{data['total']:,}", 28, 112, 32, pal["glow"], weight=700, spacing=-1)
    )
    out.append(pf.draw("CONTRIBUTIONS", 29, 120, 2, 1, pal["accent"]))
    out.append(key_value(pal, 28, 156, "commits", f"{data['commits']:,}", 196))
    out.append(key_value(pal, 28, 174, "active days", str(data["active_days"]), 196))

    # right: the streaks
    out.append(f'<path d="M252 84v100" stroke="{pal["border"]}" stroke-width="1"/>')
    out.append(side_stat(pal, 276, 110, str(data["current_streak"]), "DAY STREAK"))
    out.append(side_stat(pal, 276, 146, str(data["longest_streak"]), "BEST RUN"))
    out.append(
        mono(f"busiest · {WEEKDAYS[data['busiest_weekday']]}", 276, 176, 11, pal["dim"])
    )

    out.append(f'<path d="M26 186h{W - 52}" stroke="{pal["border"]}" stroke-width="1"/>')
    out.append(mono(f"@{USERNAME} · since {data['since']}", 28, 202, 10.5, pal["accent"]))
    out.append(
        mono(f"synced {data['synced']}", W - 26, 202, 10.5, pal["dim"], anchor="end")
    )
    return svg(W, H, "".join(out))


def render_pulse(pal: dict, data: dict | None) -> str:
    W, H = CARD_W, CARD_H
    weeks = 26
    cell, gap = 11, 3
    out = [card(pal, W, H)]
    out.append(header(pal, "PULSE", f"last {weeks} weeks", W))

    ramp = heat(pal)
    if data is None:
        grid = [[0] * 7 for _ in range(weeks)]
        peak = 1
    else:
        days = {iso: count for iso, count, _ in data["days"]}
        last = date.fromisoformat(data["days"][-1][0])
        start = last - timedelta(days=last.weekday() + 1 + (weeks - 1) * 7)
        grid = []
        for week in range(weeks):
            column = []
            for weekday in range(7):
                day = start + timedelta(days=week * 7 + weekday)
                column.append(days.get(day.isoformat(), 0))
            grid.append(column)
        peak = max((max(col) for col in grid), default=0) or 1

    x0 = (W - (weeks * (cell + gap) - gap)) // 2
    y0 = 82
    for week, column in enumerate(grid):
        for weekday, count in enumerate(column):
            if count <= 0:
                level = 0
            else:
                level = 1 + min(3, int(3 * (count - 1) / max(1, peak - 1)))
            out.append(
                f'<rect x="{x0 + week * (cell + gap)}" y="{y0 + weekday * (cell + gap)}" '
                f'width="{cell}" height="{cell}" rx="3" fill="{ramp[level]}"/>'
            )

    legend_y = y0 + 7 * (cell + gap) + 20
    out.append(mono("less", x0, legend_y, 10, pal["dim"]))
    for i, colour in enumerate(ramp):
        out.append(
            f'<rect x="{x0 + 34 + i * 14}" y="{legend_y - 9}" width="10" height="10" rx="2" '
            f'fill="{colour}"/>'
        )
    out.append(mono("more", x0 + 34 + len(ramp) * 14 + 6, legend_y, 10, pal["dim"]))
    if data is not None:
        out.append(
            mono(
                f"{data['active_days']} days with a commit",
                W - 26,
                legend_y,
                10.5,
                pal["accent"],
                anchor="end",
            )
        )
    else:
        out.append(
            mono("waiting for the first sync", W - 26, legend_y, 10.5, pal["dim"], anchor="end")
        )
    return svg(W, H, "".join(out))


def render_codetime(pal: dict, waka: dict | None) -> str:
    W, H = CARD_W, CARD_H
    out = [
        "<style>.eq rect{animation:eq 1.8s ease-in-out infinite;transform-box:fill-box;transform-origin:center bottom}"
        "@keyframes eq{0%,100%{transform:scaleY(.35)}50%{transform:scaleY(1)}}"
        ".bk{animation:bk 1.05s steps(1) infinite}@keyframes bk{50%{opacity:0}}</style>",
        card(pal, W, H),
    ]
    out.append(header(pal, "CODE TIME", "wakatime · last 7 days", W))

    if waka is None:
        heights = [26, 48, 34, 62, 40, 54, 30, 52, 42, 64, 32, 50]
        for i, bar in enumerate(heights):
            out.append(
                f'<g class="eq"><rect x="{28 + i * 34}" y="{166 - bar}" width="18" '
                f'height="{bar}" rx="4" fill="{pal["accent"]}" '
                f'opacity="{0.25 + (i % 4) * 0.13:.2f}" '
                f'style="animation-delay:{round(i * 0.13, 2)}s"/></g>'
            )
        out.append(f'<path d="M26 182h{W - 52}" stroke="{pal["border"]}" stroke-width="1"/>')
        out.append(
            mono("$ waka --connect", 28, 202, 12, pal["text"])
            + f'<rect x="150" y="191" width="8" height="13" fill="{pal["glow"]}" class="bk"/>'
        )
        out.append(
            mono("no api key yet — see SETUP.md", W - 26, 202, 10.5, pal["dim"], anchor="end")
        )
        return svg(W, H, "".join(out))

    y = 90
    bar_x, bar_w = 168, 240
    for entry in waka["languages"]:
        percent = max(0.0, min(100.0, float(entry["percent"])))
        out.append(mono(entry["name"][:14].lower(), 28, y + 4, 11.5, pal["text"]))
        out.append(
            f'<rect x="{bar_x}" y="{y - 7}" width="{bar_w}" height="10" rx="5" '
            f'fill="{pal["accent"]}" opacity="0.14"/>'
        )
        out.append(
            f'<rect x="{bar_x}" y="{y - 7}" width="{max(6, bar_w * percent / 100):.1f}" '
            f'height="10" rx="5" fill="{pal["accent2"]}"/>'
        )
        out.append(
            mono(f"{percent:.0f}%", W - 26, y + 4, 10.5, pal["dim"], anchor="end")
        )
        y += 20

    out.append(f'<path d="M26 182h{W - 52}" stroke="{pal["border"]}" stroke-width="1"/>')
    out.append(mono(waka["total"], 28, 202, 12.5, pal["hi"], weight=700))
    out.append(mono(f"{waka['daily']} / day", W - 26, 202, 10.5, pal["accent"], anchor="end"))
    return svg(W, H, "".join(out))


# --------------------------------------------------------------------------
# build
# --------------------------------------------------------------------------


def main() -> None:
    token = os.environ.get("METRICS_TOKEN") or os.environ.get("GITHUB_TOKEN")
    waka_key = os.environ.get("WAKATIME_API_KEY")

    print("building data cards...")
    data = fetch_github(token) if token else None
    if token is None:
        print("  ! no token in env, writing placeholder cards")
    waka = fetch_wakatime(waka_key) if waka_key else None

    for pal in PALETTES:
        write(f"stats-{pal['name']}.svg", render_stats(pal, data))
        write(f"pulse-{pal['name']}.svg", render_pulse(pal, data))
        write(f"codetime-{pal['name']}.svg", render_codetime(pal, waka))
    print("done.")


if __name__ == "__main__":
    main()
