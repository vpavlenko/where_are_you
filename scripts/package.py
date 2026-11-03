from pathlib import Path
import base64, re, zipfile
R=Path(__file__).resolve().parents[1];D=R/'dist'
page=(D/'index.html').read_text()
page=page.replace('<link rel="stylesheet" href="styles.css">','<style>\n'+(D/'styles.css').read_text()+'\n</style>')
page=page.replace('<script src="reader.js" defer></script>','<script>document.addEventListener("DOMContentLoaded", () => {\n'+(D/'reader.js').read_text()+'\n});</script>')
def inline(m):return 'src="data:image/webp;base64,'+base64.b64encode((D/m[1]).read_bytes()).decode()+'"'
page=re.sub(r'src="(assets/[^"\s]+\.webp)"',inline,page)
page=page.replace('href="source.pdf"','href="unnamed-file-331.pdf"')
(R/'where-are-you.html').write_text(page)
with zipfile.ZipFile(R/'where-are-you.zip','w',zipfile.ZIP_DEFLATED) as archive:
    for p in sorted(D.rglob('*')):
        if p.is_file():archive.write(p,p.relative_to(D))
print('Created where-are-you.html and where-are-you.zip')
