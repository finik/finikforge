import vk, cairosvg, math
C=280; RED='#E11414'; BLK='#0e0e0e'; FONT='Arial, Helvetica, sans-serif'; S=0.16; bcx,bcy=374.0,204.5
R_OUT=224; R_IN=140; W=8
# sword local: tip at (0,0), extends +y (outward). dims chosen so blade crosses both rings.
r_tip=104; bw=14; Lb=130; gt=9; gw=44; Lg=12; grw=10; pr=8
def sword_shapes(fill, stroke, sw, fuller=False, leaf=False):
    st=f'stroke="{stroke}" stroke-width="{sw}" stroke-linejoin="round"' if stroke!='none' else ''
    if leaf:
        # viking taper: wider at guard, narrowing toward the point
        blade=f'<path d="M 0,0 L 5,18 L 9,{Lb} L -9,{Lb} L -5,18 Z" fill="{fill}" {st}/>'
    else:
        blade=f'<path d="M 0,0 L {bw/2},16 L {bw/2},{Lb} L {-bw/2},{Lb} L {-bw/2},16 Z" fill="{fill}" {st}/>'
    guard=f'<rect x="{-gw/2}" y="{Lb-2}" width="{gw}" height="{gt+2}" rx="2" fill="{fill}" {st}/>'
    if leaf:
        grip=f'<rect x="{-grw/2}" y="{Lb+gt-3}" width="{grw}" height="{Lg+5}" fill="{fill}" {st}/>'
        pom=f'<rect x="-9" y="{Lb+gt+Lg-2}" width="18" height="15" rx="1.5" fill="{fill}" {st}/>'
    else:
        grip=f'<rect x="{-grw/2}" y="{Lb+gt-3}" width="{grw}" height="{Lg+5}" fill="{fill}" {st}/>'
        y0=Lb+gt+Lg
        base=f'<rect x="-11" y="{y0-2}" width="22" height="8" rx="2" fill="{fill}" {st}/>'
        lobes=(f'<circle cx="-7" cy="{y0+6}" r="5.5" fill="{fill}" {st}/>'
               f'<circle cx="0" cy="{y0+7}" r="6.5" fill="{fill}" {st}/>'
               f'<circle cx="7" cy="{y0+6}" r="5.5" fill="{fill}" {st}/>')
        pom=base+lobes
    # center channel (fuller) removed per Dmitry's 6/2026 request; param kept for call-site compatibility
    fl=''
    return blade+guard+grip+pom+fl
def place(theta):
    th=math.radians(theta)
    tx=C+r_tip*math.cos(th); ty=C-r_tip*math.sin(th)
    a=math.degrees(math.atan2(-math.cos(th), -math.sin(th)))
    return f'translate({tx:.2f},{ty:.2f}) rotate({a:.2f})'
def ring_arc(rr, theta, dd, fill, sw):
    th0=math.radians(theta-dd); th1=math.radians(theta+dd)
    x0=C+rr*math.cos(th0); y0=C-rr*math.sin(th0)
    x1=C+rr*math.cos(th1); y1=C-rr*math.sin(th1)
    # minor arc; increasing math angle => sweep-flag 0 in y-down screen
    return f'<path d="M {x0:.2f},{y0:.2f} A {rr},{rr} 0 0 0 {x1:.2f},{y1:.2f}" fill="none" stroke="{fill}" stroke-width="{sw}"/>'

def build(bottom='FORCE', bls=11):
    TL=f'translate({C-182},{C}) scale({S}) translate({-bcx},{-bcy})'
    vleft=vk.group(RED,TL); vright=vk.group(RED,f'translate({2*C},0) scale(-1,1) {TL}')
    rt,rb=158,206
    top=f'M {C-rt},{C} A {rt},{rt} 0 0 1 {C+rt},{C}'
    bot=f'M {C-rb},{C} A {rb},{rb} 0 0 0 {C+rb},{C}'
    swords_ang=[30,150,210,330]; types=['A','B','A','B']  # A=over outer/under inner ; B=under outer/over inner
    casings=''.join(f'<g transform="{place(t)}">{sword_shapes(BLK,BLK,6)}</g>' for t in swords_ang)
    reds=''.join(f'<g transform="{place(t)}">{sword_shapes(RED,"none",0,True)}</g>' for t in swords_ang)
    # weave fix: redraw the ring that goes OVER the sword
    fixes=''
    for t,ty in zip(swords_ang,types):
        if ty=='A':   # under inner -> inner ring over sword
            fixes+=ring_arc(R_IN,t,7,BLK,W+6)+ring_arc(R_IN,t,7,RED,W)
        else:         # under outer -> outer ring over sword
            fixes+=ring_arc(R_OUT,t,6,BLK,W+6)+ring_arc(R_OUT,t,6,RED,W)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {2*C} {2*C}" width="{2*C}" height="{2*C}">
<circle cx="{C}" cy="{C}" r="274" fill="{BLK}"/>
<circle cx="{C}" cy="{C}" r="{R_OUT}" fill="none" stroke="{RED}" stroke-width="{W}"/>
<circle cx="{C}" cy="{C}" r="{R_IN}" fill="none" stroke="{RED}" stroke-width="{W}"/>
<path id="top" d="{top}" fill="none"/><path id="bot" d="{bot}" fill="none"/>
<text font-family="{FONT}" font-weight="bold" font-size="70" fill="{RED}" letter-spacing="11"><textPath href="#top" startOffset="50%" text-anchor="middle">FINIK</textPath></text>
<text font-family="{FONT}" font-weight="bold" font-size="70" fill="{RED}" letter-spacing="{bls}"><textPath href="#bot" startOffset="50%" text-anchor="middle">{bottom}</textPath></text>
{vleft}{vright}
{casings}{reds}{fixes}
<text x="{C}" y="{C}" font-family="{FONT}" font-weight="bold" font-size="112" fill="#fff" text-anchor="middle" dominant-baseline="central">50</text>
</svg>'''
if __name__=="__main__":
    cairosvg.svg2png(bytestring=build().encode(),write_to="sw.png",output_width=420,background_color="white")
    print("ok")
