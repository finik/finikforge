"""
Regenerate the FINIK FORGE packages (per-weight vendor sizes, all formats), 10- or 12-sided.

Usage:
  python3 gen_finik_forge.py            # both variants -> ./output_12sided and ./output_10sided
  python3 gen_finik_forge.py 12         # just 12-sided -> ./output_12sided
  python3 gen_finik_forge.py 10 mydir   # 10-sided -> ./mydir

Sizing: each badge's corner-to-corner width = the vendor 12-sided head diameter, so 10- and 12-sided
badges share the same footprint and drop onto the same heads. Page (design box) = head * half/Rbg.
Requires: pip install --break-system-packages cairosvg fonttools opencv-python numpy pillow
"""
import os, io, sys, math
import badge as B, textpath as TP, cairosvg
from PIL import Image, ImageDraw

VF=os.path.join(os.path.dirname(__file__),'vfonts','Viking-Bold.otf')
NUMF=TP.DEFAULT

# vendor 12-sided dumbbell HEAD diameter (max across-corners), inches.
VENDOR_IN={5:4.125,10:4.625,15:5.375,20:5.875,25:6.125,30:6.5,35:6.875,
           40:7.5,45:7.5,50:7.5,55:7.5,60:7.5,65:7.5,70:7.5,75:7.5}

def page_mm(w, sides):
    """Physical page (design box) in mm so the badge's corner-to-corner = vendor head diameter."""
    v=B.VARIANTS[sides]; half,_,_=B._frame(v)
    return round(VENDOR_IN[w]*25.4 * half/v['Rbg'], 1)

def plates(sides):
    return [(f'{w:02d}lb',str(w),page_mm(w,sides)) for w in sorted(VENDOR_IN)]+[('blank','',page_mm(50,sides))]

def gen(sides=12, out=None):
    out = out or f'output_{sides}sided'
    P = plates(sides)
    for sub in ('artwork','pdf','eps','ai','burn','burn-eps','burn-ai','burn-pdf'):
        os.makedirs(f'{out}/{sub}',exist_ok=True)
    art=B.trace(173,sides=sides)          # red-art trace is head_mm-independent -> once per variant
    for name,num,hm in P:
        a =B.build_art (num,hm,sides=sides,text_font=VF,num_font=NUMF)
        bn=B.build_burn(num,hm,sides=sides,art=art,text_font=VF,num_font=NUMF)
        open(f'{out}/artwork/finik_forge_{name}.svg','w').write(a)
        open(f'{out}/burn/finik_forge_{name}_burn.svg','w').write(bn)
        cairosvg.svg2pdf(bytestring=a.encode(), write_to=f'{out}/pdf/finik_forge_{name}.pdf')
        cairosvg.svg2eps(bytestring=a.encode(), write_to=f'{out}/eps/finik_forge_{name}.eps')
        cairosvg.svg2pdf(bytestring=a.encode(), write_to=f'{out}/ai/finik_forge_{name}.ai')
        cairosvg.svg2eps(bytestring=bn.encode(),write_to=f'{out}/burn-eps/finik_forge_{name}_burn.eps')
        cairosvg.svg2pdf(bytestring=bn.encode(),write_to=f'{out}/burn-pdf/finik_forge_{name}_burn.pdf')
        cairosvg.svg2pdf(bytestring=bn.encode(),write_to=f'{out}/burn-ai/finik_forge_{name}_burn.ai')
    _contact(sides,out,P); _truesizes(sides,out,P)
    print(f'DONE {sides}-sided -> {out}/  ({len(P)} plates x 8 formats)')

def _contact(sides,out,P):
    cell=360;cols=4;rows=4;pad=12
    sheet=Image.new('RGB',(cols*cell+pad*(cols+1),rows*cell+pad*(rows+1)),(40,40,40))
    for i,(name,num,hm) in enumerate(P):
        a=B.build_art(num,hm,sides=sides,text_font=VF,num_font=NUMF)
        im=Image.open(io.BytesIO(cairosvg.svg2png(bytestring=a.encode(),output_width=cell,output_height=cell,background_color='#262626'))).convert('RGB')
        r,c=divmod(i,cols); sheet.paste(im,(pad+c*(cell+pad),pad+r*(cell+pad)))
    sheet.save(f'{out}/finik_forge_contactsheet.png')

def _truesizes(sides,out,P):
    v=B.VARIANTS[sides]; half,_,_=B._frame(v)
    cols=4;rows=4;scale=2.4;cellt=int(190*scale)+34
    proof=Image.new('RGB',(cols*cellt,rows*cellt),(245,245,245))
    for i,(name,num,hm) in enumerate(P):
        cd=hm*v['Rbg']/half;d=int(cd*scale)
        a=B.build_art(num,hm,sides=sides,text_font=VF,num_font=NUMF)
        im=Image.open(io.BytesIO(cairosvg.svg2png(bytestring=a.encode(),output_width=d,output_height=d,background_color='#1a1a1a'))).convert('RGB')
        r,c=divmod(i,cols);cx=c*cellt+cellt//2;cy=r*cellt+cellt//2
        proof.paste(im,(cx-d//2,cy-d//2)); ImageDraw.Draw(proof).text((c*cellt+8,r*cellt+8),f'{name}  {cd:.0f}mm',fill=(20,20,20))
    proof.save(f'{out}/finik_forge_truesizes.png')

if __name__=='__main__':
    a=sys.argv[1:]
    if a and a[0] in ('10','12'):
        gen(int(a[0]), a[1] if len(a)>1 else None)
    else:
        gen(12); gen(10)
