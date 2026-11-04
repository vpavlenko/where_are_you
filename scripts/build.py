"""Build aligned source-language columns and the optimal letter introduction schedule."""
from pathlib import Path
from collections import Counter
import json, html, shutil
import struct
def image_size(path):
    data=path.read_bytes()
    if data[12:16]==b'VP8X':return 1+int.from_bytes(data[24:27],'little'),1+int.from_bytes(data[27:30],'little')
    if data[12:16]==b'VP8 ' :return tuple(v & 0x3fff for v in struct.unpack('<HH',data[26:30]))
    if data[12:16]==b'VP8L':
        bits=int.from_bytes(data[21:25],'little');return (bits&0x3fff)+1,((bits>>14)&0x3fff)+1
    raise ValueError(path)
R=Path(__file__).resolve().parents[1]; out=R/'dist'; esc=html.escape
records=json.loads((R/'story-source.json').read_text())
mapping=dict(zip('abcdefghijklmnopqrstuvwxyz', ['а','б','ч','д','е','ф','г','х','и','дж','к','л','м','н','о','п','к','р','с','т','у','в','в','ш','й','з']))
body=[r for r in records if 2<=r['page']<=14 and r['page']!=12]
english=[(r['page'],b['text']) for r in body for b in r['blocks'] if b['lang']=='en']
tsonga=[(r['page'],b['text']) for r in body for b in r['blocks'] if b['lang']=='ts']
assert len(english)==len(tsonga)==34
pairs={n:[] for n in range(1,17)}
for i,((ep,en),(tp,ts)) in enumerate(zip(english,tsonga),1):
    pairs[tp].append((i,en,ts))
# One new target per paragraph. Maximum-weight assignment optimizes total source
# characters converted throughout all 34 paragraphs. Each introduction must occur
# in that paragraph; no pedagogical optimality claim.
counts=[Counter(mapping[c] for c in t.lower() if c in mapping) for _,t in tsonga]
targets=sorted(set().union(*(c.keys() for c in counts)))
n=len(targets)
weights=[[sum(c[t] for c in counts[slot:]) for t in targets] for slot in range(n)]
def assignment(cost):
    n=len(cost);u=[0]*(n+1);v=[0]*(n+1);p=[0]*(n+1);way=[0]*(n+1)
    for i in range(1,n+1):
        p[0]=i;j0=0;mins=[float('inf')]*(n+1);used=[False]*(n+1)
        while True:
            used[j0]=True;i0=p[j0];delta=float('inf');j1=0
            for j in range(1,n+1):
                if not used[j]:
                    cur=cost[i0-1][j-1]-u[i0]-v[j]
                    if cur<mins[j]:mins[j]=cur;way[j]=j0
                    if mins[j]<delta:delta=mins[j];j1=j
            for j in range(n+1):
                if used[j]:u[p[j]]+=delta;v[j]-=delta
                else:mins[j]-=delta
            j0=j1
            if p[j0]==0:break
        while True:
            j1=way[j0];p[j0]=p[j1];j0=j1
            if j0==0:break
    result=[0]*n
    for j in range(1,n+1):result[p[j]-1]=j-1
    return result
order=assignment([[-x if counts[i][targets[j]] else 10**9 for j,x in enumerate(row)] for i,row in enumerate(weights)])
assert all(counts[i][targets[t]] for i,t in enumerate(order)), 'Every introduced letter must occur in its introduction paragraph'
schedule='\n'.join(f'{i+1} {targets[t]}' for i,t in enumerate(order))
config={'mapping':mapping,'defaultSchedule':schedule,'paragraphCount':36}
def art(n,cover=False):
    source=4 if cover else n; path=out/f'assets/page-{source:02}.webp'
    if not path.exists():return ''
    w,h=image_size(path)
    loading='fetchpriority="high"' if cover else 'loading="lazy"'
    return f'<figure class="art art-{n}"><img src="assets/page-{source:02}.webp" width="{w}" height="{h}" alt="" {loading} decoding="async"></figure>'
def row(i,en,ts):
    return f'<div class="paragraph-pair" id="paragraph-{i}" data-paragraph="{i}"><p lang="en" class="story-text">{esc(en)}</p><div class="translation"><a class="paragraph-number" href="#paragraph-{i}" aria-label="Абзац {i}">{i:02}</a><p lang="ts" class="story-text tsonga" data-step="{i}">{esc(ts)}</p></div><div class="introduced"></div></div>'
parts=[]
for r in records:
    n=r['page']; start=f'<section class="story-page{ " cover" if n==1 else ""}{ " back-cover" if n==16 else ""}" id="page-{n}" data-page="{n}" aria-label="{n}"><a class="page-number" href="#page-{n}">{n:02} / 16</a>'
    if n==1:
        parts.append(start+'<div class="cover-title"><h1 lang="en">Where are you?</h1><p lang="ts" class="subtitle tsonga" data-step="1">U kwihi?</p></div>'+art(n,True)+'<div class="credits"><span>Ann Walton</span><span>Rico</span><span>Tsakani Nkwe</span></div></section>');continue
    rows=pairs[n]
    if n==16:
        en=[b['text'] for b in r['blocks'] if b['lang']=='en'];ts=[b['text'] for b in r['blocks'] if b['lang']=='ts']
        rows=[(35+i,e,t) for i,(e,t) in enumerate(zip(en,ts))]
    text=''.join(row(*p) for p in rows)
    picture=art(n) if r['art_bbox'] else ''
    parts.append(start+(picture+text if n in [3,10,16] else text+picture)+'</section>')
options=''.join(f'<option value="{n}">{n:02} / 16</option>' for n in range(1,17))
page='''<!doctype html>
<html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="theme-color" content="#263e51"><title>Where are you?</title><link rel="icon" href="data:,"><link rel="stylesheet" href="styles.css"><script src="reader.js" defer></script></head>
<body><header class="toolbar"><a class="book-name" href="#page-1">Where are you?</a><div class="controls"><span>12 pt</span><label for="page-select" class="sr-only">Страница</label><select id="page-select">'''+options+'''</select><a href="#letter-settings">Порядок букв</a></div><div class="progress" aria-hidden="true"><div id="progress-bar"></div></div></header>
<div class="reader-layout"><aside id="letter-settings"><label for="letter-order">Порядок букв</label><textarea id="letter-order" rows="12" spellcheck="false" autocapitalize="off" aria-describedby="schedule-example schedule-error">'''+schedule+'''</textarea><pre id="schedule-example">1 к т
3 а</pre><div class="settings-actions"><button id="auto-order" type="button">Автопорядок</button><label class="original-toggle"><input id="latin-only" type="checkbox"> Латиница</label></div><output id="schedule-error" role="status" aria-live="polite"></output><details class="mapping"><summary>Соответствия</summary><div id="mapping-list"></div><span>Приближённо</span></details></aside>
<main><div class="column-headings"><span>Оригинал · English</span><span>Перевод · Xitsonga</span></div>'''+''.join(parts)+'''</main></div>
<footer><img class="nalibali" src="assets/nalibali.webp" width="182" height="128" alt="Nal’ibali"><p>World Read Aloud Day 2019 • Siku ra Misava ra ku Hlayela Ehenhla 2019</p><div><a href="https://nalibali.org/">Nal’ibali</a><span aria-hidden="true">·</span><a href="source.pdf">PDF</a><span aria-hidden="true">·</span><a href="#page-1" aria-label="Наверх">↑</a></div></footer>
<script id="reader-config" type="application/json">'''+json.dumps(config,ensure_ascii=False).replace('<','\\u003c')+'''</script></body></html>'''
(out/'index.html').write_text(page)
shutil.copyfile(R/'unnamed-file-331.pdf',out/'source.pdf')
(R/'tmp'/'letter-order.json').write_text(json.dumps({'schedule':schedule,'converted':sum(weights[i][t] for i,t in enumerate(order)),'characters':sum(sum(c.values()) for c in counts)},ensure_ascii=False,indent=2))
print(f'Built 36 aligned paragraph pairs, {len(targets)} introduction stages.\n{schedule}')
