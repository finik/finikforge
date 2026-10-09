"""
FINIK FORGE standalone brand logo (wall art / t-shirt) — NOT a dumbbell badge.
Weapons in their original positions, a large valknut centered, EST. / 2020 flanking it,
FINIK / FORGE around. No dumbbell plate. RED fill only; every weave gap is a true
transparent hole (traced, evenodd), so it prints clean on any shirt or wall color.

Usage: python3 gen_logo.py            -> ./logo/  (SVG + transparent PNG + black demo + EPS/AI/PDF)
Requires: pip install --break-system-packages cairosvg fonttools opencv-python numpy pillow
"""
import io, os, numpy as np, cv2, cairosvg
import badge as B, hammerbuild as H, vk, textpath as TP
VF=os.path.join(os.path.dirname(__file__),'vfonts','Viking-Bold.otf')
C=H.C; RED=H.RED; BLK=H.BLK; S=H.S; bcx=H.bcx; W=H.W; R_OUT=H.R_OUT; R_IN=H.R_IN
v=B.VARIANTS[12]; half,vbmin,vbsz=B._frame(v); cs=v['content_scale']

# tuned layout params
VKS = 0.378      # centered valknut scale
TXT = 27         # EST./2020 text size
SR  = 182        # radius of the EST./2020 side text
BCY = 226.5      # valknut vertical anchor (raised so its bottom-heavy centroid reads centered)

def _cwrap(body): return f'<g transform="translate({C},{C}) scale({cs}) translate({-C},{-C})">{body}</g>'

def _mask():
    """Red art (rings + weapons + centered valknut) as black-on-white, weave gaps WHITE (=holes)."""
    INK='#000'; GAP='#fff'
    rings=(f'<circle cx="{C}" cy="{C}" r="{R_OUT}" fill="none" stroke="{INK}" stroke-width="{W}"/>'
           f'<circle cx="{C}" cy="{C}" r="{R_IN}" fill="none" stroke="{INK}" stroke-width="{W}"/>')
    weap,fixes=B._weapons_and_fixes(v,INK,GAP,INK,GAP)
    cvk=vk.group(INK,f'translate({C},{C}) scale({VKS},{VKS}) translate({-bcx},{-BCY})',gap=B.VK_GAP,gapcolor=GAP)
    body=_cwrap(f'{rings}{cvk}{weap}{fixes}')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vbmin:.2f} {vbmin:.2f} {vbsz:.2f} {vbsz:.2f}" '
            f'width="{vbsz}" height="{vbsz}"><rect x="{vbmin:.2f}" y="{vbmin:.2f}" width="{vbsz:.2f}" height="{vbsz:.2f}" fill="#fff"/>{body}</svg>')

def _trace(N=2800,eps=0.7):
    png=cairosvg.svg2png(bytestring=_mask().encode(),output_width=N,output_height=N,background_color='white')
    arr=cv2.imdecode(np.frombuffer(png,np.uint8),cv2.IMREAD_GRAYSCALE)
    fg=(arr<128).astype(np.uint8)*255
    cnts,_=cv2.findContours(fg,cv2.RETR_CCOMP,cv2.CHAIN_APPROX_SIMPLE)
    sc=vbsz/N; subs=[]
    for cnt in cnts:
        if cv2.contourArea(cnt)<4: continue
        ap=cv2.approxPolyDP(cnt,eps,True).reshape(-1,2)
        if len(ap)<3: continue
        subs.append('M'+' L'.join(f'{vbmin+x*sc:.2f},{vbmin+y*sc:.2f}' for x,y in ap)+' Z')
    return ' '.join(subs)

def build():
    """Full logo SVG: red-only, transparent background, weave gaps as holes."""
    art=_trace()
    fin=TP.arc_text('FINIK',158,70,v['ls_fin'],'top',C,C,RED,font=VF)
    forge=TP.arc_text('FORGE',206,70,v['ls_forge'],'bottom',C,C,RED,font=VF)
    est=TP.number_path('EST.',TXT,C-SR,C,RED); yr=TP.number_path('2020',TXT,C+SR,C,RED)
    txt=_cwrap(f'{fin}{forge}{est}{yr}')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vbmin:.2f} {vbmin:.2f} {vbsz:.2f} {vbsz:.2f}" '
            f'width="620" height="620"><g fill="{RED}" fill-rule="evenodd"><path d="{art}"/></g>{txt}</svg>')

if __name__=='__main__':
    os.makedirs('logo',exist_ok=True)
    svg=build()
    open('logo/finikforge_logo.svg','w').write(svg)                                                     # vector master (transparent)
    cairosvg.svg2png(bytestring=svg.encode(),write_to='logo/finikforge_logo.png',output_width=1600)     # transparent PNG
    cairosvg.svg2png(bytestring=svg.encode(),write_to='logo/finikforge_logo_black.png',output_width=800,background_color='#000000')  # demo
    cairosvg.svg2eps(bytestring=svg.encode(),write_to='logo/finikforge_logo.eps')                       # print
    cairosvg.svg2pdf(bytestring=svg.encode(),write_to='logo/finikforge_logo.pdf')
    cairosvg.svg2pdf(bytestring=svg.encode(),write_to='logo/finikforge_logo.ai')                        # PDF-compatible AI
    print('logo written to ./logo/ (svg, transparent png, black demo, eps, pdf, ai)')
