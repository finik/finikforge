import vk, cairosvg, math
import sword as SW
C=280; RED='#E11414'; BLK='#0e0e0e'; FONT='Arial, Helvetica, sans-serif'; S=0.16; bcx,bcy=374.0,204.5
R_OUT=224; R_IN=140; W=8
AXE_D=open('AXE_d.txt').read().strip()

def axe_place(theta,r_inner,sc,flip,anchor,extra=0):
    th=math.radians(theta); fx=-1 if flip else 1
    px=C+r_inner*math.cos(th); py=C-r_inner*math.sin(th)
    a=math.degrees(math.atan2(-math.cos(th),-math.sin(th)))+extra
    return f'translate({px:.2f},{py:.2f}) rotate({a:.2f}) scale({sc*fx},{sc}) translate({-anchor[0]},{-anchor[1]})'
def axe_g(theta,r_inner,sc,flip,fill,stroke,sw,anchor,extra=0):
    st=f'stroke="{stroke}" stroke-width="{sw}" stroke-linejoin="round"' if stroke!='none' else ''
    return f'<g transform="{axe_place(theta,r_inner,sc,flip,anchor,extra)}"><path d="{AXE_D}" fill="{fill}" {st}/></g>'

def mjolnir(fill, stroke='none', sw=0):
    st=f'stroke="{stroke}" stroke-width="{sw}" stroke-linejoin="round"' if stroke!='none' else ''
    head='M -28,0 L 28,0 L 38,7 L 38,37 L 28,44 L -28,44 L -38,37 L -38,7 Z'
    handle='M -6,30 L 6,30 L 6,148 L -6,148 Z'
    cap='M -9,147 L 9,147 L 9,157 L -9,157 Z'
    return f'<path d="{head}" fill="{fill}" {st}/><path d="{handle}" fill="{fill}" {st}/><path d="{cap}" fill="{fill}" {st}/>'
def mjolnir_g(theta, r_inner, fill, stroke='none', sw=0, ssc=1.0):
    th=math.radians(theta); px=C+r_inner*math.cos(th); py=C-r_inner*math.sin(th)
    a=math.degrees(math.atan2(-math.cos(th),-math.sin(th)))
    return f'<g transform="translate({px:.2f},{py:.2f}) rotate({a:.2f}) scale({ssc})">{mjolnir(fill,stroke,sw)}</g>'

def build(bottom='FORGE', bls=11,
          axp=dict(r_inner=120,sc=0.155,flip=False,anchor=(430,150),extra=0),
          hm_r=116, tilt=30, hm_s=0.82, num="50"):
    TL=f'translate({C-182},{C}) scale({S}) translate({-bcx},{-bcy})'
    vleft=vk.group(RED,TL,gap=8); vright=vk.group(RED,f'translate({2*C},0) scale(-1,1) {TL}',gap=8)
    rt,rb=158,206
    top=f'M {C-rt},{C} A {rt},{rt} 0 0 1 {C+rt},{C}'; bot=f'M {C-rb},{C} A {rb},{rb} 0 0 0 {C+rb},{C}'
    a_tr=tilt; a_tl=180-tilt; a_bl=180+tilt; a_br=360-tilt   # tr=axe, tl=hammer, bl=leaf sword, br=straight sword
    sw_cas=''; sw_red=''
    for ang,lf in [(a_br,False),(a_bl,True)]:
        sw_cas+=f'<g transform="{SW.place(ang)}">{SW.sword_shapes(BLK,BLK,6,False,lf)}</g>'
        sw_red+=f'<g transform="{SW.place(ang)}">{SW.sword_shapes(RED,"none",0,True,lf)}</g>'
    ax_cas=axe_g(a_tr,axp['r_inner'],axp['sc'],axp['flip'],BLK,BLK,6/axp['sc'],axp['anchor'],axp['extra'])
    ax_red=axe_g(a_tr,axp['r_inner'],axp['sc'],axp['flip'],RED,'none',0,axp['anchor'],axp['extra'])
    hm_cas=mjolnir_g(a_tl,hm_r,BLK,BLK,6/hm_s,ssc=hm_s)
    hm_red=mjolnir_g(a_tl,hm_r,RED,ssc=hm_s)
    fixes=''
    for ang,ty in [(a_tr,'B'),(a_tl,'B'),(a_bl,'A'),(a_br,'B')]:  # axe=type B: handle UNDER outer ring, blade/beard OVER inner ring (clean weave)
        if ty=='A': fixes+=SW.ring_arc(R_IN,ang,7,BLK,W+6)+SW.ring_arc(R_IN,ang,7,RED,W)
        else:       fixes+=SW.ring_arc(R_OUT,ang,6,BLK,W+6)+SW.ring_arc(R_OUT,ang,6,RED,W)
    Rbg=298; VBH=306
    bgpts=" ".join(f"{C+Rbg*math.cos(math.radians(k*30+15)):.2f},{C-Rbg*math.sin(math.radians(k*30+15)):.2f}" for k in range(12))
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="{C-VBH} {C-VBH} {2*VBH} {2*VBH}" width="{2*VBH}" height="{2*VBH}">
<polygon points="{bgpts}" fill="{BLK}"/>
<circle cx="{C}" cy="{C}" r="{R_OUT}" fill="none" stroke="{RED}" stroke-width="{W}"/>
<circle cx="{C}" cy="{C}" r="{R_IN}" fill="none" stroke="{RED}" stroke-width="{W}"/>
<path id="top" d="{top}" fill="none"/><path id="bot" d="{bot}" fill="none"/>
<text font-family="{FONT}" font-weight="bold" font-size="70" fill="{RED}" letter-spacing="8"><textPath href="#top" startOffset="50%" text-anchor="middle">FINIK</textPath></text>
<text font-family="{FONT}" font-weight="bold" font-size="70" fill="{RED}" letter-spacing="{bls}"><textPath href="#bot" startOffset="50%" text-anchor="middle">{bottom}</textPath></text>
{vleft}{vright}
{sw_cas}{sw_red}{ax_cas}{ax_red}{hm_cas}{hm_red}{fixes}
<text x="{C}" y="{C}" font-family="{FONT}" font-weight="bold" font-size="112" fill="#fff" text-anchor="middle" dominant-baseline="central">{num}</text>
</svg>'''
if __name__=="__main__":
    cairosvg.svg2png(bytestring=build().encode(),write_to="hb3.png",output_width=460,background_color="white")
    print("ok")

import textpath as TP
def build_prod(num, head_mm, num_font_mm=30.0, text_font=TP.DEFAULT, num_font=TP.DEFAULT,
               axp=dict(r_inner=120,sc=0.155,flip=False,anchor=(430,150),extra=0),
               hm_r=116, tilt=30, hm_s=0.82):
    # ---- identical geometry to build() ----
    TL=f'translate({C-182},{C}) scale({S}) translate({-bcx},{-bcy})'
    vleft=vk.group(RED,TL,gap=8); vright=vk.group(RED,f'translate({2*C},0) scale(-1,1) {TL}',gap=8)
    rt,rb=158,206
    a_tr=tilt; a_tl=180-tilt; a_bl=180+tilt; a_br=360-tilt
    sw_cas=''; sw_red=''
    for ang,lf in [(a_br,False),(a_bl,True)]:
        sw_cas+=f'<g transform="{SW.place(ang)}">{SW.sword_shapes(BLK,BLK,6,False,lf)}</g>'
        sw_red+=f'<g transform="{SW.place(ang)}">{SW.sword_shapes(RED,"none",0,True,lf)}</g>'
    ax_cas=axe_g(a_tr,axp['r_inner'],axp['sc'],axp['flip'],BLK,BLK,6/axp['sc'],axp['anchor'],axp['extra'])
    ax_red=axe_g(a_tr,axp['r_inner'],axp['sc'],axp['flip'],RED,'none',0,axp['anchor'],axp['extra'])
    hm_cas=mjolnir_g(a_tl,hm_r,BLK,BLK,6/hm_s,ssc=hm_s)
    hm_red=mjolnir_g(a_tl,hm_r,RED,ssc=hm_s)
    fixes=''
    for ang,ty in [(a_tr,'B'),(a_tl,'B'),(a_bl,'A'),(a_br,'B')]:  # axe=type B: handle UNDER outer ring, blade/beard OVER inner ring (clean weave)
        if ty=='A': fixes+=SW.ring_arc(R_IN,ang,7,BLK,W+6)+SW.ring_arc(R_IN,ang,7,RED,W)
        else:       fixes+=SW.ring_arc(R_OUT,ang,6,BLK,W+6)+SW.ring_arc(R_OUT,ang,6,RED,W)
    Rbg=298
    bgpts=" ".join(f"{C+Rbg*math.cos(math.radians(k*30+15)):.2f},{C-Rbg*math.sin(math.radians(k*30+15)):.2f}" for k in range(12))
    # ---- text as outlines ----
    fin=TP.arc_text('FINIK',rt,70,21,'top',C,C,RED,font=text_font)
    forge=TP.arc_text('FORGE',rb,70,36,'bottom',C,C,RED,font=text_font)
    # constant physical number: font(design units) = num_font_mm * (designspan/head_mm)
    cos15=math.cos(math.radians(15)); DBBOX=2*Rbg*cos15; bbmin=C-Rbg*cos15
    nf=num_font_mm*DBBOX/head_mm
    numpath=TP.number_path(num,nf,C,C,'#fff',font=num_font)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="{bbmin:.2f} {bbmin:.2f} {DBBOX:.2f} {DBBOX:.2f}" width="{head_mm}mm" height="{head_mm}mm">
<polygon points="{bgpts}" fill="{BLK}"/>
<circle cx="{C}" cy="{C}" r="{R_OUT}" fill="none" stroke="{RED}" stroke-width="{W}"/>
<circle cx="{C}" cy="{C}" r="{R_IN}" fill="none" stroke="{RED}" stroke-width="{W}"/>
{fin}{forge}
{vleft}{vright}
{sw_cas}{sw_red}{ax_cas}{ax_red}{hm_cas}{hm_red}{fixes}
{numpath}
</svg>'''

def build_redart_mask(head_mm, axp=dict(r_inner=120,sc=0.155,flip=False,anchor=(430,150),extra=0),
                      hm_r=116, tilt=30, hm_s=0.82):
    """Rings+weapons+valknuts ONLY, rendered BLACK on WHITE (erasers=white). No text/number.
    Used to trace the gappy art into true vector contours."""
    Bk='#000000'; Wt='#ffffff'
    TL=f'translate({C-182},{C}) scale({S}) translate({-bcx},{-bcy})'
    vleft=vk.group(Bk,TL,gap=8,gapcolor=Wt); vright=vk.group(Bk,f'translate({2*C},0) scale(-1,1) {TL}',gap=8,gapcolor=Wt)
    a_tr=tilt; a_tl=180-tilt; a_bl=180+tilt; a_br=360-tilt
    sw_cas=''; sw_red=''
    for ang,lf in [(a_br,False),(a_bl,True)]:
        sw_cas+=f'<g transform="{SW.place(ang)}">{SW.sword_shapes(Wt,Wt,6,False,lf)}</g>'
        sw_red+=f'<g transform="{SW.place(ang)}">{SW.sword_shapes(Bk,"none",0,True,lf)}</g>'
    # NOTE: sword fuller is drawn with BLK(#0e0e0e) hard-coded -> must become WHITE in mask; patch below
    sw_red=sw_red.replace('#0e0e0e',Wt)
    ax_cas=axe_g(a_tr,axp['r_inner'],axp['sc'],axp['flip'],Wt,Wt,6/axp['sc'],axp['anchor'],axp['extra'])
    ax_red=axe_g(a_tr,axp['r_inner'],axp['sc'],axp['flip'],Bk,'none',0,axp['anchor'],axp['extra'])
    hm_cas=mjolnir_g(a_tl,hm_r,Wt,Wt,6/hm_s,ssc=hm_s)
    hm_red=mjolnir_g(a_tl,hm_r,Bk,ssc=hm_s)
    fixes=''
    for ang,ty in [(a_tr,'B'),(a_tl,'B'),(a_bl,'A'),(a_br,'B')]:  # axe=type B: handle UNDER outer ring, blade/beard OVER inner ring (clean weave)
        if ty=='A': fixes+=SW.ring_arc(R_IN,ang,7,Wt,W+6)+SW.ring_arc(R_IN,ang,7,Bk,W)
        else:       fixes+=SW.ring_arc(R_OUT,ang,6,Wt,W+6)+SW.ring_arc(R_OUT,ang,6,Bk,W)
    Rbg=298; cos15=math.cos(math.radians(15)); DBBOX=2*Rbg*cos15; bbmin=C-Rbg*cos15
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="{bbmin:.2f} {bbmin:.2f} {DBBOX:.2f} {DBBOX:.2f}" width="{2*Rbg}" height="{2*Rbg}">
<rect x="{bbmin:.2f}" y="{bbmin:.2f}" width="{DBBOX:.2f}" height="{DBBOX:.2f}" fill="{Wt}"/>
<circle cx="{C}" cy="{C}" r="{R_OUT}" fill="none" stroke="{Bk}" stroke-width="{W}"/>
<circle cx="{C}" cy="{C}" r="{R_IN}" fill="none" stroke="{Bk}" stroke-width="{W}"/>
{vleft}{vright}
{sw_cas}{sw_red}{ax_cas}{ax_red}{hm_cas}{hm_red}{fixes}
</svg>'''
