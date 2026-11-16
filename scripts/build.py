"""Build the profile's public activity dashboard.

Run: python scripts/build.py [--offline] [--static]
Only dashboard.svg and activity.json are written. The anime artwork stays intact.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
import datetime as dt
import html
import json
import os
import re
import urllib.parse
import urllib.request
from pathlib import Path
from zoneinfo import ZoneInfo

from profile_art import INK, PANEL, LINE, WHITE, MUTED, CYAN, LILAC, CORAL, text, rect

USER = "Shakhzodmir"
OUT = Path(__file__).resolve().parents[1] / "assets"
SNAPSHOT = OUT / "activity.json"
SEOUL = ZoneInfo("Asia/Seoul")


def get(url, as_json=False):
    headers = {"User-Agent": "Shakhzodmir-profile", "Accept": "application/vnd.github+json" if as_json else "text/html"}
    token = os.environ.get("GITHUB_TOKEN")
    if token and urllib.parse.urlparse(url).hostname == "api.github.com":
        headers["Authorization"] = "Bearer " + token
    request = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(request, timeout=30) as response:
        body = response.read().decode("utf-8")
    return json.loads(body) if as_json else body


def parse_contributions(page, today):
    ids = {}
    for tag in re.findall(r"<(?:td|rect)\b[^>]*>", page):
        date = re.search(r'data-date="(\d{4}-\d\d-\d\d)"', tag)
        cid = re.search(r'id="([^"]+)"', tag)
        if date and cid and date.group(1) <= today:
            ids[date.group(1)] = cid.group(1)
    tooltips = {}
    for cid, value in re.findall(r'<tool-tip\b[^>]*?for="([^"]+)"[^>]*>(.*?)</tool-tip>', page, re.S):
        tooltips[cid] = html.unescape(re.sub(r"<[^>]+>", "", value)).strip()
    if not ids or any(cid not in tooltips for cid in ids.values()):
        raise ValueError("GitHub contribution calendar could not be read completely")
    days = []
    for date, cid in ids.items():
        tip = tooltips[cid].replace(",", "")
        count = re.match(r"(\d+)\s+contribution", tip, re.I)
        if count:
            n = int(count.group(1))
        elif tip.lower().startswith("no contributions"):
            n = 0
        else:
            raise ValueError("Unrecognized contribution tooltip")
        days.append([date, n])
    return sorted(days)


def languages():
    repos = []
    page = 1
    while True:
        batch = get(f"https://api.github.com/users/{USER}/repos?per_page=100&type=owner&page={page}", True)
        repos.extend(r for r in batch if not r.get("fork") and not r.get("private"))
        if len(batch) < 100:
            break
        page += 1
    totals = {}
    with ThreadPoolExecutor(max_workers=6) as pool:
        for distribution in pool.map(lambda repo: get(repo["languages_url"], True), repos):
            for name, count in distribution.items():
                totals[name] = totals.get(name, 0) + count
    return sorted(totals.items(), key=lambda pair: (-pair[1], pair[0])), len(repos)


def streaks(days, today):
    counts = {dt.date.fromisoformat(date): n for date, n in days if date <= today.isoformat()}
    best = run = 0
    previous = None
    for date, count in sorted(counts.items()):
        contiguous = previous is not None and date - previous == dt.timedelta(days=1)
        run = (run + 1 if contiguous else 1) if count else 0
        best = max(best, run)
        previous = date
    cursor = today if counts.get(today, 0) else today - dt.timedelta(days=1)
    current = 0
    while counts.get(cursor, 0) > 0:
        current += 1
        cursor -= dt.timedelta(days=1)
    return current, best


def day_label(n):
    return f"{n} day" if n == 1 else f"{n} days"


def collect():
    today = dt.datetime.now(SEOUL).date()
    days = parse_contributions(get(f"https://github.com/users/{USER}/contributions"), today.isoformat())
    langs, count = languages()
    return {
        "user": USER,
        "as_of": today.isoformat(),
        "scope": "Public repositories excluding forks; GitHub contribution calendar",
        "days": days,
        "languages": langs,
        "public_repos": count,
    }


def dashboard(data, static=False):
    days, langs = data["days"], data["languages"]
    today = dt.date.fromisoformat(data["as_of"])
    current, best = streaks(days, today)
    total = sum(n for _, n in days)
    label = f"Public GitHub activity for {USER}, refreshed {data['as_of']}. {total} contributions, current streak {day_label(current)}, longest streak {day_label(best)}, {data['public_repos']} non-fork public repositories."
    css = "" if static else "@keyframes beacon{50%{opacity:.35}}.beacon{animation:beacon 4s ease-in-out infinite}"
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="514" viewBox="0 0 1200 514" role="img" aria-label="'+html.escape(label, quote=True)+'">',
        "<title>"+html.escape(label)+"</title>",
        '<defs><linearGradient id="area" x1="0" y1="0" x2="0" y2="1"><stop stop-color="'+LILAC+'" stop-opacity=".24"/><stop offset="1" stop-color="'+LILAC+'" stop-opacity="0"/></linearGradient>',
        '<linearGradient id="plot"><stop stop-color="'+LILAC+'"/><stop offset="1" stop-color="'+CYAN+'"/></linearGradient></defs>',
        "<style>"+css+"@media(prefers-reduced-motion:reduce){*{animation:none!important}}</style>",
    ]
    metrics = [
        ("12 MONTH CONTRIBUTIONS", f"{total:,}", LILAC),
        ("CURRENT STREAK", day_label(current), CORAL),
        ("LONGEST STREAK", day_label(best), CYAN),
        ("PUBLIC REPOS · NO FORKS", str(data["public_repos"]), "#B7DE98"),
    ]
    for i, (caption, value, color) in enumerate(metrics):
        x = i * 305
        parts += [rect(x+.5, .5, 284, 124, PANEL, 16, LINE),
                  text(x+24, 34, caption, 14, MUTED, 500, True),
                  text(x+24, 91, value, 44, color, 700),
                  f'<path d="M{x+24} 107 H{x+260}" stroke="{color}" stroke-opacity=".45" stroke-width="2"/>']
    parts += [rect(.5,144.5,779,330,PANEL,18,LINE),
              text(27,184,"Contribution signal",25,WHITE,600),
              text(751,184,"WEEKLY / 12 MONTHS",13,MUTED,500,True,'text-anchor="end"'),
              rect(800.5,144.5,399,330,PANEL,18,LINE),
              text(828,184,"Public code",25,WHITE,600)]
    # Group real calendar dates into Monday-aligned weeks.
    weeks = {}
    for day, count in days:
        date = dt.date.fromisoformat(day)
        start = date-dt.timedelta(days=date.weekday())
        weeks[start] = weeks.get(start, 0)+count
    ordered = sorted(weeks.items())
    peak = max((n for _, n in ordered), default=0) or 1
    x0,x1,yt,yb = 34,730,225,415
    points = [(x0+(x1-x0)*i/max(len(ordered)-1,1), yb-(yb-yt)*n/peak) for i,(_,n) in enumerate(ordered)]
    for i in range(4):
        y = yb-(yb-yt)*i/3
        parts.append(f'<path d="M{x0} {y:.1f} H{x1}" stroke="{LINE}" stroke-opacity=".7"/>')
        parts.append(text(752, y+4, round(peak*i/3), 12, MUTED, extra='text-anchor="end"'))
    if points:
        coordinates = " ".join(f"{x:.1f},{y:.1f}" for x,y in points)
        outline = "M"+" L".join(f"{x:.1f} {y:.1f}" for x,y in points)
        parts += [f'<path d="{outline} L{x1} {yb} L{x0} {yb}Z" fill="url(#area)"/>',
                  f'<polyline points="{coordinates}" fill="none" stroke="url(#plot)" stroke-width="3" stroke-linejoin="round" stroke-linecap="round"/>',
                  f'<circle cx="{points[-1][0]:.1f}" cy="{points[-1][1]:.1f}" r="5" fill="{CYAN}" class="beacon"/>']
        marks = sorted(set([0,len(ordered)//3,len(ordered)*2//3,len(ordered)-1]))
        for i in marks:
            parts.append(text(points[i][0],449,ordered[i][0].strftime("%b %y"),13,MUTED,extra='text-anchor="middle"'))
    total_bytes = sum(n for _,n in langs) or 1
    colors = [LILAC,CYAN,CORAL,"#F7D38B","#B7DE98"]
    for i,((name,count),color) in enumerate(zip(langs[:5],colors)):
        y = 229+i*41
        pct = count/total_bytes*100
        parts += [f'<circle cx="830" cy="{y-5}" r="4" fill="{color}"/>',
                  text(845,y,name,18,WHITE),
                  text(1170,y,f"{pct:.1f}%",16,MUTED,500,True,extra='text-anchor="end"'),
                  rect(845,y+9,325,4,LINE,2,LINE),
                  rect(845,y+9,max(325*count/total_bytes,1),4,color,2,color)]
    other = sum(n for _,n in langs[5:])/total_bytes*100
    note = f"{len(langs)} languages · by bytes"
    if len(langs)>5:
        note += f" · other {other:.1f}%"
    parts += [text(828,454,note,13,MUTED),
              text(5,502,"PUBLIC ACTIVITY / "+data["as_of"],13,MUTED,500,True),
              text(1194,502,"REFRESHED DAILY · ASIA/SEOUL",13,MUTED,500,True,'text-anchor="end"'),
              "</svg>\n"]
    return "\n".join(parts)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--offline", action="store_true", help="Rebuild from the last successful data snapshot")
    parser.add_argument("--static", action="store_true", help="Disable decorative motion")
    args = parser.parse_args()
    if args.offline:
        data = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
    else:
        # Leave existing assets intact if the network or source format fails.
        data = collect()
    svg = dashboard(data, args.static)
    OUT.mkdir(parents=True, exist_ok=True)
    SNAPSHOT.write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    (OUT/"dashboard.svg").write_text(svg,encoding="utf-8")
    print(f"Dashboard refreshed: {sum(n for _,n in data['days'])} contributions, {data['public_repos']} public repositories, as of {data['as_of']}")


if __name__ == "__main__":
    main()
