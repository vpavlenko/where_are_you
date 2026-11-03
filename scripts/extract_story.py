"""Recover booklet order, source text, and original artwork from the supplied PDF."""
from pathlib import Path
import json, re
import fitz
from PIL import Image, ImageDraw, ImageChops

ROOT=Path(__file__).resolve().parents[1]
doc=fitz.open(ROOT/'unnamed-file-331.pdf')
# PDF page, quadrant, upside down. The source uses a cut-and-fold imposition.
ORDER=[(5,'BR',False),(6,'BL',False),(11,'BR',False),(12,'BL',False),
       (12,'TL',True),(11,'TR',True),(6,'TL',True),(5,'TR',True),
       (5,'TL',True),(6,'TR',True),(11,'TL',True),(12,'TR',True),
       (12,'BR',False),(11,'BL',False),(6,'BR',False),(5,'BL',False)]
REGIONS={'TL':(47,44,405,581),'TR':(406,44,764,581),
         'BL':(47,582,405,1118),'BR':(406,582,764,1118)}

def clean(text):
    text=text.replace('ﬁ ', 'fi').replace('ﬂ ', 'fl')
    return re.sub(r'\s+', ' ', text.replace('ﬁ','fi').replace('ﬂ','fl')).strip()

def local_box(box,clip,rotate):
    x0,y0,x1,y1=box
    if rotate: return (clip.x1-x1,clip.y1-y1,clip.x1-x0,clip.y1-y0)
    return (x0-clip.x0,y0-clip.y0,x1-clip.x0,y1-clip.y0)

records=[]; previews=[]
for number,(pdf,quadrant,rotate) in enumerate(ORDER,1):
    p=doc[pdf-1]; clip=fitz.Rect(REGIONS[quadrant])
    pix=p.get_pixmap(matrix=fitz.Matrix(2,2),clip=clip,alpha=False)
    im=Image.frombytes('RGB',(pix.width,pix.height),pix.samples)
    if rotate: im=im.rotate(180)
    im.save(ROOT/f'tmp/pdfs/page-{number:02}.png')
    preview=im.copy(); preview.thumbnail((245,370)); previews.append(preview)
    blocks=[]
    for b in p.get_text('dict')['blocks']:
        if b['type']!=0: continue
        selected=[]
        for line in b['lines']:
            box=fitz.Rect(line['bbox']); cx=(box.x0+box.x1)/2;cy=(box.y0+box.y1)/2
            if not clip.contains(fitz.Point(cx,cy)): continue
            local=local_box(box,clip,rotate)
            if local[1]<10 or local[3]>clip.height-10: continue
            spans=line['spans']; text=clean(''.join(s['text'] for s in spans))
            if not text or re.fullmatch(r'\d+|T',text): continue
            selected.append((local,text,spans[0]['color']))
        if not selected:continue
        bounds=(min(x[0][0] for x in selected),min(x[0][1] for x in selected),max(x[0][2] for x in selected),max(x[0][3] for x in selected))
        blocks.append({'bbox':bounds,'text':clean(' '.join(x[1] for x in selected)),'lang':'ts' if selected[0][2]==22432 else 'en'})
    blocks.sort(key=lambda b:(b['bbox'][1],b['bbox'][0]))
    merged=[]
    for b in blocks:
        if merged and b['lang']==merged[-1]['lang'] and b['bbox'][1]-merged[-1]['bbox'][3]<5:
            prev=merged[-1];prev['text']+=' '+b['text'];prev['bbox']=(min(prev['bbox'][0],b['bbox'][0]),prev['bbox'][1],max(prev['bbox'][2],b['bbox'][2]),max(prev['bbox'][3],b['bbox'][3]))
        else:merged.append(b)
    image_boxes=[]
    for info in p.get_image_info():
        box=fitz.Rect(info['bbox']) & clip
        if box.is_empty or box.width*box.height<120:continue
        image_boxes.append(local_box(box,clip,rotate))
    art=None
    if image_boxes:
        x0=max(0,min(b[0] for b in image_boxes));y0=max(0,min(b[1] for b in image_boxes))
        x1=min(clip.width,max(b[2] for b in image_boxes));y1=min(clip.height,max(b[3] for b in image_boxes))
        art=[x0,y0,x1,y1]
        # Back cover contains a logo and decorative divider; retain the top illustration separately.
        if number==16:art=[105,24,220,112]
        # Cover typography is re-created as HTML; crop away its bottom credits.
        if number==1:art=[0,99,358,499]
        # Remove PDF text operators only. Preserve all raster art and vector drawing.
        artdoc=fitz.open(ROOT/'unnamed-file-331.pdf'); artpage=artdoc[pdf-1]
        for block in artpage.get_text('dict')['blocks']:
            if block['type']!=0: continue
            for line in block['lines']:
                rect=fitz.Rect(line['bbox'])
                # These words belong to the illustrated book, not the narrative.
                if pdf==12 and rect.x0>600 and rect.y1<300: continue
                artpage.add_redact_annot(rect,fill=False)
        artpage.apply_redactions(images=0,graphics=0)
        if number==12:
            artpage.draw_rect(fitz.Rect(735,51,750,73),color=None,fill=(1,1,1),overlay=True)
        apix=artpage.get_pixmap(matrix=fitz.Matrix(2,2),clip=clip,alpha=False)
        aim=Image.frombytes('RGB',(apix.width,apix.height),apix.samples)
        if rotate: aim=aim.rotate(180)
        art=[max(3,art[0]),max(3,art[1]),min(clip.width-3,art[2]),min(clip.height-3,art[3])]
        crop=aim.crop(tuple(round(v*2) for v in art))
        diff=ImageChops.difference(crop,Image.new('RGB',crop.size,'white')).convert('L')
        bounds=diff.point(lambda x:255 if x>28 else 0).getbbox()
        if bounds: crop=crop.crop(bounds)
        artdoc.close()
        crop.save(ROOT/f'dist/assets/page-{number:02}.webp','WEBP',quality=94,method=6)
    if number==16:
        for i,b in enumerate(merged): b['lang']='ts' if i in (1,3) else 'en'
    records.append({'page':number,'pdf_page':pdf,'quadrant':quadrant,'rotated':rotate,'blocks':merged,'art_bbox':art})
contact=Image.new('RGB',(4*265,4*410),'#e7e7e7');draw=ImageDraw.Draw(contact)
for i,im in enumerate(previews):
    x=(i%4)*265+10;y=(i//4)*410+25;contact.paste(im,(x,y));draw.text((x,y-18),str(i+1),fill='black')
contact.save(ROOT/'tmp/pdfs/contact.jpg')
(ROOT/'story-source.json').write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n')
for r in records:
 print('\nPAGE',r['page'],'ART',r['art_bbox'])
 for b in r['blocks']:print(b['lang'],b['text'])
# Publisher mark from the original back cover.
logo=doc[4].get_pixmap(matrix=fitz.Matrix(2,2),clip=fitz.Rect(287,980,378,1044),alpha=False)
Image.frombytes('RGB',(logo.width,logo.height),logo.samples).save(ROOT/'dist/assets/nalibali.webp','WEBP',quality=94)
