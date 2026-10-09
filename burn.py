import cairosvg, cv2, numpy as np, math, io
import hammerbuild as HB, textpath as TP

C=HB.C; Rbg=298; cos15=math.cos(math.radians(15)); DBBOX=2*Rbg*cos15; BBMIN=C-Rbg*cos15

def trace_redart(head_mm, N=2400, eps_px=0.9, **kw):
    svg=HB.build_redart_mask(head_mm, **kw)
    png=cairosvg.svg2png(bytestring=svg.encode(), output_width=N, output_height=N, background_color='white')
    arr=cv2.imdecode(np.frombuffer(png,np.uint8), cv2.IMREAD_GRAYSCALE)
    fg=(arr<128).astype(np.uint8)*255
    cnts,hier=cv2.findContours(fg, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
    sc=DBBOX/N
    subs=[]
    for cnt in cnts:
        if cv2.contourArea(cnt) < 4: continue
        ap=cv2.approxPolyDP(cnt, eps_px, True).reshape(-1,2)
        if len(ap)<3: continue
        pts=[(BBMIN+x*sc, BBMIN+y*sc) for x,y in ap]
        d='M'+' L'.join(f'{px:.2f},{py:.2f}' for px,py in pts)+' Z'
        subs.append(d)
    return ' '.join(subs)

def build_burn_layer_svg(num, head_mm, num_font_mm=30.0, burn_color='#E11414', num_color='#ffffff',
                         show_bg=False, text_font=TP.DEFAULT, num_font=TP.DEFAULT,
                         ls_fin=21, ls_forge=36, registration=True, art=None, **kw):
    if art is None:
        art=trace_redart(head_mm, **kw)
    rt,rb=158,206
    fin=TP.arc_text('FINIK',rt,70,ls_fin,'top',C,C,burn_color,font=text_font)
    forge=TP.arc_text('FORGE',rb,70,ls_forge,'bottom',C,C,burn_color,font=text_font)
    nf=num_font_mm*DBBOX/head_mm
    numpath=TP.number_path(num,nf,C,C,num_color,font=num_font) if num else ''
    bg=f'<rect x="{BBMIN:.2f}" y="{BBMIN:.2f}" width="{DBBOX:.2f}" height="{DBBOX:.2f}" fill="#0e0e0e"/>' if show_bg else ''
    reg=''
    if registration:
        pts=' '.join(f'{C+Rbg*math.cos(math.radians(k*30+15)):.2f},{C-Rbg*math.sin(math.radians(k*30+15)):.2f}' for k in range(12))
        reg=f'<polygon points="{pts}" fill="none" stroke="#888888" stroke-width="0.5" stroke-dasharray="6 4"/>'
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="{BBMIN:.2f} {BBMIN:.2f} {DBBOX:.2f} {DBBOX:.2f}" width="{head_mm}mm" height="{head_mm}mm">
{bg}<g id="engrave-red" fill="{burn_color}" fill-rule="evenodd"><path d="{art}"/>{fin}{forge}</g>
<g id="engrave-white" fill="{num_color}">{numpath}</g>
<g id="registration">{reg}</g>
</svg>'''

def _inner(svg):
    return svg[svg.index('>', svg.index('<svg'))+1 : svg.rindex('</svg>')]

def build_final(num, head_mm, num_font_mm=30.0, **kw):
    """Main deliverable: ARTWORK layer (visible) + BURN layer (engrave geometry, hidden)."""
    art_svg=HB.build_prod(num, head_mm, num_font_mm=num_font_mm, **kw)
    burn_svg=build_burn_layer_svg(num, head_mm, num_font_mm=num_font_mm, show_bg=False, **kw)
    head=art_svg[:art_svg.index('>')+1].replace('<svg ', '<svg xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape" ')
    return (head+'\n'
            +'<g inkscape:groupmode="layer" inkscape:label="ARTWORK">'+_inner(art_svg)+'</g>\n'
            +'<g inkscape:groupmode="layer" inkscape:label="BURN" style="display:none">'+_inner(burn_svg)+'</g>\n'
            +'</svg>')

def build_burn_only(num, head_mm, num_font_mm=30.0, text_font=TP.DEFAULT, num_font=TP.DEFAULT, art=None, **kw):
    """Standalone burn file: just engrave geometry on transparent bg."""
    return build_burn_layer_svg(num, head_mm, num_font_mm=num_font_mm, show_bg=False,
                                text_font=text_font, num_font=num_font, art=art, **kw)
