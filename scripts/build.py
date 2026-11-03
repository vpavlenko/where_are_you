"""Build the responsive HTML reader from the recovered, source-faithful content."""
from pathlib import Path
import json, html, shutil
from PIL import Image
R=Path(__file__).resolve().parents[1];out=R/'dist'
records=json.loads((R/'story-source.json').read_text())
esc=html.escape

def art(n,cover=False):
    # The cover repeats page 4's artwork. Use its complete, type-free illustration.
    source=4 if cover else n
    path=out/f'assets/page-{source:02}.webp'
    if not path.exists():return ''
    w,h=Image.open(path).size
    loading='fetchpriority="high"' if cover else 'loading="lazy"'
    return f'<figure class="art art-{n}"><img src="assets/page-{source:02}.webp" width="{w}" height="{h}" alt="" {loading} decoding="async"></figure>'

parts=[]
for r in records:
    n=r['page']
    start=f'<section class="story-page{ " cover" if n==1 else ""}{ " back-cover" if n==16 else ""}" id="page-{n}" aria-label="{n}" data-page="{n}"><a class="page-number" href="#page-{n}">{n:02}</a>'
    if n==1:
        parts.append(start+'<div class="cover-title"><h1 lang="en">Where are you?</h1><p lang="ts" class="subtitle">U kwihi?</p></div>'+art(n,True)+'<div class="credits"><span>Ann Walton</span><span>Rico</span><span>Tsakani Nkwe</span></div></section>')
        continue
    # The lettering on page 12 is already retained inside its illustration.
    blocks=[] if n==12 else r['blocks']
    text=''
    for lang in ['en','ts']:
        paras=[b for b in blocks if b['lang']==lang]
        if not paras:continue
        text+=f'<div lang="{lang}" class="story-text">'+''.join('<p>'+esc(b['text'])+'</p>' for b in paras)+'</div>'
    picture=art(n) if r['art_bbox'] else ''
    # Keep all original pages separate and sequential, with flowing text.
    content=picture+text if n in [3,10,16] else text+picture
    parts.append(start+content+'</section>')
options=''.join(f'<option value="{n}">{n:02} / 16</option>' for n in range(1,17))
page='''<!doctype html>
<html lang="en" data-language="both">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="theme-color" content="#263e51">
<title>Where are you?</title>
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 40 40'%3E%3Ctext y='32' font-size='32'%3E📖%3C/text%3E%3C/svg%3E">
<link rel="stylesheet" href="styles.css">
<script src="reader.js" defer></script>
</head>
<body>
<header class="toolbar">
<a class="book-name" href="#page-1">Where are you?</a>
<div class="controls">
<label class="sr-only" for="language">Language</label>
<select id="language"><option value="both">English + Xitsonga</option><option value="en">English</option><option value="ts">Xitsonga</option></select>
<div class="text-size"><button type="button" id="smaller" aria-label="Smaller text">A−</button><button type="button" id="larger" aria-label="Larger text">A+</button></div>
<label class="sr-only" for="page-select">Page</label>
<select id="page-select">'''+options+'''</select>
</div>
<div class="progress" aria-hidden="true"><div id="progress-bar"></div></div>
</header>
<main>'''+''.join(parts)+'''</main>
<footer><img class="nalibali" src="assets/nalibali.webp" width="182" height="128" alt="Nal’ibali"><p>World Read Aloud Day 2019 • Siku ra Misava ra ku Hlayela Ehenhla 2019</p><div><a href="https://nalibali.org/">Nal’ibali</a><span aria-hidden="true">·</span><a href="source.pdf">PDF</a><span aria-hidden="true">·</span><a href="#page-1" aria-label="Back up">↑</a></div></footer>
</body></html>
'''
(out/'index.html').write_text(page)
shutil.copyfile(R/'unnamed-file-331.pdf',out/'source.pdf')
print('Built dist/index.html: 16 sequential sections, selectable HTML text, original artwork.')
