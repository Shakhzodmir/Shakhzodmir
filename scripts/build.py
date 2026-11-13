"""Builds the animated SVGs for the profile README: hero banner, divider, stats dashboard.
Run: python scripts/build.py [--static]   (--static freezes animations, for previews)"""
import io, json, os, random, re, sys, urllib.request, datetime as dt

USER = "Shakhzodmir"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets")
STATIC = "--static" in sys.argv
FONT = "'Segoe UI','Noto Sans','Helvetica Neue',Arial,sans-serif"
BG, CARD, TEXT, MUTED = "#1a1b27", "#1f2335", "#c0caf5", "#7a84b0"
INDIGO, PURPLE, PINK, CYAN, GREEN, YELLOW = "#5B4FE9", "#bb9af7", "#f7768e", "#7dcfff", "#9ece6a", "#e0af68"
FREEZE = "*{animation:none!important}" if STATIC else ""


def get(url, as_json=False):
    req = urllib.request.Request(url, headers={"User-Agent": "profile-readme", "Accept": "application/vnd.github+json" if as_json else "text/html"})
    tok = os.environ.get("GITHUB_TOKEN")
    if tok and "api.github.com" in url:
        req.add_header("Authorization", "Bearer " + tok)
    with urllib.request.urlopen(req, timeout=30) as r:
        data = r.read().decode("utf-8")
    return json.loads(data) if as_json else data


def contributions():
    html = get("https://github.com/users/%s/contributions" % USER)
    ids = {}
    for tag in re.findall(r"<td[^>]*contribution-day-component[^>]*>", html):
        d = re.search(r'data-date="(\d{4}-\d\d-\d\d)"', tag)
        i = re.search(r'id="(contribution-day-component-[\d-]+)"', tag)
        if d and i:
            ids[d.group(1)] = i.group(1)
    tips = dict(re.findall(r'<tool-tip[^>]*?for="(contribution-day-component-[\d-]+)"[^>]*>\s*([^<]+?)\s*</tool-tip>', html))
    days = {}
    for date, cid in ids.items():
        m = re.match(r"(\d+)", tips.get(cid, "").replace(",", ""))
        days[date] = int(m.group(1)) if m else 0
    if not days:
        raise SystemExit("could not read the contribution calendar")
    return sorted(days.items())


def languages():
    repos = get("https://api.github.com/users/%s/repos?per_page=100&type=owner" % USER, True)
    total = {}
    for r in repos:
        if r.get("fork"):
            continue
        for lang, n in get(r["languages_url"], True).items():
            total[lang] = total.get(lang, 0) + n
    return sorted(total.items(), key=lambda kv: -kv[1]), len(repos)


def streaks(days):
    today = dt.date.today().isoformat()
    cur = best = run = 0
    for d, n in days:
        run = run + 1 if n else 0
        best = max(best, run)
    for d, n in reversed(days):
        if n:
            cur += 1
        elif d != today:
            break
    return cur, best


def write(name, svg):
    os.makedirs(OUT, exist_ok=True)
    io.open(os.path.join(OUT, name), "w", encoding="utf-8", newline="\n").write(svg)


def hero():
    W, H = 1200, 320
    rnd = random.Random(11)
    petals = []
    for i in range(22):
        x, s, dur, delay, drift = rnd.randint(0, W), rnd.uniform(0.6, 1.5), rnd.uniform(7, 14), rnd.uniform(-14, 0), rnd.randint(60, 220)
        col = rnd.choice([PINK, "#ffb7c5", PURPLE, "#ff9eb5"])
        petals.append(
            '<g style="animation:fall %.1fs linear %.1fs infinite;--dx:%dpx" transform="translate(%d,-20)">'
            '<path d="M0 0 C6 -9 16 -6 14 4 C12 12 3 14 0 8 C-2 4 -2 2 0 0Z" fill="%s" opacity="0.85" transform="scale(%.2f)" '
            'style="animation:spin %.1fs ease-in-out infinite alternate;transform-box:fill-box;transform-origin:center"/></g>'
            % (dur, delay, drift, x, col, s, dur / 2))
    stars = "".join(
        '<circle cx="%d" cy="%d" r="%.1f" fill="#fff" style="animation:twinkle %.1fs ease-in-out %.1fs infinite"/>'
        % (rnd.randint(0, W), rnd.randint(0, 170), rnd.uniform(0.6, 1.8), rnd.uniform(2, 5), rnd.uniform(-5, 0)) for _ in range(60))
    grid = "".join('<line x1="%.0f" y1="215" x2="%d" y2="%d" stroke="%s" stroke-opacity="0.35"/>' % (600 + (x - 600) * 0.15, x, H, INDIGO) for x in range(-1200, 2401, 120))
    hl = "".join('<line x1="0" x2="%d" y1="0" y2="0" stroke="%s" stroke-opacity="0.35" style="animation:floor 4s linear %.1fs infinite"/>' % (W, PURPLE, -i * 0.8) for i in range(5))
    bands = "".join('<rect x="800" y="%d" width="260" height="%d" fill="#241b4d"/>' % (y, h) for y, h in [(150, 3), (166, 5), (182, 7), (198, 9)])
    css = """
    @keyframes fall{0%{transform:translate(0,-30px)}100%{transform:translate(var(--dx),370px)}}
    @keyframes spin{0%{transform:rotate(-40deg) scale(1)}100%{transform:rotate(160deg) scale(.8)}}
    @keyframes twinkle{0%,100%{opacity:.15}50%{opacity:1}}
    @keyframes floor{0%{transform:translateY(215px);opacity:0}15%{opacity:1}100%{transform:translateY(330px);opacity:1}}
    @keyframes sun{0%,100%{transform:translateY(0)}50%{transform:translateY(-8px)}}
    @keyframes rise{0%{opacity:0;transform:translateY(26px)}100%{opacity:1;transform:translateY(0)}}
    @keyframes sheen{0%{transform:translateX(-700px)}60%,100%{transform:translateX(900px)}}
    @keyframes draw{0%{stroke-dashoffset:1}100%{stroke-dashoffset:0}}
    @keyframes glow{0%,100%{opacity:.35}50%{opacity:.6}}
    .name{animation:rise 1.1s cubic-bezier(.2,.8,.2,1) .2s both}
    .sub{animation:rise 1.1s cubic-bezier(.2,.8,.2,1) .6s both}
    .jp{animation:rise 1.4s cubic-bezier(.2,.8,.2,1) 1s both}
    """ + FREEZE
    svg = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="Shakhzod Miraliev, UI/UX Designer and Developer">
<defs>
<linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#0f1020"/><stop offset=".62" stop-color="#241b4d"/><stop offset="1" stop-color="#3b1d55"/></linearGradient>
<linearGradient id="sunG" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#ffd1a6"/><stop offset=".5" stop-color="{PINK}"/><stop offset="1" stop-color="{INDIGO}"/></linearGradient>
<linearGradient id="txt" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#ffffff"/><stop offset=".5" stop-color="#d9d2ff"/><stop offset="1" stop-color="#ffc2d1"/></linearGradient>
<linearGradient id="sh" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".5" stop-color="#fff" stop-opacity=".9"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>
<filter id="blur" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="30"/></filter>
<clipPath id="clip"><rect width="{W}" height="{H}" rx="18"/></clipPath>
<clipPath id="sunClip"><rect x="0" y="0" width="{W}" height="215"/></clipPath>
<mask id="nameMask"><text x="70" y="150" font-family="{FONT}" font-size="76" font-weight="800" fill="#fff">Shakhzod Miraliev</text></mask>
</defs>
<style>{css}</style>
<g clip-path="url(#clip)">
<rect width="{W}" height="{H}" fill="url(#sky)"/>
{stars}
<g clip-path="url(#sunClip)"><circle cx="930" cy="190" r="150" fill="{PINK}" filter="url(#blur)" style="animation:glow 6s ease-in-out infinite"/>
<g style="animation:sun 7s ease-in-out infinite"><circle cx="930" cy="190" r="112" fill="url(#sunG)"/>{bands}</g></g>
<rect x="0" y="215" width="{W}" height="105" fill="#150f2e"/>
{grid}{hl}
<line x1="0" x2="{W}" y1="215" y2="215" stroke="{PINK}" stroke-width="2" opacity=".9"/>
<g class="name"><text x="70" y="150" font-family="{FONT}" font-size="76" font-weight="800" fill="url(#txt)">Shakhzod Miraliev</text>
<g mask="url(#nameMask)"><rect x="0" y="80" width="260" height="90" fill="url(#sh)" style="animation:sheen 5s ease-in-out 1.6s infinite"/></g></g>
<g class="sub"><text x="74" y="196" font-family="{FONT}" font-size="26" font-weight="600" fill="{PURPLE}">UI/UX Designer × Developer</text>
<path d="M74 212 H470" stroke="{PINK}" stroke-width="3" stroke-linecap="round" pathLength="1" stroke-dasharray="1" style="animation:draw 1.6s ease-out 1s both"/></g>
<g class="jp"><text x="76" y="262" font-family="{FONT}" font-size="20" fill="#e6e1ff" opacity=".9">一歩ずつ · one step at a time</text></g>
{petals}
</g></svg>"""
    for k, v in dict(W=W, H=H, PINK=PINK, INDIGO=INDIGO, PURPLE=PURPLE, FONT=FONT, css=css, stars=stars, bands=bands, grid=grid, hl=hl, petals="".join(petals)).items():
        svg = svg.replace("{%s}" % k, str(v))
    write("hero.svg", svg)


def divider():
    css = "@keyframes run{0%{transform:translateX(-300px)}100%{transform:translateX(1200px)}}" + FREEZE
    svg = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 14" width="1200" height="14">
<defs><linearGradient id="l" x1="0" x2="1"><stop offset="0" stop-color="{INDIGO}" stop-opacity="0"/><stop offset=".3" stop-color="{INDIGO}"/><stop offset=".7" stop-color="{PINK}"/><stop offset="1" stop-color="{PINK}" stop-opacity="0"/></linearGradient>
<linearGradient id="g" x1="0" x2="1"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".5" stop-color="#fff"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient></defs>
<style>{css}</style>
<rect x="0" y="6" width="1200" height="2" rx="1" fill="url(#l)"/>
<rect x="0" y="5" width="300" height="4" rx="2" fill="url(#g)" style="animation:run 4.5s ease-in-out infinite"/>
</svg>"""
    write("divider.svg", svg.replace("{INDIGO}", INDIGO).replace("{PINK}", PINK).replace("{css}", css))


def dashboard():
    days = contributions()
    langs, repo_count = languages()
    total = sum(n for _, n in days)
    cur, best = streaks(days)
    W, H = 1200, 560
    css = """
    @keyframes up{0%{opacity:0;transform:translateY(22px)}100%{opacity:1;transform:translateY(0)}}
    @keyframes draw{0%{stroke-dashoffset:1}100%{stroke-dashoffset:0}}
    @keyframes fade{0%{opacity:0}100%{opacity:1}}
    @keyframes grow{0%{transform:scaleX(0)}100%{transform:scaleX(1)}}
    @keyframes growY{0%{transform:scaleY(0)}100%{transform:scaleY(1)}}
    @keyframes ring{0%{stroke-dasharray:0 1000}100%{stroke-dasharray:1000 0}}
    @keyframes pulse{0%{r:5px;opacity:.9}100%{r:22px;opacity:0}}
    @keyframes sweep{0%{transform:translateX(-400px)}45%,100%{transform:translateX(1300px)}}
    @keyframes spin{100%{transform:rotate(360deg)}}
    @keyframes flick{0%,100%{transform:scale(1)}50%{transform:scale(1.14)}}
    .card{animation:up .8s cubic-bezier(.2,.8,.2,1) both}
    .bar{transform-box:fill-box;transform-origin:left center;animation:grow 1.2s cubic-bezier(.2,.8,.2,1) both}
    .col{transform-box:fill-box;transform-origin:center bottom;animation:growY .9s cubic-bezier(.2,.8,.2,1) both}
    """ + FREEZE
    o = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d" role="img" aria-label="GitHub stats of %s">' % (W, H, W, H, USER),
         '<defs><linearGradient id="area" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="%s" stop-opacity=".55"/><stop offset="1" stop-color="%s" stop-opacity="0"/></linearGradient>' % (PURPLE, INDIGO),
         '<linearGradient id="line" x1="0" x2="1"><stop offset="0" stop-color="%s"/><stop offset=".6" stop-color="%s"/><stop offset="1" stop-color="%s"/></linearGradient>' % (INDIGO, PURPLE, PINK),
         '<linearGradient id="sw" x1="0" x2="1"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".5" stop-color="#fff" stop-opacity=".07"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>',
         '<clipPath id="all"><rect width="%d" height="%d" rx="16"/></clipPath><mask id="donut"><circle cx="1000" cy="300" r="78" fill="none" stroke="#fff" stroke-width="30" transform="rotate(-90 1000 300)" style="animation:ring 1.8s ease-out .9s both"/></mask></defs>' % (W, H),
         "<style>%s</style>" % css]
    tiles = [("CONTRIBUTIONS · 12 MONTHS", "{:,}".format(total), PURPLE), ("CURRENT STREAK", "%d days" % cur, PINK), ("LONGEST STREAK", "%d days" % best, CYAN), ("PUBLIC REPOS", str(repo_count), GREEN)]
    for i, (label, value, col) in enumerate(tiles):
        x = i * 305
        o.append('<g class="card" style="animation-delay:%.2fs"><rect x="%d" y="0" width="285" height="120" rx="16" fill="%s"/>' % (i * 0.12, x, CARD)
                 + '<rect x="%d" y="0" width="285" height="120" rx="16" fill="none" stroke="%s" stroke-opacity=".35"/>' % (x, col)
                 + '<text x="%d" y="38" font-family="%s" font-size="13" font-weight="700" letter-spacing="1.5" fill="%s">%s</text>' % (x + 24, FONT, MUTED, label)
                 + '<text x="%d" y="88" font-family="%s" font-size="42" font-weight="800" fill="%s">%s</text>' % (x + 24, FONT, col, value)
                 + '<rect class="bar" x="%d" y="100" width="237" height="3" rx="1.5" fill="%s" opacity=".7" style="animation-delay:%.2fs"/></g>' % (x + 24, col, 0.5 + i * 0.12))
    o.append('<g class="card" style="animation-delay:.12s"><path d="M552 30 c-10 12 -18 20 -18 32 a18 18 0 0 0 36 0 c0 -8 -4 -13 -8 -18 c-1 6 -4 9 -7 10 c2 -9 1 -17 -3 -24z" fill="%s" opacity=".9" style="transform-box:fill-box;transform-origin:center bottom;animation:flick 1.1s ease-in-out infinite"/></g>' % PINK)
    weeks = [sum(n for _, n in days[i:i + 7]) for i in range(0, len(days), 7)]
    peak = max(weeks) or 1
    x0, x1, yb, yt = 40, 740, 500, 215
    pts = [(x0 + (x1 - x0) * i / (len(weeks) - 1), yb - (yb - yt) * w / peak) for i, w in enumerate(weeks)]
    d = "M%.1f %.1f" % pts[0]
    for a, b in zip(pts[1:], pts[2:]):
        d += " Q%.1f %.1f %.1f %.1f" % (a[0], a[1], (a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
    d += " L%.1f %.1f" % pts[-1]
    o.append('<g class="card" style="animation-delay:.3s"><rect x="0" y="140" width="780" height="420" rx="16" fill="%s"/>' % CARD
             + '<text x="28" y="180" font-family="%s" font-size="20" font-weight="700" fill="%s">Contributions</text>' % (FONT, TEXT)
             + '<text x="752" y="180" text-anchor="end" font-family="%s" font-size="14" fill="%s">weekly · last 12 months</text>' % (FONT, MUTED))
    for k in range(4):
        y = yb - (yb - yt) * k / 3
        o.append('<line x1="%d" x2="%d" y1="%.0f" y2="%.0f" stroke="#fff" stroke-opacity=".06"/><text x="%d" y="%.0f" font-family="%s" font-size="11" fill="%s">%d</text>' % (x0, x1, y, y, x1 + 8, y + 4, FONT, MUTED, round(peak * k / 3)))
    seen = None
    for i in range(0, len(days), 7):
        m = days[i][0][:7]
        if m != seen and seen is not None and int(m[5:]) % 2 == 1:
            x = x0 + (x1 - x0) * (i // 7) / (len(weeks) - 1)
            o.append('<text x="%.0f" y="532" text-anchor="middle" font-family="%s" font-size="12" fill="%s">%s</text>' % (x, FONT, MUTED, dt.date(int(m[:4]), int(m[5:]), 1).strftime("%b")))
        seen = m
    for i, (px, py) in enumerate(pts):
        o.append('<rect class="col" x="%.1f" y="%.1f" width="6" height="%.1f" rx="3" fill="%s" opacity=".28" style="animation-delay:%.2fs"/>' % (px - 3, py, max(yb - py, 0), INDIGO, 0.6 + i * 0.02))
    o.append('<path d="%s L%d %d L%d %d Z" fill="url(#area)" style="animation:fade 1.2s ease-out 2.2s both"/>' % (d, x1, yb, x0, yb)
             + '<path d="%s" fill="none" stroke="url(#line)" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round" pathLength="1" stroke-dasharray="1" style="animation:draw 2.4s ease-in-out .8s both"/>' % d
             + '<g style="animation:fade .4s ease-out 3.1s both"><circle cx="%.1f" cy="%.1f" r="5" fill="%s" style="animation:pulse 1.8s ease-out infinite"/><circle cx="%.1f" cy="%.1f" r="5" fill="%s"/></g></g>' % (pts[-1][0], pts[-1][1], PINK, pts[-1][0], pts[-1][1], PINK))
    top = langs[:5]
    tot = sum(n for _, n in top) or 1
    cols = [PINK, YELLOW, CYAN, PURPLE, GREEN]
    R = 78
    C = 2 * 3.14159265 * R
    o.append('<g class="card" style="animation-delay:.42s"><rect x="800" y="140" width="400" height="420" rx="16" fill="%s"/>' % CARD
             + '<text x="828" y="180" font-family="%s" font-size="20" font-weight="700" fill="%s">Languages</text>' % (FONT, TEXT)
             + '<circle cx="1000" cy="300" r="%d" fill="none" stroke="#fff" stroke-opacity=".05" stroke-width="30"/><g mask="url(#donut)">' % R)
    acc = 0
    for (lang, n), col in zip(top, cols):
        ln = C * n / tot
        seg = max(ln - 3, 0.5)
        o.append('<circle cx="1000" cy="300" r="%d" fill="none" stroke="%s" stroke-width="30" stroke-dasharray="%.1f %.1f" stroke-dashoffset="%.1f" transform="rotate(-90 1000 300)"/>' % (R, col, seg, C - seg, -acc))
        acc += ln
    o.append('</g><circle cx="1000" cy="300" r="102" fill="none" stroke="%s" stroke-opacity=".5" stroke-width="1.5" stroke-dasharray="4 10" style="transform-box:fill-box;transform-origin:center;animation:spin 24s linear infinite"/>' % PURPLE
             + '<text x="1000" y="298" text-anchor="middle" font-family="%s" font-size="28" font-weight="800" fill="%s">%d</text><text x="1000" y="318" text-anchor="middle" font-family="%s" font-size="12" fill="%s">languages</text>' % (FONT, TEXT, len(langs), FONT, MUTED))
    for i, ((lang, n), col) in enumerate(zip(top, cols)):
        y = 428 + i * 26
        pct = 100.0 * n / tot
        o.append('<circle cx="834" cy="%d" r="5" fill="%s"/><text x="848" y="%d" font-family="%s" font-size="14" fill="%s">%s</text>' % (y - 5, col, y, FONT, TEXT, lang)
                 + '<rect x="960" y="%d" width="160" height="8" rx="4" fill="#fff" fill-opacity=".06"/><rect class="bar" x="960" y="%d" width="%.1f" height="8" rx="4" fill="%s" style="animation-delay:%.2fs"/>' % (y - 10, y - 10, max(160 * pct / 100, 4), col, 1.2 + i * 0.15)
                 + '<text x="1172" y="%d" text-anchor="end" font-family="%s" font-size="13" fill="%s">%.0f%%</text>' % (y, FONT, MUTED, pct))
    o.append('</g><g clip-path="url(#all)"><rect x="0" y="0" width="400" height="%d" fill="url(#sw)" style="animation:sweep 7s ease-in-out 3s infinite"/></g></svg>' % H)
    write("dashboard.svg", "\n".join(o))
    print("total=%d streak=%d/%d repos=%d langs=%s" % (total, cur, best, repo_count, [l for l, _ in top]))


hero()
divider()
dashboard()
