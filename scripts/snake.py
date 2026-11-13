import sys, io
F={'D':["1111.","1...1","1...1","1...1","1...1","1...1","1111."],
'E':["11111","1....","1....","1111.","1....","1....","11111"],
'S':[".1111","1....","1....",".111.","....1","....1","1111."],
'I':["11111","..1..","..1..","..1..","..1..","..1..","11111"],
'G':[".1111","1....","1....","1.111","1...1","1...1",".111."],
'N':["1...1","11..1","11..1","1.1.1","1..11","1..11","1...1"],
'R':["1111.","1...1","1...1","1111.","1.1..","1..1.","1...1"]}
WORD="DESIGNER"; COLS,ROWS=53,7; C,G=11,3; P=C+G
off=(COLS-(len(WORD)*6-1))//2
lit={}
for i,ch in enumerate(WORD):
    for r,row in enumerate(F[ch]):
        for c,v in enumerate(row):
            if v=='1': lit[(off+i*6+c,r)]=(i*7+r*3+c*5)%4
import random
rnd=random.Random(23)
cur=(0,3); path=[cur]; left=set(lit)
while left:
    near=sorted(left,key=lambda p:abs(p[0]-cur[0])+abs(p[1]-cur[1]))[:5]
    tgt=rnd.choice(near)
    while cur!=tgt:
        dx=(tgt[0]>cur[0])-(tgt[0]<cur[0]); dy=(tgt[1]>cur[1])-(tgt[1]<cur[1])
        if dx and (not dy or rnd.random()<0.5): cur=(cur[0]+dx,cur[1])
        else: cur=(cur[0],cur[1]+dy)
        path.append(cur); left.discard(cur)
for _ in range(6):
    cur=(min(cur[0]+1,COLS-1),cur[1]); path.append(cur)
N=len(path); STEP=0.075; PAUSE=4; D=N*STEP+PAUSE; LEN=5
def build(dark):
    empty='#161b22' if dark else '#ebedf0'
    greens=['#1f8a3b','#26a641','#2fc24e','#39d353'] if dark else ['#40c463','#30a14e','#2a8f45','#216e39']
    snake=['#c084fc','#a855f7','#9333ea','#7e22ce','#6b21a8']
    W=COLS*P+G+20; H=ROWS*P+G+20
    o=[f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">']
    idx={}
    for i,p in enumerate(path): idx.setdefault(p,i)
    for c in range(COLS):
        for r in range(ROWS):
            x,y=10+G+c*P,10+G+r*P
            if (c,r) in lit:
                g=greens[lit[(c,r)]]; t=(idx[(c,r)]*STEP)/D; t2=min(t+0.004,0.985)
                o.append(f'<rect x="{x}" y="{y}" width="{C}" height="{C}" rx="2" fill="{g}"><animate attributeName="fill" dur="{D:.2f}s" repeatCount="indefinite" calcMode="discrete" values="{g};{empty};{g}" keyTimes="0;{t2:.4f};0.99"/></rect>')
            else:
                o.append(f'<rect x="{x}" y="{y}" width="{C}" height="{C}" rx="2" fill="{empty}"/>')
    for k in range(LEN-1,-1,-1):
        xs=[];ys=[]
        for i in range(N+1):
            j=min(max(i-k,0),N-1); c,r=path[j]
            xs.append(str(10+G+c*P - (1 if k==0 else 0))); ys.append(str(10+G+r*P - (1 if k==0 else 0)))
        kt=";".join(f"{min(i*STEP/D,1):.4f}" for i in range(N+1))+";1"
        xs.append(xs[-1]); ys.append(ys[-1])
        s=C+2 if k==0 else C-k
        op=f'<animate attributeName="opacity" dur="{D:.2f}s" repeatCount="indefinite" values="1;1;0;0" keyTimes="0;{N*STEP/D:.4f};{(N*STEP+0.4)/D:.4f};1"/>'
        o.append(f'<rect width="{s}" height="{s}" rx="3" fill="{snake[k]}" x="{xs[0]}" y="{ys[0]}"><animate attributeName="x" dur="{D:.2f}s" repeatCount="indefinite" values="{";".join(xs)}" keyTimes="{kt}"/><animate attributeName="y" dur="{D:.2f}s" repeatCount="indefinite" values="{";".join(ys)}" keyTimes="{kt}"/>{op}</rect>')
    o.append('</svg>'); return "\n".join(o)
out=sys.argv[1]
io.open(out+'/designer-snake-dark.svg','w',encoding='utf-8',newline='\n').write(build(True))
io.open(out+'/designer-snake.svg','w',encoding='utf-8',newline='\n').write(build(False))
print(len(lit),'lit cells', N,'steps', round(D,1),'s')
