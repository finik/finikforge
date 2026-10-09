# top valknut group from uploaded svg (g4046), inner group translate(-371.95,-602.41)
INNER_T="translate(-371.95,-602.41)"
PATHS=[
 "m904.64 970.23-34.05-57.39h-177.4l48.349-82.486-32.12-57.1-112.07 196.98z",
 "m786.91 643.91-32.677 58.183 83.914 147-97.609-0.62816-33.395 56.378 228.63-1.4434z",
 "m557.09 906.42 66.726-0.79259 85.924-148.65 47.261 83.114 65.522 0.73205-114.56-195.54z",
]
def group(fill, extra_transform="", gap=0, gapcolor="#0e0e0e"):
    st=f'stroke="{gapcolor}" stroke-width="{gap}" stroke-linejoin="round"' if gap else ''
    ps="".join(f'<path d="{d}" fill="{fill}" {st}/>' for d in PATHS)
    return f'<g transform="{extra_transform}"><g transform="{INNER_T}">{ps}</g></g>'
