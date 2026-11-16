"""Standalone profile artwork. Run: python scripts/profile_art.py."""
from html import escape
from pathlib import Path
OUT = Path(__file__).resolve().parents[1] / "assets"
INK, PANEL, LINE = "#090D1B", "#101728", "#253149"
WHITE, MUTED, CYAN, LILAC, CORAL = "#F1F4FF", "#9CAAC3", "#66E3ED", "#B8A2FF", "#FF879D"
FONT = "'Segoe UI','Noto Sans',Arial,sans-serif"
MONO = "'Cascadia Code','JetBrains Mono','DejaVu Sans Mono',monospace"

def text(x,y,value,size=22,color=WHITE,weight=400,mono=False,extra=""):
    return (f'<text x="{x}" y="{y}" font-family="{MONO if mono else FONT}" '
            f'font-size="{size}" font-weight="{weight}" fill="{color}" {extra}>'
            f'{escape(str(value))}</text>')

def rect(x,y,w,h,fill=PANEL,radius=16,stroke=LINE):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{radius}" fill="{fill}" stroke="{stroke}"/>'

def star(x,y,color=CYAN,size=16):
    return (f'<path d="M{x} {y-size} Q{x+2} {y-2} {x+size} {y} '
            f'Q{x+2} {y+2} {x} {y+size} Q{x-2} {y+2} {x-size} {y} '
            f'Q{x-2} {y-2} {x} {y-size}Z" fill="{color}"/>')

def chip(x,y,label,color=CYAN,width=None):
    w=width or 28+len(label)*11
    return rect(x,y,w,36,INK,8,LINE)+text(x+14,y+24,label,17,color,500,True)

def save(name,w,h,label,body,accent=CYAN):
    svg=(f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
         f'viewBox="0 0 {w} {h}" role="img" aria-label="{escape(label,quote=True)}">'
         f'<title>{escape(label)}</title><defs>'
         f'<linearGradient id="wash" x1="0" y1="0" x2="1" y2="1">'
         f'<stop stop-color="{PANEL}"/><stop offset="1" stop-color="{INK}"/></linearGradient>'
         f'<radialGradient id="halo"><stop stop-color="{accent}" stop-opacity=".14"/>'
         '<stop offset="1" stop-color="#090D1B" stop-opacity="0"/></radialGradient>'
         f'<clipPath id="frame"><rect width="{w}" height="{h}" rx="20"/></clipPath></defs>'
         '<style>@keyframes breathe{50%{opacity:.45}}'
         '@keyframes trace{to{stroke-dashoffset:-96}}'
         '.pulse{animation:breathe 4s ease-in-out infinite}'
         '.trace{animation:trace 12s linear infinite}'
         '@media(prefers-reduced-motion:reduce){*{animation:none!important}}</style>'
         f'<g clip-path="url(#frame)">{rect(.5,.5,w-1,h-1,"url(#wash)",20,LINE)}'
         +body+'</g></svg>\n')
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/name).write_text(svg,encoding="utf-8")

def signal():
    b=text(28,45,"CREATIVE SYSTEM",17,MUTED,600,True)
    for i,(label,c) in enumerate([("01 THINK",MUTED),("02 DESIGN",LILAC),("03 BUILD",CYAN),("04 SHIP",CORAL)]):
        x=330+i*210
        b+=text(x,45,label,18,c,600,True)
        if i<3: b+=f'<path d="M{x+134} 39 h35 m-6 -5 6 5 -6 5" fill="none" stroke="{LINE}" stroke-width="2"/>'
    b+=f'<circle cx="1160" cy="38" r="5" fill="{CYAN}" class="pulse"/>'
    save("signal.svg",1200,76,"Creative process: think, design, build, ship",b)

def identity():
    b=text(36,45,"01 / CHARACTER FILE",16,CYAN,600,True)
    b+=text(36,104,"Design it. Build it. Ship it.",40,WHITE,700)
    b+=text(36,145,"Shakhzod Miraliev · 이로운",23,MUTED)
    b+=text(36,202,"BASED IN",14,MUTED,500,True)
    b+=text(36,234,"South Korea  ←  Uzbekistan",23,WHITE,500)
    b+=f'<path d="M644 34 V262" stroke="{LINE}"/>'
    for x,y,s,size,c,weight,mono in [
        (680,45,"CURRENT GUILD",14,MUTED,500,True),
        (680,89,"AI G-Payments",32,WHITE,650,False),
        (680,123,"대리 · 개발팀 / Assistant Manager",21,CYAN,400,False),
        (680,178,"EDUCATION",14,MUTED,500,True),
        (680,211,"Inha University Graduate School",22,WHITE,500,False),
        (680,244,"Convergence Design",20,MUTED,400,False)]:
        b+=text(x,y,s,size,c,weight,mono)
    b+=f'<path d="M36 270 H1164" stroke="{LINE}"/>'
    for x,label,c in [(36,"UZBEK · NATIVE",CYAN),(310,"RUSSIAN · NATIVE",LILAC),(606,"ENGLISH · BUSINESS",CORAL),(922,"KOREAN · TOPIK 4",CYAN)]:
        b+=text(x,311,label,16,c,500,True)
    save("character.svg",1200,340,"Shakhzod Miraliev (이로운). UI/UX designer and developer in South Korea, from Uzbekistan. Assistant Manager in the development team at AI G-Payments. Inha University Graduate School, Convergence Design. Uzbek and Russian native; business English; Korean TOPIK 4.",b)

def mission(kind,number,title,subtitle,tags,accent):
    b=f'<ellipse cx="970" cy="170" rx="340" ry="280" fill="url(#halo)"/><path d="M660 1 604 349" stroke="{LINE}"/>'
    b+=text(36,45,f"MISSION / {number}",16,accent,600,True)
    # Long names receive two lines so the illustration always has its own space.
    if kind=="madie":
        b+=text(36,120,"Korean with",56,WHITE,750)+text(36,183,"Madie",56,WHITE,750)
        for i,line in enumerate(subtitle): b+=text(39,222+i*27,line,21,MUTED)
    else:
        b+=text(36,136,title,72 if len(title)<10 else 62,WHITE,750)
        for i,line in enumerate(subtitle): b+=text(39,182+i*32,line,25,MUTED)
    x=36
    for tag in tags:
        b+=chip(x,283,tag,accent)
        x+=len(tag)*11+40
    b+=text(1158,45,{"odim":"HEALTH TECH","madie":"ED TECH","glow":"GAME DEV","city":"CIVIC TECH"}[kind],14,accent,500,True,'text-anchor="end"')
    if kind=="odim":
        b+=f'<circle cx="931" cy="183" r="110" fill="none" stroke="{LINE}"/><circle cx="931" cy="183" r="136" fill="none" stroke="{LINE}" stroke-dasharray="2 12"/>'
        b+=f'<path d="M732 200 H816 L844 156 882 220 917 174 H1134" fill="none" stroke="{accent}" stroke-width="4" stroke-linecap="round"/>'
        for x,y,label in [(761,200,"PATIENT"),(936,174,"SPECIALIST"),(1107,174,"DOCTOR")]:
            b+=f'<circle cx="{x}" cy="{y}" r="25" fill="{INK}" stroke="{accent}" stroke-width="2"/>'
            b+=f'<circle cx="{x}" cy="{y-5}" r="6" fill="none" stroke="{WHITE}" stroke-width="2"/><path d="M{x-10} {y+11} q10 -14 20 0" fill="none" stroke="{WHITE}" stroke-width="2"/>'
            b+=text(x,y+53,label,12,MUTED,500,True,'text-anchor="middle"')
        b+=star(1044,90,accent,13)
    elif kind=="madie":
        b+=f'<ellipse cx="944" cy="176" rx="188" ry="106" fill="none" stroke="{LINE}" transform="rotate(-23 944 176)"/>'
        b+='<g transform="rotate(-9 933 173)">'+rect(848,83,180,180,"#242039",22,"#685D91")+text(938,210,"한",112,WHITE,700,extra='text-anchor="middle"')+'</g>'
        for x,y,ch,c,rot in [(767,99,"가",CYAN,-15),(1058,166,"나",CORAL,12),(804,241,"다",LILAC,9)]:
            b+=f'<g transform="rotate({rot} {x+34} {y+34})">'+rect(x,y,68,68,INK,14,LINE)+text(x+34,y+48,ch,38,c,600,extra='text-anchor="middle"')+'</g>'
        b+=star(1060,88,accent,17)+star(1032,285,CYAN,10)
    elif kind=="glow":
        b+=f'<circle cx="950" cy="178" r="128" fill="none" stroke="{LINE}"/><circle cx="950" cy="178" r="147" fill="none" stroke="{LINE}" stroke-dasharray="2 12"/>'
        colors=[LILAC,CYAN,CORAL,"#F7D38B"]
        b+='<g transform="rotate(-10 955 179)">'
        for row in range(4):
            for col in range(5):
                x,y=796+col*59,64+row*59
                c=colors[(row*3+col*2+row//2)%4]
                b+=rect(x,y,49,49,c,12,c)
                if (row+col)%3==0:
                    b+=f'<path d="M{x+26} {y+14} v22 m0 -22 9 -2 v18" fill="none" stroke="{INK}" stroke-width="2.5"/><ellipse cx="{x+21}" cy="{y+35}" rx="6" ry="4" fill="{INK}"/>'
                else: b+=star(x+25,y+25,INK,11)
        b+='</g>'+star(1132,112,CYAN,16)+star(759,247,CORAL,11)
    else:
        b+='<g transform="translate(770 69) scale(.88)">'
        b+=f'<path d="M0 174 176 73 389 176 212 278Z" fill="#111F33" stroke="{LINE}"/>'
        for x,y,w,h in [(39,126,46,71),(116,94,48,114),(206,120,55,84),(288,157,35,48)]:
            b+=f'<path d="M{x} {y} v-{h} l{w} -26 v{h}Z" fill="#1B3350" stroke="#365474"/>'
            b+=f'<path d="M{x+w} {y-26} v-{h} l24 14 v{h}Z" fill="#14283E" stroke="#365474"/>'
            b+=f'<path d="M{x} {y-h} l{w} -26 24 14 -{w} 26Z" fill="#2F506C" stroke="#456783"/>'
            for k in range(min(3,max(1,h//22))):
                b+=f'<path d="M{x+10} {y-h+13+k*16} l{w-18} -16" stroke="{accent}" stroke-opacity=".65" stroke-width="2"/>'
        b+=f'<path d="M34 185 115 232 287 133 M115 232 215 176 335 236" fill="none" stroke="{accent}" stroke-width="3"/>'
        for x,y in [(34,185),(115,232),(287,133),(335,236)]: b+=f'<circle cx="{x}" cy="{y}" r="5" fill="{accent}"/>'
        b+='</g>'+star(1101,89,accent,14)
    save(f"mission-{kind}.svg",1200,350,f"{title}: {' '.join(subtitle)}. {' · '.join(tags)}.",b,accent)

def toolkit():
    b=text(36,45,"03 / LOADOUT",16,CYAN,600,True)+text(36,100,"Design arsenal",30,WHITE,650)+text(542,100,"Build arsenal",30,WHITE,650)
    b+=f'<path d="M506 78 V260" stroke="{LINE}"/>'
    for x,y,label in [(36,129,"Figma"),(151,129,"Illustrator"),(36,178,"Photoshop"),(197,178,"After Effects"),(36,227,"Blender")]: b+=chip(x,y,label,LILAC)
    for x,y,label in [(542,129,"TypeScript"),(702,129,"React"),(807,129,"Next.js"),(934,129,"Tailwind"),(542,178,"Node.js"),(669,178,"Supabase"),(807,178,"Firebase"),(945,178,"Cloudflare"),(542,227,"Lua / Defold"),(724,227,"Python"),(840,227,"C++"),(923,227,"Android Studio")]: b+=chip(x,y,label,CYAN)
    save("toolkit.svg",1200,296,"Design: Figma, Illustrator, Photoshop, After Effects, Blender. Code: TypeScript, React, Next.js, Tailwind, Node.js, Supabase, Firebase, Cloudflare, Lua, Defold, Python, C++, Android Studio.",b)

def footer():
    b=f'<ellipse cx="1052" cy="145" rx="350" ry="220" fill="url(#halo)"/>'
    b+=text(36,45,"THE STORY CONTINUES",15,CYAN,600,True)+text(36,113,"One step at a time.",54,WHITE,700)
    b+=text(39,158,"一歩ずつ  /  From the first sketch to the final build.",22,MUTED)
    b+=f'<path d="M38 204 H1160" stroke="{LINE}"/><path d="M38 204 H1160" stroke="{CYAN}" stroke-width="2" stroke-dasharray="8 88" class="trace"/>'
    b+=star(1088,100,CYAN,29)+star(1026,147,LILAC,13)
    save("endcard.svg",1200,240,"One step at a time. 一歩ずつ. From the first sketch to the final build.",b)

def links():
    for name,label,color in [("portfolio","BEHANCE PORTFOLIO",LILAC),("madie","KOREAN WITH MADIE",CYAN),("company","AI G-PAYMENTS",CORAL)]:
        b=text(22,37,label,17,color,600,True)
        b+=f'<path d="M260 39 273 26 M261 26 h12 v12" fill="none" stroke="{color}" stroke-width="2"/>'
        save(f"link-{name}.svg",300,62,label,b,color)

def main():
    signal()
    identity()
    mission("odim","01","ODIM",["Recovery, connected.","One flow. Three perspectives."],["REHABILITATION","WEB + ANDROID"],CYAN)
    mission("madie","02","Korean with Madie",["A new language.","A world of possibilities."],["99 LESSONS","AI TUTOR"],LILAC)
    mission("glow","03","GLOW",["Match the notes.","Bring the city back to life."],["MUSICAL MATCH-3","DEFOLD + LUA"],CORAL)
    mission("city","04","SMART CITY",["A city of information.","One connected interface."],["MASTER’S THESIS","4 LANGUAGES"],CYAN)
    toolkit()
    footer()
    links()
    print("Generated 11 standalone SVG assets")

if __name__=="__main__":
    main()
