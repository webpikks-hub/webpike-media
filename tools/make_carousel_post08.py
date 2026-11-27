# Karusel 1080x1350: "Kam Instagram – a më duhet edhe uebfaqe?" (Webpikë)
import os, sys
from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1350
HERE = os.path.dirname(os.path.abspath(__file__))
FD = os.path.join(HERE, "fonts", "SpaceGrotesk%5Bwght%5D.ttf")
FB = os.path.join(HERE, "fonts", "PlusJakartaSans%5Bwght%5D.ttf")
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "..", "images", "post-08")

SURF = (250, 248, 244); INK = (20, 22, 26); MUTED = (91, 96, 104); GREY = (163, 167, 174)
PIKA = (255, 90, 31); DETI = (14, 124, 107); LINE = (228, 224, 216); LIGHT = (243, 241, 236); WHITE = (255, 255, 255)

def font(path, size, wght):
    f = ImageFont.truetype(path, size)
    try: f.set_variation_by_axes([wght])
    except Exception: pass
    return f

F_HUGE = font(FD, 112, 700); F_BIG = font(FD, 88, 700); F_TITLE = font(FD, 84, 700); F_MED = font(FD, 54, 700)
F_NUM = font(FD, 220, 700); F_BODY = font(FB, 46, 500); F_SMALL = font(FB, 34, 700); F_TAG = font(FD, 36, 700)
F_CHIP = font(FB, 36, 700)

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
    logo(d, 150, H-110, F_TAG, LIGHT if dark else INK)
    s = f"{i}/{n}"
    d.text((W-90-d.textlength(s, font=F_SMALL), H-104), s, font=F_SMALL, fill=GREY if dark else MUTED)

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


def x_mark(d, cx, cy, r, col):
    d.ellipse([cx-r, cy-r, cx+r, cy+r], fill=col)
    k = r*0.42
    d.line([(cx-k, cy-k), (cx+k, cy+k)], fill=WHITE, width=max(5, int(r/5)))
    d.line([(cx-k, cy+k), (cx+k, cy-k)], fill=WHITE, width=max(5, int(r/5)))

def v_mark(d, cx, cy, r, col):
    d.ellipse([cx-r, cy-r, cx+r, cy+r], fill=col)
    w = max(5, int(r/5))
    d.line([(cx-r*0.45, cy+r*0.02), (cx-r*0.1, cy+r*0.38), (cx+r*0.48, cy-r*0.35)], fill=WHITE, width=w, joint="curve")

# ikona: profili social (grid postimesh) / globi (uebfaqe)
def icon_social(d, cx, cy):
    d.rounded_rectangle([cx-120, cy-150, cx+120, cy+150], radius=36, fill=WHITE, outline=INK, width=8)
    d.ellipse([cx-90, cy-125, cx-40, cy-75], fill=PIKA)
    d.line([(cx-25, cy-108), (cx+80, cy-108)], fill=INK, width=10)
    d.line([(cx-25, cy-86), (cx+40, cy-86)], fill=GREY, width=8)
    for r in range(3):
        for c in range(3):
            x0 = cx-90 + c*62; y0 = cy-45 + r*62
            d.rounded_rectangle([x0, y0, x0+54, y0+54], radius=8, fill=LINE if (r+c)%2 else (255, 214, 196))
    x_mark(d, cx+120, cy+130, 46, INK)

def icon_google(d, cx, cy):
    d.rounded_rectangle([cx-160, cy-60, cx+160, cy+60], radius=60, fill=WHITE, outline=INK, width=8)
    d.ellipse([cx-130, cy-28, cx-74, cy+28], outline=INK, width=9)
    d.line([(cx-82, cy+20), (cx-58, cy+44)], fill=INK, width=11)
    d.line([(cx-40, cy), (cx+120, cy)], fill=MUTED, width=10)
    # rezultat poshtë
    d.rounded_rectangle([cx-160, cy+90, cx+160, cy+170], radius=20, fill=DETI)
    d.line([(cx-130, cy+130), (cx+60, cy+130)], fill=WHITE, width=12)
    d.ellipse([cx+100, cy+112, cx+136, cy+148], fill=PIKA)
    d.rounded_rectangle([cx-160, cy-170, cx+40, cy-110], radius=18, fill=LINE)
    d.line([(cx-140, cy-140), (cx+20, cy-140)], fill=GREY, width=10)

def icon_info(d, cx, cy):
    d.rounded_rectangle([cx-95, cy-165, cx+95, cy+165], radius=36, fill=INK)
    d.rounded_rectangle([cx-78, cy-135, cx+78, cy+135], radius=20, fill=WHITE)
    rows = [PIKA, DETI, PIKA]
    for k, c in enumerate(rows):
        y = cy-105 + k*80
        d.ellipse([cx-62, y, cx-22, y+40], fill=c)
        d.line([(cx-8, y+14), (cx+58, y+14)], fill=INK, width=9)
        d.line([(cx-8, y+32), (cx+30, y+32)], fill=GREY, width=7)

ITEMS = [
    ("Rrjetet sociale nuk janë të tuat", "Algoritmi vendos kush e sheh postimin tënd. Uebfaqja është 100% e jotja — askush s'ta fsheh.", icon_social),
    ("Google s'i lexon story-t", "Kur dikush kërkon “restorant në Prishtinë”, Google shfaq uebfaqe — jo postimet e javës së kaluar.", icon_google),
    ("Klienti do info, jo scroll", "Menyja, orari, lokacioni e rezervimi në një vend — pa kërkuar nëpër 200 postime.", icon_info),
]
N = len(ITEMS) + 3

def slide_hook():
    img, d = base(True)
    for k in range(2):
        cx = M + 22 + k*64; d.ellipse([cx-22, 290-22, cx+22, 290+22], fill=PIKA)
    y = lines_draw(d, ["Ke Instagram.", "A të duhet", "edhe uebfaqe?"], F_HUGE, M, 370, LIGHT, accent="uebfaqe?")
    d.text((M, y+40), "Përgjigjja e shkurtër: po.", font=F_BODY, fill=GREY)
    d.text((M, y+110), "Ja 3 arsye pse.", font=F_BODY, fill=GREY)
    d.text((M, y+200), "Rrëshqit  →", font=F_MED, fill=PIKA)
    footer(d, 1, N, True); return img

def slide_item(i, title, desc, icon):
    img, d = base(False)
    d.text((M-8, 170), f"0{i}", font=F_NUM, fill=PIKA)
    cx, cy = W - M - 190, 320
    d.ellipse([cx-190, cy-190, cx+190, cy+190], fill=LIGHT, outline=LINE, width=4)
    icon(d, cx, cy)
    y = 610
    y = lines_draw(d, wrap(d, title, F_TITLE, W-2*M), F_TITLE, M, y, INK, lh=1.08)
    d.line([(M, y+30), (M+160, y+30)], fill=PIKA, width=8)
    y += 90
    bl = wrap(d, desc, F_BODY, W-2*M-100)
    lh = int(F_BODY.size*1.45); ch = len(bl)*lh + 100
    d.rounded_rectangle([M, y, W-M, y+ch], radius=28, fill=WHITE, outline=LINE, width=3)
    ty = y + 50
    for ln in bl:
        d.text((M+50, ty), ln, font=F_BODY, fill=INK); ty += lh
    footer(d, i+1, N, False); return img

ROWS = [("Të gjen në Google", False, True), ("Menyja & orari në një vend", False, True),
        ("Nuk varet nga algoritmi", False, True), ("Duket profesionale", False, True),
        ("Postime & story ditore", True, True)]

def slide_compare():
    img, d = base(False)
    y = lines_draw(d, ["Vetëm Instagram", "vs. Instagram + uebfaqe"], F_MED, M, 150, INK, accent="uebfaqe")
    c1, c2 = 730, 900
    top = y + 50
    d.rounded_rectangle([c2-85, top-20, c2+85, top+90+len(ROWS)*150], radius=40, fill=(225, 242, 238))
    hd = font(FB, 28, 700)
    for cx, t1, t2, col in [(c1, "Vetëm", "IG", MUTED), (c2, "IG +", "Ueb", DETI)]:
        d.text((cx-d.textlength(t1, font=hd)/2, top), t1, font=hd, fill=col)
        d.text((cx-d.textlength(t2, font=hd)/2, top+34), t2, font=hd, fill=col)
    ry = top + 110
    for label, a, b in ROWS:
        d.line([(M, ry-30), (W-M, ry-30)], fill=LINE, width=3)
        ll = wrap(d, label, font(FB, 40, 600), 520)
        fy = ry + 45 - len(ll)*26
        for ln in ll:
            d.text((M, fy), ln, font=font(FB, 40, 600), fill=INK); fy += 52
        (v_mark if a else x_mark)(d, c1, ry+45, 36, DETI if a else (210, 80, 60))
        v_mark(d, c2, ry+45, 36, DETI)
        ry += 150
    footer(d, N-1, N, False); return img

def slide_cta():
    img, d = base(True)
    logo(d, W/2, 260, font(FD, 150, 700), LIGHT)
    y = 520
    for ln in ["Mbaje Instagramin.", "Shtoja uebfaqen."]:
        tw = d.textlength(ln, font=F_BIG); d.text(((W-tw)/2, y), ln, font=F_BIG, fill=LIGHT); y += 100
    sub = "Ne ndërtojmë uebfaqe për restorante & biznese lokale në Kosovë — të lidhura me rrjetet e tua sociale."
    y += 30
    for ln in wrap(d, sub, F_BODY, W-2*M-40):
        tw = d.textlength(ln, font=F_BODY); d.text(((W-tw)/2, y), ln, font=F_BODY, fill=GREY); y += 64
    bt = "Na shkruaj në DM"; bw = d.textlength(bt, font=F_MED)
    bx = (W-bw)/2 - 60; by = y + 90
    d.rounded_rectangle([bx, by, bx+bw+120, by+120], radius=60, fill=PIKA)
    d.text((bx+60, by+28), bt, font=F_MED, fill=WHITE)
    d.text(((W-d.textlength("@webpike", font=F_SMALL))/2, by+170), "@webpike", font=F_SMALL, fill=GREY)
    return img

M = 90
os.makedirs(OUT, exist_ok=True)
slides = [slide_hook()] + [slide_item(i+1, *it) for i, it in enumerate(ITEMS)] + [slide_compare(), slide_cta()]
for i, s in enumerate(slides, 1):
    p = os.path.join(OUT, f"webpike-post-08-slide-{i}.jpg"); s.save(p, "JPEG", quality=92); print(p)
