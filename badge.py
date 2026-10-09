"""
FINIK FORGE unified badge builder (10- and 12-sided).
Rebuilt from the working state as of 2026-06-30. See HANDOFF.md.

KEY PARAMS (do not regress):
  VK_GAP=16  valknut weave-gap (widened from 8 so 5lb weave channels clear ~0.8mm for paint)
  CAS=9      weapon casing width  (over-weave gaps: sword grips over outer ring, heads over inner)
  FIXX=7     ring-fix eraser extra (under-weave gaps: handles under outer, blades under inner)
  VARIANTS[12] ls_fin=24 / ls_forge=36  (FINIK widened to match FORGE width ~75mm)

CRITICAL BURN-TRACE FIX: in _mask() the valknut MUST pass gapcolor=GAP (white). The mask is
black-ink-on-white and gets contour-traced; if the valknut weave gaps use vk.group's default
dark gapcolor (#0e0e0e) they vanish against the black ink and the three triangles fuse into a
blob in every burn file. gapcolor=GAP renders them as white holes the tracer captures.
"""
import math, io
import hammerbuild as H, sword as SW, vk, textpath as TP, cairosvg, cv2, numpy as np
C=H.C; RED=H.RED; BLK=H.BLK; R_OUT=H.R_OUT; R_IN=H.R_IN; W=H.W; S=H.S; bcx=H.bcx; bcy=H.bcy

# per-variant geometry. Shared design: axe+hammer weave B (handle under outer, head over inner),
# both swords weave A (grip over outer, blade under inner), blades shortened (sword_Lb=105).
VARIANTS={
    10: dict(sides=10, step=36, offset=0,  tilt=36, Rbg=302, content_scale=1.04, ls_fin=8,  ls_forge=14, sword_Lb=105, framing='circum'),
    12: dict(sides=12, step=30, offset=15, tilt=30, Rbg=298, content_scale=1.00, ls_fin=24, ls_forge=36, sword_Lb=105, framing='flats'),
}
RT, RB = 158, 206
AXP=dict(r_inner=120,sc=0.155,flip=False,anchor=(430,150),extra=0)
HM_R, HM_S = 116, 0.82
VK_GAP = 16
CAS  = 9
FIXX = 7

def _frame(v):
    Rbg=v['Rbg']
    if v['framing']=='flats':
        half=Rbg*math.cos(math.radians(180/v['sides']))   # dodecagon across-flats (offset 15)
    else:
        half=Rbg+4                                         # decagon: circumscribed square
    return half, C-half, 2*half   # half, vbmin, vbsz

def _polygon(v, fill):
    Rbg=v['Rbg']
    pts=" ".join(f"{C+Rbg*math.cos(math.radians(k*v['step']+v['offset'])):.2f},"
                 f"{C-Rbg*math.sin(math.radians(k*v['step']+v['offset'])):.2f}" for k in range(v['sides']))
    return f'<polygon points="{pts}" fill="{fill}"/>'

def _weapons_and_fixes(v, red, casing, ring, gap):
    """Weapons (casing+colored) + ring-weave fixes.
       Artwork: red/ring=RED, casing/gap=BLK.  Mask: red/ring=ink(black), casing/gap=white."""
    tilt=v['tilt']; a_tr=tilt; a_tl=180-tilt; a_bl=180+tilt; a_br=360-tilt
    sw=''
    _old=SW.Lb; SW.Lb=v['sword_Lb']
    for ang,lf in [(a_br,False),(a_bl,True)]:
        sw+=f'<g transform="{SW.place(ang)}">{SW.sword_shapes(casing,casing,CAS,False,lf)}</g>'   # casing halo
        sw+=f'<g transform="{SW.place(ang)}">{SW.sword_shapes(red,"none",0,True,lf)}</g>'          # colored (full size)
    SW.Lb=_old
    ax=(H.axe_g(a_tr,AXP['r_inner'],AXP['sc'],AXP['flip'],casing,casing,CAS/AXP['sc'],AXP['anchor'],AXP['extra'])
        +H.axe_g(a_tr,AXP['r_inner'],AXP['sc'],AXP['flip'],red,'none',0,AXP['anchor'],AXP['extra']))
    hm=(H.mjolnir_g(a_tl,HM_R,casing,casing,CAS/HM_S,ssc=HM_S)
        +H.mjolnir_g(a_tl,HM_R,red,ssc=HM_S))
    fixes=''
    for ang,ty in [(a_tr,'B'),(a_tl,'B'),(a_bl,'A'),(a_br,'A')]:
        if ty=='A': fixes+=SW.ring_arc(R_IN,ang,7,gap,W+FIXX)+SW.ring_arc(R_IN,ang,7,ring,W)   # blade under inner ring
        else:       fixes+=SW.ring_arc(R_OUT,ang,6,gap,W+FIXX)+SW.ring_arc(R_OUT,ang,6,ring,W) # handle under outer ring
    return sw+ax+hm, fixes

def build_art(num, head_mm, sides=12, num_font_mm=30.0, text_font=TP.DEFAULT, num_font=TP.DEFAULT):
    v=VARIANTS[sides]; cs=v['content_scale']; half,vbmin,vbsz=_frame(v)
    TL=f'translate({C-182},{C}) scale({S}) translate({-bcx},{-bcy})'
    vleft=vk.group(RED,TL,gap=VK_GAP); vright=vk.group(RED,f'translate({2*C},0) scale(-1,1) {TL}',gap=VK_GAP)
    weap,fixes=_weapons_and_fixes(v,RED,BLK,RED,BLK)
    fin=TP.arc_text('FINIK',RT,70,v['ls_fin'],'top',C,C,RED,font=text_font)
    forge=TP.arc_text('FORGE',RB,70,v['ls_forge'],'bottom',C,C,RED,font=text_font)
    rings=(f'<circle cx="{C}" cy="{C}" r="{R_OUT}" fill="none" stroke="{RED}" stroke-width="{W}"/>'
           f'<circle cx="{C}" cy="{C}" r="{R_IN}" fill="none" stroke="{RED}" stroke-width="{W}"/>')
    content=f'{rings}{fin}{forge}{vleft}{vright}{weap}{fixes}'
    content=f'<g transform="translate({C},{C}) scale({cs}) translate({-C},{-C})">{content}</g>'
    nf=num_font_mm*vbsz/head_mm            # constant physical number size
    numpath=TP.number_path(num,nf,C,C,'#fff',font=num_font) if num else ''
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vbmin:.2f} {vbmin:.2f} {vbsz:.2f} {vbsz:.2f}" width="{head_mm}mm" height="{head_mm}mm">
{_polygon(v,BLK)}
{content}
{numpath}
</svg>'''

def _mask(head_mm, sides=12):
    """Black art on white bg, no text/number/frame - for contour tracing (build_burn)."""
    v=VARIANTS[sides]; cs=v['content_scale']; half,vbmin,vbsz=_frame(v)
    INK='#000'; GAP='#fff'
    TL=f'translate({C-182},{C}) scale({S}) translate({-bcx},{-bcy})'
    # gapcolor=GAP (white) is REQUIRED so valknut weave gaps trace as holes (see module docstring)
    vleft=vk.group(INK,TL,gap=VK_GAP,gapcolor=GAP); vright=vk.group(INK,f'translate({2*C},0) scale(-1,1) {TL}',gap=VK_GAP,gapcolor=GAP)
    weap,fixes=_weapons_and_fixes(v,INK,GAP,INK,GAP)
    rings=(f'<circle cx="{C}" cy="{C}" r="{R_OUT}" fill="none" stroke="{INK}" stroke-width="{W}"/>'
           f'<circle cx="{C}" cy="{C}" r="{R_IN}" fill="none" stroke="{INK}" stroke-width="{W}"/>')
    content=f'{rings}{vleft}{vright}{weap}{fixes}'
    content=f'<g transform="translate({C},{C}) scale({cs}) translate({-C},{-C})">{content}</g>'
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vbmin:.2f} {vbmin:.2f} {vbsz:.2f} {vbsz:.2f}" width="{vbsz}" height="{vbsz}">{content}</svg>'''

def trace(head_mm, sides=12, N=2600, eps_px=0.8):
    """Trace the red-art mask into a single evenodd path (holes preserved). head_mm-independent."""
    v=VARIANTS[sides]; half,vbmin,vbsz=_frame(v)
    png=cairosvg.svg2png(bytestring=_mask(head_mm,sides).encode(), output_width=N, output_height=N, background_color='white')
    arr=cv2.imdecode(np.frombuffer(png,np.uint8), cv2.IMREAD_GRAYSCALE)
    fg=(arr<128).astype(np.uint8)*255
    cnts,_=cv2.findContours(fg, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
    sc=vbsz/N; subs=[]
    for cnt in cnts:
        if cv2.contourArea(cnt)<4: continue
        ap=cv2.approxPolyDP(cnt,eps_px,True).reshape(-1,2)
        if len(ap)<3: continue
        pts=[(vbmin+x*sc, vbmin+y*sc) for x,y in ap]
        subs.append('M'+' L'.join(f'{px:.2f},{py:.2f}' for px,py in pts)+' Z')
    return ' '.join(subs)

def build_burn(num, head_mm, sides=12, art=None, num_font_mm=30.0, text_font=TP.DEFAULT, num_font=TP.DEFAULT,
               burn_color='#E11414', num_color='#ffffff'):
    """Laser file: engrave-red (traced art + outlined FINIK/FORGE) + engrave-white (number) + registration."""
    v=VARIANTS[sides]; cs=v['content_scale']; half,vbmin,vbsz=_frame(v)
    if art is None: art=trace(head_mm,sides)
    fin=TP.arc_text('FINIK',RT,70,v['ls_fin'],'top',C,C,burn_color,font=text_font)
    forge=TP.arc_text('FORGE',RB,70,v['ls_forge'],'bottom',C,C,burn_color,font=text_font)
    txt=f'<g transform="translate({C},{C}) scale({cs}) translate({-C},{-C})">{fin}{forge}</g>'
    nf=num_font_mm*vbsz/head_mm
    numpath=TP.number_path(num,nf,C,C,num_color,font=num_font) if num else ''
    Rbg=v['Rbg']
    rpts=" ".join(f"{C+Rbg*math.cos(math.radians(k*v['step']+v['offset'])):.2f},"
                  f"{C-Rbg*math.sin(math.radians(k*v['step']+v['offset'])):.2f}" for k in range(v['sides']))
    reg=f'<polygon points="{rpts}" fill="none" stroke="#888888" stroke-width="0.5" stroke-dasharray="6 4"/>'
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vbmin:.2f} {vbmin:.2f} {vbsz:.2f} {vbsz:.2f}" width="{head_mm}mm" height="{head_mm}mm">
<g id="engrave-red" fill="{burn_color}" fill-rule="evenodd"><path d="{art}"/>{txt}</g>
<g id="engrave-white" fill="{num_color}">{numpath}</g>
<g id="registration">{reg}</g>
</svg>'''
