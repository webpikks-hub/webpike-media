# Karusel 1080x1350: "3 mite për uebfaqet" (Webpikë)
import os, sys
from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1350
HERE = os.path.dirname(os.path.abspath(__file__))
FD = os.path.join(HERE, "fonts", "SpaceGrotesk%5Bwght%5D.ttf")
FB = os.path.join(HERE, "fonts", "PlusJakartaSans%5Bwght%5D.ttf")
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "..", "images", "post-02")

SURF = (250, 248, 244); INK = (20, 22, 26); MUTED = (91, 96, 104)
PIKA = (255, 90, 31); DETI = (14, 124, 107); LINE = (228, 224, 216); LIGHT = (243, 241, 236)

def font(path, size, wght):
    f = ImageFont.truetype(path, size)
    try: f.set_variation_by_axes([wght])
    except Exception: pass
    return f

F_HUGE = font(FD, 118, 700); F_BIG = font(FD, 88, 700); F_MED = font(FD, 54, 700)
F_BODY = font(FB, 44, 500); F_TRUTH = font(FB, 52, 500); F_MYTH = font(FD, 100, 700); F_SMALL = font(FB, 34, 700); F_TAG = font(FD, 36, 700)

def wrap(d, text, f, maxw):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if d.textlength(t, font=f) <= maxw: cur = t
        else: lines.append(cur); cur = w
    if cur: lines.append(cur)
    return lines

def base(dark):
    img = Image.new("RGB", (W, H), INK if dark else SURF)
    d = ImageDraw.Draw(img)
    col = (44, 47, 53) if dark else LINE
    for y in range(54, H, 72):
        for x in range(54, W, 72):
            d.ellipse([x-3, y-3, x+3, y+3], fill=col)
    return img, d

def logo(d, cx, y, f, color):
    word = "Webpik"; wlen = d.textlength(word + "e", font=f); x = cx - wlen/2
    d.text((x, y), word + "e", font=f, fill=color)
    ex = x + d.textlength(word, font=f); ew = d.textlength("e", font=f)
    r = f.size*0.07; top = y + f.size*0.18
    for k in (-1, 1):
        dx = ex + ew/2 + k*ew*0.22
        d.ellipse([dx-r, top-r, dx+r, top+r], fill=PIKA)

def footer(d, i, n, dark):
    fg = (163, 167, 174) if dark else MUTED
    logo(d, 150, H-110, F_TAG, LIGHT if dark else INK)
    s = f"{i}/{n}"
    d.text((W-90-d.textlength(s, font=F_SMALL), H-104), s, font=F_SMALL, fill=fg)

def lines_draw(d, lines, f, x, y, color, accent=None, lh=1.1):
    for ln in lines:
        if accent and accent in ln:
            pre, post = ln.split(accent, 1)
            d.text((x, y), pre, font=f, fill=color); px = x + d.textlength(pre, font=f)
            d.text((px, y), accent, font=f, fill=PIKA)
            d.text((px + d.textlength(accent, font=f), y), post, font=f, fill=color)
        else:
            d.text((x, y), ln, font=f, fill=color)
        y += f.size*lh
    return y

M = 90; N = 5
MYTHS = [
    ("“Mjafton Instagrami.”",
     "Klientët e rinj të kërkojnë në Google. Uebfaqja të nxjerr aty ku po kërkojnë — me menynë, orarin dhe lokacionin."),
    ("“Uebfaqja është për bizneset e mëdha.”",
     "Pikërisht restorantet dhe bizneset lokale fitojnë më shumë: një faqe e thjeshtë punon për ty 24/7."),
    ("“S’kam kohë të merrem me të.”",
     "Ti merresh me biznesin. Ne e ndërtojmë uebfaqen gati — të pastër, të shpejtë dhe të bukur në telefon."),
]

def slide_hook():
    img, d = base(True)
    for k in range(2):
        cx = M + 22 + k*64; d.ellipse([cx-22, 300-22, cx+22, 300+22], fill=PIKA)
    y = lines_draw(d, ["3 mite që e", "mbajnë biznesin", "tënd pa", "uebfaqe"], F_HUGE, M, 380, LIGHT, accent="uebfaqe")
    d.text((M, y+40), "A po beson edhe ti njërën prej tyre?", font=F_BODY, fill=(163,167,174))
    d.text((M, y+120), "Rrëshqit  →", font=F_MED, fill=PIKA)
    footer(d, 1, N, True); return img

def slide_myth(i, myth, truth):
    img, d = base(False)
    ml = wrap(d, myth, F_MYTH, W-2*M)
    tl = wrap(d, truth, F_TRUTH, W-2*M-100)
    lh = int(F_TRUTH.size*1.4)
    ch = 150 + len(tl)*lh + 40
    total = 72 + 60 + len(ml)*F_MYTH.size*1.1 + 30 + 90 + ch
    top = (H - 160 - total)/2 + 20
    tag = f"MITI #{i}"; tw = d.textlength(tag, font=F_TAG)
    d.rounded_rectangle([M, top, M+tw+56, top+72], radius=36, fill=INK)
    d.text((M+28, top+12), tag, font=F_TAG, fill=LIGHT)
    y = lines_draw(d, ml, F_MYTH, M, top+132, INK)
    d.line([(M, y+30), (M+160, y+30)], fill=PIKA, width=8)
    cy = y + 90
    d.rounded_rectangle([M, cy, W-M, cy+ch], radius=28, fill=(255,255,255), outline=LINE, width=3)
    cx0, cy0 = M+80, cy+80
    d.ellipse([cx0-34, cy0-34, cx0+34, cy0+34], fill=DETI)
    d.line([(cx0-16, cy0+1), (cx0-4, cy0+15), (cx0+18, cy0-13)], fill=(255,255,255), width=8)
    d.text((M+140, cy+50), "E vërteta", font=F_MED, fill=DETI)
    ty = cy + 160
    for ln in tl:
        d.text((M+50, ty), ln, font=F_TRUTH, fill=INK); ty += lh
    footer(d, i+1, N, False); return img

def slide_cta():
    img, d = base(True)
    logo(d, W/2, 300, font(FD, 150, 700), LIGHT)
    y = 560
    for ln in ["Gati për uebfaqen", "e biznesit tënd?"]:
        tw = d.textlength(ln, font=F_BIG); d.text(((W-tw)/2, y), ln, font=F_BIG, fill=LIGHT); y += 100
    sub = "Uebfaqe për restorante & biznese lokale në Kosovë"
    for ln in wrap(d, sub, F_BODY, W-2*M-40):
        tw = d.textlength(ln, font=F_BODY); d.text(((W-tw)/2, y+40), ln, font=F_BODY, fill=(163,167,174)); y += 60
    bt = "Na shkruaj në DM"; bw = d.textlength(bt, font=F_MED)
    bx = (W-bw)/2 - 60; by = y + 110
    d.rounded_rectangle([bx, by, bx+bw+120, by+120], radius=60, fill=PIKA)
    d.text((bx+60, by+28), bt, font=F_MED, fill=(255,255,255))
    d.text(((W-d.textlength("@webpike", font=F_SMALL))/2, by+170), "@webpike", font=F_SMALL, fill=(163,167,174))
    return img

os.makedirs(OUT, exist_ok=True)
slides = [slide_hook()] + [slide_myth(i+1, m, t) for i, (m, t) in enumerate(MYTHS)] + [slide_cta()]
for i, s in enumerate(slides, 1):
    p = os.path.join(OUT, f"webpike-post-02-slide-{i}.jpg"); s.save(p, "JPEG", quality=92); print(p)
