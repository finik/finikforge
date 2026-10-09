from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.boundsPen import BoundsPen
import math
import os as _os
_HERE=_os.path.dirname(_os.path.abspath(__file__))
_LOCAL=_os.path.join(_HERE,'vfonts','LiberationSans-Bold.ttf')
DEFAULT=_LOCAL if _os.path.exists(_LOCAL) else '/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf'
_cache={}
def _ctx(path):
    if path not in _cache:
        f=TTFont(path)
        _cache[path]=dict(gs=f.getGlyphSet(), cmap=f.getBestCmap(),
                          upm=f['head'].unitsPerEm, hmtx=f['hmtx'])
    return _cache[path]
def _d_adv(ctx,ch):
    g=ctx['cmap'][ord(ch)]; pen=SVGPathPen(ctx['gs']); ctx['gs'][g].draw(pen)
    return pen.getCommands(), ctx['hmtx'][g][0]
def _bbox(ctx,ch):
    g=ctx['cmap'][ord(ch)]; pen=BoundsPen(ctx['gs']); ctx['gs'][g].draw(pen)
    return (0,0) if pen.bounds is None else (pen.bounds[1],pen.bounds[3])

def number_path(num, size, cx, cy, fill='#fff', font=DEFAULT):
    if num=='' or num is None: return ''
    ctx=_ctx(font); s=size/ctx['upm']
    glyphs=[(ch,)+_d_adv(ctx,ch) for ch in str(num)]
    totw=sum(a for _,_,a in glyphs)*s
    ys=[_bbox(ctx,ch) for ch in str(num)]
    ymid=(min(y0 for y0,_ in ys)+max(y1 for _,y1 in ys))/2*s
    x=cx-totw/2; parts=[]
    for ch,d,adv in glyphs:
        parts.append(f'<g transform="translate({x:.3f},{cy+ymid:.3f}) scale({s:.5f},{-s:.5f})"><path d="{d}"/></g>')
        x+=adv*s
    return f'<g fill="{fill}">{"".join(parts)}</g>'

def arc_text(text, radius, size, ls, side, cx, cy, fill, font=DEFAULT):
    ctx=_ctx(font); s=size/ctx['upm']
    items=[(ch,)+_d_adv(ctx,ch) for ch in text]
    advs=[a*s for _,_,a in items]
    n=len(items)
    # slot center of each glyph along the baseline; letter-spacing is a gap BETWEEN glyphs (n-1 gaps)
    centers=[]; x=0.0
    for aw in advs:
        centers.append(x+aw/2.0); x+=aw+ls
    # anchor the middle glyph at phi=0 (dead-center) for odd counts; extent-midpoint for even
    anchor = centers[n//2] if n%2==1 else (centers[n//2-1]+centers[n//2])/2.0
    parts=[]
    for (ch,d,adv),c0 in zip(items,centers):
        c=c0-anchor; phi=c/radius
        if side=='top':
            px=cx+radius*math.sin(phi); py=cy-radius*math.cos(phi); rot=math.degrees(phi)
        else:
            px=cx+radius*math.sin(phi); py=cy+radius*math.cos(phi); rot=-math.degrees(phi)
        parts.append(f'<g transform="translate({px:.3f},{py:.3f}) rotate({rot:.3f}) scale({s:.5f},{-s:.5f}) translate({-adv/2:.2f},0)"><path d="{d}"/></g>')
    return f'<g fill="{fill}">{"".join(parts)}</g>'
