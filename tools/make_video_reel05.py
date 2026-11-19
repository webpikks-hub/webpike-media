"""Webpikë Reel 05 – "Para → Pas": all Webpikë services (motion graphics, 1080x1920, 24 s).

Before: no website, messy Instagram, not on Google Maps, ugly logo, unanswered DMs.
After: Logo & identity, Website, Instagram design, Google Maps, Marketing AI automation.
The demo business "Luna" is fictional. Usage: python3 make_video_reel05.py OUT.mp4 [FRAMES_DIR times] [--only-frames]
"""
import math, random, subprocess, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS, SS = 1080, 1920, 30, 2
SCENES = [(0, 2.5), (2.5, 7.5), (7.5, 8.5), (8.5, 10.5), (10.5, 12.5), (12.5, 14.5), (14.5, 16.5), (16.5, 18.5),
          (18.5, 21.0), (21.0, 24.0)]
DUR = 24.0
CUTS = [a for a, _ in SCENES[1:]]
ARGS = [a for a in sys.argv[1:] if not a.startswith("--")]
OUT = ARGS[0] if ARGS else "reel05.mp4"

FD = "/home/claude/webpike-media/tools/fonts/SpaceGrotesk%5Bwght%5D.ttf"
FB = "/home/claude/webpike-media/tools/fonts/PlusJakartaSans%5Bwght%5D.ttf"
UGLY = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"

INK = (20, 22, 26); BLACK = (10, 11, 13); PIKA = (255, 90, 31); CREAM = (250, 248, 244); DETI = (14, 124, 107)
MUTED = (120, 125, 133); LINE = (228, 224, 216); WHITE = (255, 255, 255); RED = (225, 52, 48); LIGHT = (243, 241, 236)

_fc = {}


def F(path, size, wght=600):
    k = (path, size, wght)
    if k not in _fc:
        f = ImageFont.truetype(path, int(size * SS))
        try:
            f.set_variation_by_axes([wght])
        except Exception:
            pass
        _fc[k] = f
    return _fc[k]


def S(v):
    return v * SS


def B(x0, y0, x1, y1):
    return [x0 * SS, y0 * SS, x1 * SS, y1 * SS]


def ease(t):
    t = max(0.0, min(1.0, t)); return 1 - (1 - t) ** 3


def back(t, s=1.7):
    t = max(0.0, min(1.0, t)); t -= 1; return t * t * ((s + 1) * t + s) + 1


def mix(c1, c2, p):
    return tuple(int(a + (b - a) * p) for a, b in zip(c1, c2))


def tc(d, x, y, s, f, fill):
    """centered text at base coords."""
    d.text((S(x) - d.textlength(s, font=f) / 2, S(y)), s, font=f, fill=fill)


# ---------------------------------------------------------------- backgrounds
_bg = {}


def background(kind):
    if kind in _bg:
        return _bg[kind].copy()
    dark = kind != "light"
    img = Image.new("RGB", (S(W), S(H)), BLACK if dark else CREAM)
    if kind in ("glow", "glow2"):
        g = Image.new("L", (W // 2, H // 2), 0)
        ImageDraw.Draw(g).ellipse([270 - 300, 480 - 300 + (60 if kind == "glow2" else 0), 270 + 300, 480 + 300], fill=255)
        g = g.filter(ImageFilter.GaussianBlur(140)).resize(img.size).point(lambda v: int(v * 0.42))
        img = Image.composite(Image.new("RGB", img.size, (120, 40, 8)), img, g)
    d = ImageDraw.Draw(img)
    col = (32, 34, 40) if dark else LINE
    for y in range(60, H, 72):
        for x in range(60, W, 72):
            d.ellipse(B(x - 3, y - 3, x + 3, y + 3), fill=col)
    _bg[kind] = img
    return img.copy()


def paste_layer(img, layer, cx, cy, p=1.0, rot=0.0, alpha=1.0):
    if p <= 0.01 or alpha <= 0.01:
        return
    L = layer
    if p != 1.0:
        L = L.resize((max(2, int(L.size[0] * p)), max(2, int(L.size[1] * p))), Image.BICUBIC)
    if rot:
        L = L.rotate(rot, resample=Image.BICUBIC, expand=True)
    if alpha < 1:
        a = L.getchannel("A").point(lambda v: int(v * alpha)); L = L.copy(); L.putalpha(a)
    img.paste(L, (int(S(cx) - L.size[0] / 2), int(S(cy) - L.size[1] / 2)), L)


def new_layer(w, h):
    L = Image.new("RGBA", (S(w), S(h)), (0, 0, 0, 0)); return L, ImageDraw.Draw(L)


def shadow_card(w, h, fill=WHITE, r=34, outline=None):
    L, d = new_layer(w + 40, h + 40)
    sh = Image.new("L", L.size, 0)
    ImageDraw.Draw(sh).rounded_rectangle(B(24, 30, w + 16, h + 26), radius=S(r), fill=120)
    sh = sh.filter(ImageFilter.GaussianBlur(S(10)))
    L.paste(Image.new("RGBA", L.size, (0, 0, 0, 255)), (0, 0), sh)
    d.rounded_rectangle(B(20, 20, w + 20, h + 20), radius=S(r), fill=fill, outline=outline, width=S(3) if outline else 0)
    return L, d


def star(d, cx, cy, r, fill):
    pts = []
    for i in range(10):
        a = -math.pi / 2 + i * math.pi / 5
        rr = r if i % 2 == 0 else r * 0.45
        pts.append((S(cx + math.cos(a) * rr), S(cy + math.sin(a) * rr)))
    d.polygon(pts, fill=fill)


def check(d, cx, cy, r, bg=DETI):
    d.ellipse(B(cx - r, cy - r, cx + r, cy + r), fill=bg)
    d.line([(S(cx - r * 0.45), S(cy + r * 0.02)), (S(cx - r * 0.1), S(cy + r * 0.38)), (S(cx + r * 0.5), S(cy - r * 0.35))],
           fill=WHITE, width=int(S(r * 0.24)), joint="curve")


def xmark(d, cx, cy, r):
    d.ellipse(B(cx - r, cy - r, cx + r, cy + r), fill=RED)
    k = r * 0.42
    for s in (1, -1):
        d.line([(S(cx - k), S(cy - k * s)), (S(cx + k), S(cy + k * s))], fill=WHITE, width=int(S(r * 0.24)))


# ---------------------------------------------------------------- BEFORE layers (cached)
_L = {}


def cached(name, fn):
    if name not in _L:
        _L[name] = fn()
    return _L[name]


def L_search():
    L, d = shadow_card(820, 330)
    d.rounded_rectangle(B(60, 60, 800, 150), radius=S(45), fill=(244, 244, 246), outline=(220, 220, 225), width=S(3))
    d.ellipse(B(92, 86, 126, 120), outline=MUTED, width=S(5)); d.line([(S(121), S(115)), (S(136), S(130))], fill=MUTED, width=S(5))
    d.text((S(156), S(80)), "lokali luna prishtinë", font=F(FB, 38, 600), fill=INK)
    d.text((S(64), S(190)), "Nuk u gjet asnjë uebfaqe.", font=F(FB, 42, 800), fill=RED)
    d.rounded_rectangle(B(64, 268, 600, 284), radius=S(8), fill=(225, 225, 228))
    d.rounded_rectangle(B(64, 300, 480, 314), radius=S(8), fill=(235, 235, 238))
    return L


def L_insta_bad():
    L, d = shadow_card(560, 780)
    d.ellipse(B(56, 56, 176, 176), fill=(205, 205, 210))
    d.ellipse(B(96, 78, 136, 118), fill=(240, 240, 242)); d.chord(B(76, 116, 156, 196), 180, 360, fill=(240, 240, 242))
    for i, (n, l) in enumerate((("14", "postime"), ("63", "ndjekës"), ("410", "ndjek"))):
        tc(d, 260 + i * 120, 80, n, F(FB, 36, 800), INK)
        tc(d, 260 + i * 120, 124, l, F(FB, 22, 500), MUTED)
    d.text((S(60), S(200)), "luna_lokali_2019", font=F(FB, 32, 700), fill=INK)
    d.text((S(60), S(244)), "(pa përshkrim)", font=F(FB, 26, 500), fill=(170, 170, 175))
    rnd = random.Random(4)
    grid = Image.new("RGB", (S(500), S(500)), (235, 235, 235))
    gd = ImageDraw.Draw(grid)
    cols = [(150, 140, 120), (90, 100, 110), (200, 180, 60), (120, 70, 140), (70, 120, 60), (180, 90, 90), (60, 60, 70),
            (210, 200, 190), (130, 160, 200)]
    for i in range(9):
        r, c = divmod(i, 3)
        x0, y0 = c * 167, r * 167
        gd.rectangle(B(x0 + 2, y0 + 2, x0 + 165, y0 + 165), fill=cols[i])
        if i in (1, 5, 7):  # random clip-art / text-y junk
            gd.ellipse(B(x0 + 40, y0 + 40, x0 + 120, y0 + 120), fill=(240, 220, 60))
        if i in (2, 6):
            gd.line([(S(x0 + 20), S(y0 + 20)), (S(x0 + 150), S(y0 + 140))], fill=(255, 255, 255), width=S(8))
    grid = grid.filter(ImageFilter.GaussianBlur(S(4)))
    L.paste(grid, (S(50), S(300)))
    return L


def L_maps_bad():
    L, d = shadow_card(480, 400)
    d.rounded_rectangle(B(40, 40, 480, 300), radius=S(22), fill=(226, 230, 222))
    for k in range(5):
        d.line([(S(40), S(80 + k * 50)), (S(480), S(60 + k * 55))], fill=WHITE, width=S(10))
    d.line([(S(200), S(40)), (S(260), S(300))], fill=WHITE, width=S(14))
    d.ellipse(B(220, 120, 300, 200), fill=(170, 170, 175))
    d.polygon([(S(228), S(175)), (S(292), S(175)), (S(260), S(240))], fill=(170, 170, 175))
    tc(d, 260, 128, "?", F(FD, 54, 700), WHITE)
    d.text((S(50), S(328)), "Nuk shfaqet në hartë", font=F(FB, 34, 800), fill=RED)
    return L


def L_logo_bad():
    L, d = shadow_card(440, 280)
    f = ImageFont.truetype(UGLY, S(96))
    txt = Image.new("RGBA", (S(420), S(160)), (0, 0, 0, 0))
    td = ImageDraw.Draw(txt)
    cols = [(230, 40, 160), (40, 160, 230), (60, 200, 60), (250, 200, 0)]
    x = S(12)
    for i, ch in enumerate("LUNA"):
        td.text((x + S(5), S(16)), ch, font=f, fill=(0, 0, 0, 200))
        td.text((x, S(10)), ch, font=f, fill=cols[i])
        x += td.textlength(ch, font=f)
    txt = txt.resize((S(400), S(120))).rotate(-6, expand=True, resample=Image.BICUBIC)
    L.paste(txt, (S(30), S(70)), txt)
    return L


def L_dm_bad():
    L, d = shadow_card(560, 200)
    d.ellipse(B(54, 64, 144, 154), fill=(255, 235, 230))
    d.rounded_rectangle(B(74, 88, 124, 124), radius=S(8), outline=RED, width=S(5))
    d.polygon([(S(84), S(124)), (S(84), S(140)), (S(100), S(124))], fill=RED)
    d.text((S(170), S(70)), "3 mesazhe pa përgjigje", font=F(FB, 34, 800), fill=INK)
    d.text((S(170), S(118)), "Klientët prisnin… 2 ditë", font=F(FB, 28, 600), fill=RED)
    return L


# ---------------------------------------------------------------- AFTER layers
def logo_mark(d, cx, cy, s, dark_bg=True):
    """fictional demo brand: 'luna' + orange crescent."""
    img = d._image
    x0, y0 = int(S(cx - 62 * s)), int(S(cy - 62 * s))
    sz = int(S(124 * s)) + 1
    m = Image.new("L", (sz, sz), 0)
    md = ImageDraw.Draw(m)
    o = lambda a, b, c, e: [S(a * s), S(b * s), S(c * s), S(e * s)]
    md.ellipse(o(2, 2, 122, 122), fill=255)
    md.ellipse(o(32, -14, 142, 96), fill=0)
    img.paste(Image.new(img.mode, (sz, sz), PIKA if img.mode == "RGB" else PIKA + (255,)), (x0, y0), m)


def L_logo_good():
    L, d = new_layer(760, 520)
    logo_mark(d, 210, 150, 1.0)
    d.text((S(300), S(84)), "luna", font=F(FD, 130, 700), fill=LIGHT)
    d.text((S(306), S(232)), "RESTORANT · PRISHTINË", font=F(FB, 26, 700), fill=MUTED)
    for i, c in enumerate([PIKA, (255, 190, 140), LIGHT, (40, 42, 48)]):
        d.ellipse(B(150 + i * 120, 330, 240 + i * 120, 420), fill=c, outline=(70, 72, 78), width=S(3))
    d.text((S(640), S(340)), "Aa", font=F(FD, 64, 700), fill=LIGHT)
    return L


def site_layer(w, h, mobile=False):
    img = Image.new("RGB", (S(w), S(h)), (14, 15, 18))
    d = ImageDraw.Draw(img); u = S(w) / 100
    if not mobile:
        d.rectangle([0, 0, S(w), 8 * u], fill=(22, 23, 27))
        d.ellipse([3 * u, 2 * u, 7 * u, 6 * u], fill=PIKA)
        d.text((8.5 * u, 1.6 * u), "luna", font=F(FD, w * 0.03, 700), fill=LIGHT)
        for i, s in enumerate(["Menyja", "Rezervo", "Kontakti"]):
            d.text((60 * u + i * 12 * u, 2.4 * u), s, font=F(FB, w * 0.018, 600), fill=(170, 170, 175))
        d.text((6 * u, 15 * u), "Shije që", font=F(FD, w * 0.06, 700), fill=LIGHT)
        d.text((6 * u, 23 * u), "të kthen sërish.", font=F(FD, w * 0.06, 700), fill=PIKA)
        d.rounded_rectangle([6 * u, 36 * u, 26 * u, 42 * u], radius=3 * u, fill=PIKA)
        d.text((8.6 * u, 37.2 * u), "Rezervo tavolinë", font=F(FB, w * 0.017, 800), fill=INK)
        d.rounded_rectangle([28 * u, 36 * u, 42 * u, 42 * u], radius=3 * u, outline=(200, 200, 200), width=max(1, int(0.3 * u)))
        d.text((30.4 * u, 37.2 * u), "Menyja", font=F(FB, w * 0.017, 700), fill=LIGHT)
        d.ellipse([56 * u, 10 * u, 94 * u, 48 * u], fill=(40, 30, 26))
        d.ellipse([60 * u, 14 * u, 90 * u, 44 * u], fill=(250, 240, 228))
        d.ellipse([66 * u, 20 * u, 84 * u, 38 * u], fill=PIKA)
        d.ellipse([70 * u, 24 * u, 77 * u, 31 * u], fill=(255, 180, 120))
        for i in range(4):
            x0 = 6 * u + i * 22.5 * u
            d.rounded_rectangle([x0, 52 * u, x0 + 20 * u, 60 * u + 0], radius=2 * u, fill=(26, 27, 32))
            d.ellipse([x0 + 7 * u, 53.5 * u, x0 + 13 * u, 59.5 * u], fill=[PIKA, (255, 160, 100), (240, 120, 60), (255, 200, 150)][i])
    else:
        d.rectangle([0, 0, S(w), 12 * u], fill=(22, 23, 27))
        d.ellipse([6 * u, 3.5 * u, 11 * u, 8.5 * u], fill=PIKA)
        d.text((14 * u, 2.4 * u), "luna", font=F(FD, w * 0.07, 700), fill=LIGHT)
        d.ellipse([18 * u, 18 * u, 82 * u, 82 * u], fill=(250, 240, 228))
        d.ellipse([30 * u, 30 * u, 70 * u, 70 * u], fill=PIKA)
        d.text((8 * u, 90 * u), "Shije që", font=F(FD, w * 0.1, 700), fill=LIGHT)
        d.text((8 * u, 103 * u), "të kthen.", font=F(FD, w * 0.1, 700), fill=PIKA)
        d.rounded_rectangle([8 * u, 122 * u, 70 * u, 136 * u], radius=7 * u, fill=PIKA)
        d.text((14 * u, 124.6 * u), "Rezervo", font=F(FB, w * 0.065, 800), fill=INK)
    return img


def device(screen, frame_col=(26, 27, 31), border=None, radius=40, pad=18):
    w, h = screen.size
    L = Image.new("RGBA", (w + S(pad * 2), h + S(pad * 2)), (0, 0, 0, 0))
    d = ImageDraw.Draw(L)
    d.rounded_rectangle([0, 0, L.size[0] - 1, L.size[1] - 1], radius=S(radius), fill=frame_col, outline=border, width=S(4) if border else 0)
    m = Image.new("L", screen.size, 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, w - 1, h - 1], radius=S(radius * 0.6), fill=255)
    L.paste(screen, (S(pad), S(pad)), m)
    return L


def L_laptop():
    scr = device(site_layer(820, 512), radius=26, pad=20)
    L = Image.new("RGBA", (scr.size[0] + S(120), scr.size[1] + S(60)), (0, 0, 0, 0))
    L.paste(scr, (S(60), 0), scr)
    d = ImageDraw.Draw(L)
    y = scr.size[1]
    d.polygon([(S(40), y), (L.size[0] - S(40), y), (L.size[0], y + S(36)), (0, y + S(36))], fill=(56, 58, 64))
    d.rectangle([0, y + S(36), L.size[0], y + S(46)], fill=(36, 38, 42))
    return L


def insta_good(t_local):
    w, h = 560, 900
    scr = Image.new("RGB", (S(w), S(h)), (255, 255, 255))
    d = ImageDraw.Draw(scr)
    d.ellipse(B(36, 50, 156, 170), fill=PIKA)
    d.ellipse(B(44, 58, 148, 162), fill=BLACK)
    logo_mark(d, 96, 110, 0.55)
    k = ease(t_local / 1.2)
    stats = [(f"{int(48 * k)}", "postime"), (f"{1 + 1.4 * k:.1f}K", "ndjekës"), ("180", "ndjek")]
    for i, (n, l) in enumerate(stats):
        tc(d, 250 + i * 110, 74, n, F(FB, 34, 800), INK)
        tc(d, 250 + i * 110, 116, l, F(FB, 21, 500), MUTED)
    d.text((S(36), S(190)), "Luna · Restorant", font=F(FB, 30, 800), fill=INK)
    d.text((S(36), S(230)), "Pica e furrës me dru · Prishtinë", font=F(FB, 24, 500), fill=(70, 70, 75))
    d.text((S(36), S(264)), "Rezervo në DM", font=F(FB, 24, 700), fill=PIKA)
    for i, s in enumerate(["Menyja", "Oferta", "Rezervo", "Ne"]):
        cx = 80 + i * 130
        d.ellipse(B(cx - 46, 314, cx + 46, 406), outline=PIKA, width=S(5))
        d.ellipse(B(cx - 36, 324, cx + 36, 396), fill=[BLACK, PIKA, (255, 200, 160), BLACK][i])
        tc(d, cx, 414, s, F(FB, 20, 600), INK)
    top = 470
    for i in range(9):
        r, c = divmod(i, 3)
        x0, y0 = c * 187, top + r * 187
        p = ease((t_local - 0.15 - i * 0.07) / 0.35)
        if p <= 0:
            continue
        bgc = [BLACK, PIKA, CREAM][(r + c) % 3]
        d.rectangle(B(x0 + 2, y0 + 2, x0 + 185, y0 + 185), fill=mix(WHITE, bgc, p))
        cx, cy = x0 + 93, y0 + 93
        if (r + c) % 3 != 1:
            d.ellipse(B(cx - 52 * p, cy - 52 * p, cx + 52 * p, cy + 52 * p), fill=(250, 240, 228))
            d.ellipse(B(cx - 30 * p, cy - 30 * p, cx + 30 * p, cy + 30 * p), fill=PIKA)
        else:
            d.rounded_rectangle(B(x0 + 30, cy - 12, x0 + 155, cy + 4), radius=S(8), fill=mix(WHITE, BLACK, p))
            d.rounded_rectangle(B(x0 + 30, cy + 16, x0 + 120, cy + 30), radius=S(8), fill=mix(WHITE, BLACK, p * 0.6))
    return device(scr, frame_col=(18, 18, 20), border=PIKA, radius=48, pad=16)


def maps_good(t_local):
    L, d = new_layer(900, 980)
    d.rounded_rectangle(B(20, 20, 880, 660), radius=S(40), fill=(30, 33, 38))
    for k in range(6):
        d.line([(S(20), S(90 + k * 100)), (S(880), S(50 + k * 110))], fill=(48, 52, 60), width=S(16))
    for k in range(4):
        d.line([(S(150 + k * 220), S(20)), (S(110 + k * 230), S(660))], fill=(48, 52, 60), width=S(12))
    d.rounded_rectangle(B(560, 80, 760, 200), radius=S(20), fill=(26, 60, 50))
    # pin drop
    p = back((t_local - 0.1) / 0.5)
    py = 330 - (1 - p) * 300 if p > 0 else -999
    if p > 0:
        d.ellipse(B(400, 420, 500, 446), fill=(15, 16, 19))
        d.ellipse(B(390, py - 60, 510, py + 60), fill=PIKA)
        d.polygon([(S(398), S(py + 25)), (S(502), S(py + 25)), (S(450), S(py + 110))], fill=PIKA)
        d.ellipse(B(420, py - 30, 480, py + 30), fill=WHITE)
        rp = (t_local * 1.4) % 1
        d.ellipse(B(450 - 90 * rp - 20, 433 - 24 * rp - 6, 450 + 90 * rp + 20, 433 + 24 * rp + 6), outline=mix(PIKA, (30, 33, 38), rp), width=S(5))
    q = back((t_local - 0.6) / 0.45)
    if q > 0:
        card = Image.new("RGBA", (S(820), S(280)), (0, 0, 0, 0))
        cd = ImageDraw.Draw(card)
        cd.rounded_rectangle(B(0, 0, 820, 280), radius=S(32), fill=WHITE)
        cd.text((S(40), S(32)), "Luna · Restorant", font=F(FB, 44, 800), fill=INK)
        cd.text((S(40), S(96)), "4.9", font=F(FB, 38, 800), fill=INK)
        for i in range(5):
            star(cd, 140 + i * 46, 118, 20, (255, 180, 0))
        cd.text((S(380), S(98)), "(320 vlerësime)", font=F(FB, 30, 600), fill=MUTED)
        cd.text((S(40), S(170)), "Hapur tani", font=F(FB, 32, 800), fill=DETI)
        cd.text((S(250), S(170)), "· Rrugëtimi · Uebfaqja", font=F(FB, 32, 600), fill=MUTED)
        card = card.resize((max(2, int(card.size[0] * q)), max(2, int(card.size[1] * q))))
        L.paste(card, (int(S(450) - card.size[0] / 2), int(S(810) - card.size[1] / 2)), card)
    return L


def ai_chat(t_local):
    L, d = new_layer(900, 1000)
    d.rounded_rectangle(B(20, 20, 880, 980), radius=S(44), fill=(24, 25, 30))
    d.ellipse(B(60, 56, 140, 136), fill=PIKA); d.ellipse(B(68, 64, 132, 128), fill=BLACK); logo_mark(d, 100, 96, 0.33)
    d.text((S(164), S(62)), "luna.prishtina", font=F(FB, 34, 800), fill=LIGHT)
    d.text((S(164), S(104)), "Aktiv tani", font=F(FB, 24, 600), fill=(90, 200, 150))
    d.line([(S(20), S(170)), (S(880), S(170))], fill=(44, 46, 52), width=S(3))

    def bubble(y, text, mine, p):
        if p <= 0:
            return
        f = F(FB, 34, 600)
        tw = d.textlength(text, font=f) / SS
        bw, bh = tw + 64, 84
        x0 = 840 - bw if mine else 60
        yy = y + (1 - p) * 30
        d.rounded_rectangle(B(x0, yy, x0 + bw, yy + bh), radius=S(36), fill=PIKA if mine else (52, 54, 62))
        d.text((S(x0 + 32), S(yy + 20)), text, font=f, fill=INK if mine else LIGHT)

    bubble(220, "A keni tavolinë për sonte?", False, ease((t_local - 0.1) / 0.3))
    if 0.45 < t_local < 0.95:
        for i in range(3):
            a = 0.5 + 0.5 * math.sin(t_local * 14 - i)
            d.ellipse(B(760 + i * 30 - 9, 350 - 9 - a * 6, 760 + i * 30 + 9, 350 + 9 - a * 6), fill=PIKA)
    bubble(330, "Po! Për sa persona?", True, ease((t_local - 0.95) / 0.3))
    bubble(440, "Për 4, ora 20:00", False, ease((t_local - 1.25) / 0.3))
    bubble(550, "Gati! U rezervua.", True, ease((t_local - 1.55) / 0.3))
    p = back((t_local - 0.3) / 0.4)
    if p > 0:
        d.rounded_rectangle(B(60, 700, 840, 820), radius=S(30), fill=(36, 30, 26), outline=PIKA, width=S(3))
        d.rounded_rectangle(B(90, 730, 170, 790), radius=S(16), fill=PIKA)
        tc(d, 130, 736, "AI", F(FD, 38, 700), INK)
        d.text((S(200), S(736)), "Përgjigje automatike 24/7", font=F(FB, 36, 700), fill=LIGHT)
    q = ease((t_local - 0.7) / 0.4)
    if q > 0:
        d.text((S(70), S(860)), "Postime të planifikuara", font=F(FB, 30, 700), fill=MUTED)
        for i in range(7):
            on = i < int(1 + 6 * ease((t_local - 0.8) / 1.0))
            d.rounded_rectangle(B(70 + i * 110, 910, 160 + i * 110, 950), radius=S(12), fill=PIKA if on else (44, 46, 52))
    return L


# ---------------------------------------------------------------- scenes
def title_tag(img, tag, title, tl, tag_col=PIKA, dark=True, y=150):
    d = ImageDraw.Draw(img)
    p = back(tl / 0.4)
    if p <= 0:
        return
    f = F(FD, 38, 700)
    tw = d.textlength(tag, font=f) / SS
    x0 = 540 - (tw + 56) / 2
    yy = y - (1 - p) * 80
    d.rounded_rectangle(B(x0, yy, x0 + tw + 56, yy + 66), radius=S(33), fill=tag_col)
    d.text((S(x0 + 28), S(yy + 11)), tag, font=f, fill=INK if tag_col == PIKA else WHITE)
    ft = F(FD, 84, 700)
    tc(d, 540, yy + 92, title, ft, LIGHT if dark else INK)


def s_hook(t, tl):
    img = background("glow")
    d = ImageDraw.Draw(img)
    for i, (ln, col) in enumerate([("Biznesi yt", LIGHT), ("online duket", LIGHT), ("kështu?", PIKA)]):
        p = ease((tl - 0.1 - i * 0.18) / 0.4)
        if p <= 0:
            continue
        f = F(FD, 132, 700)
        d.text((S(90), S(620 + i * 150 + (1 - p) * 60)), ln, font=f, fill=mix(BLACK, col, p))
    p = ease((tl - 0.9) / 0.4)
    if p > 0:
        d.text((S(94), S(1110)), "Shiko deri në fund.", font=F(FB, 46, 600), fill=mix(BLACK, (160, 164, 170), p))
    # two brand dots
    for k in range(2):
        q = back((tl - k * 0.12) / 0.35)
        r = 24 * q
        d.ellipse(B(112 + k * 66 - r, 540 - r, 112 + k * 66 + r, 540 + r), fill=PIKA)
    return img


BEFORE = [("search", L_search, 540, 470, -2, 0.0), ("insta", L_insta_bad, 300, 1020, 4, 0.55),
          ("maps", L_maps_bad, 830, 880, -5, 1.1), ("logo", L_logo_bad, 790, 1290, 6, 1.6),
          ("dm", L_dm_bad, 560, 1560, -3, 2.1)]
XPOS = {"search": (860, 360), "insta": (520, 680), "maps": (1000, 730), "logo": (960, 1180), "dm": (790, 1480)}


def s_before(t, tl):
    img = background("light")
    jit = (math.sin(tl * 40) * 4, math.cos(tl * 37) * 3) if tl > 3.4 else (0, 0)
    for name, fn, x, y, rot, st in BEFORE:
        p = back((tl - st) / 0.35)
        if p <= 0:
            continue
        paste_layer(img, cached(name, fn), x + jit[0], y + jit[1], p * 0.92, rot)
    d = ImageDraw.Draw(img)
    for name, fn, x, y, rot, st in BEFORE:
        q = back((tl - st - 0.35) / 0.25, 2.5)
        if q > 0:
            cx, cy = XPOS[name]
            xmark(d, cx + jit[0], cy + jit[1], 46 * q)
    # top title
    d.rounded_rectangle(B(0, 0, W, 250), radius=0, fill=CREAM)
    title_tag(img, "PARA", "Pa prezencë online", tl, tag_col=RED, dark=False, y=110)
    # bottom punch line
    p = ease((tl - 3.3) / 0.4)
    if p > 0:
        d = ImageDraw.Draw(img)
        d.rounded_rectangle(B(70, 1720, 1010, 1850), radius=S(30), fill=mix(CREAM, INK, p))
        tc(d, 540, 1748, "Klientët shkojnë te konkurrenca.", F(FD, 50, 700), mix(CREAM, LIGHT, p))
    return img


def s_wipe(t, tl):
    # orange circle wipe from before-collage into black, then text
    p = ease(tl / 0.5)
    base = s_before(t, 5.0) if p < 1 else background("dark")
    d = ImageDraw.Draw(base)
    r = 2300 * p
    d.ellipse(B(540 - r, 960 - r, 540 + r, 960 + r), fill=PIKA)
    q = ease((tl - 0.35) / 0.4)
    if q > 0:
        r2 = 2300 * ease((tl - 0.45) / 0.5)
        if r2 > 0:
            dark = background("dark")
            m = Image.new("L", base.size, 0)
            ImageDraw.Draw(m).ellipse(B(540 - r2, 960 - r2, 540 + r2, 960 + r2), fill=255)
            base = Image.composite(dark, base, m)
        d = ImageDraw.Draw(base)
        f = F(FD, 120, 700)
        tc(d, 540, 760 + (1 - q) * 40, "Webpikë", f, mix(PIKA, LIGHT, q) if r2 > 0 else INK)
        tc(d, 540, 920 + (1 - q) * 40, "e rregullon.", F(FD, 96, 700), PIKA if r2 > 0 else INK)
    return base


SERVICES = ["Logo & identitet", "Uebfaqe", "Instagram profesional", "Google Maps", "Marketing me AI"]


def svc_header(img, i, tl):
    title_tag(img, f"PAS · {i + 1}/5", SERVICES[i], tl)


def s_logo(t, tl):
    img = background("glow2")
    bad = cached("logo", L_logo_bad)
    m = ease((tl - 0.45) / 0.4)
    if m < 1:
        paste_layer(img, bad, 540, 960, 1.2 * (1 - m * 0.3), 6 * (1 - m), alpha=1 - m)
    if m > 0:
        paste_layer(img, cached("logo_good", L_logo_good), 540, 990, 0.9 + 0.1 * back(m), 0, alpha=m)
    # sparkle burst at morph
    d = ImageDraw.Draw(img)
    if 0.45 < tl < 1.2:
        k = (tl - 0.45) / 0.75
        for j in range(14):
            a = j * math.tau / 14
            r1, r2 = 200 + 300 * k, 240 + 330 * k
            d.line([(S(540 + math.cos(a) * r1), S(960 + math.sin(a) * r1)), (S(540 + math.cos(a) * r2), S(960 + math.sin(a) * r2))],
                   fill=mix(PIKA, BLACK, k), width=S(6))
    svc_header(img, 0, tl)
    return img


def s_web(t, tl):
    img = background("glow2")
    p = ease(tl / 0.6)
    fl = math.sin(tl * 2.2) * 10
    paste_layer(img, cached("laptop", L_laptop), 520, 1000 + (1 - p) * 400 + fl, 0.98)
    q = back((tl - 0.35) / 0.5)
    if q > 0:
        ph = cached("phone_site", lambda: device(site_layer(250, 520, mobile=True), frame_col=(18, 18, 20), border=PIKA, radius=40, pad=14))
        paste_layer(img, ph, 880, 1260 - fl + (1 - q) * 300, q, -4)
    d = ImageDraw.Draw(img)
    for j, s in enumerate(["Hapet shpejt në telefon", "Menyja & rezervime online"]):
        r = ease((tl - 0.8 - j * 0.25) / 0.35)
        if r > 0:
            check(d, 130, 1590 + j * 90 + 26, 26)
            d.text((S(176), S(1590 + j * 90)), s, font=F(FB, 44, 700), fill=mix(BLACK, LIGHT, r))
    svc_header(img, 1, tl)
    return img


def s_insta(t, tl):
    img = background("glow2")
    p = back((tl - 0.05) / 0.5)
    paste_layer(img, insta_good(tl), 540, 1090 + math.sin(tl * 2) * 8, p * 0.95, 0)
    d = ImageDraw.Draw(img)
    for i in range(6):  # floating likes
        ht = (tl * 0.9 + i * 0.3) % 1.3
        x = 170 + (i % 2) * 740 + math.sin(ht * 5 + i) * 30
        y = 1500 - ht * 700
        r = 26 * (1 - ht / 1.4) + 8
        col = PIKA if i % 2 else (255, 140, 90)
        d.ellipse(B(x - r, y - r, x, y), fill=col); d.ellipse(B(x, y - r, x + r, y), fill=col)
        d.polygon([(S(x - r), S(y - r * 0.45)), (S(x + r), S(y - r * 0.45)), (S(x), S(y + r * 0.9))], fill=col)
    svc_header(img, 2, tl)
    return img


def s_maps(t, tl):
    img = background("glow2")
    paste_layer(img, maps_good(tl), 540, 1080, ease(tl / 0.35) * 0.98)
    svc_header(img, 3, tl)
    return img


def s_ai(t, tl):
    img = background("glow2")
    paste_layer(img, ai_chat(tl), 540, 1080, ease(tl / 0.35) * 0.98)
    svc_header(img, 4, tl)
    return img


def s_summary(t, tl):
    img = background("glow")
    d = ImageDraw.Draw(img)
    p = ease(tl / 0.4)
    tc(d, 540, 330 + (1 - p) * 40, "Gjithçka që i duhet", F(FD, 76, 700), mix(BLACK, LIGHT, p))
    tc(d, 540, 420 + (1 - p) * 40, "biznesit tënd online:", F(FD, 76, 700), mix(BLACK, PIKA, p))
    for i, s in enumerate(SERVICES):
        q = back((tl - 0.35 - i * 0.2) / 0.35)
        if q <= 0:
            continue
        y = 620 + i * 190
        x = 110 + (1 - q) * 120
        d.rounded_rectangle(B(x, y, 970, y + 150), radius=S(30), fill=(26, 27, 32), outline=(52, 54, 60), width=S(3))
        check(d, x + 80, y + 75, 38, PIKA)
        d.text((S(x + 150), S(y + 44)), s, font=F(FD, 56, 650), fill=LIGHT)
    return img


def s_cta(t, tl):
    img = background("glow")
    d = ImageDraw.Draw(img)
    p = ease(tl / 0.6)
    f = F(FD, 160, 700)
    word = "Webpik"
    wl = d.textlength(word + "e", font=f)
    x = S(540) - wl / 2
    y = S(600 + (1 - p) * 40)
    d.text((x, y), word + "e", font=f, fill=mix(BLACK, LIGHT, p))
    ex = x + d.textlength(word, font=f); ew = d.textlength("e", font=f)
    r = f.size * 0.07 * p; top = y + f.size * 0.18
    for k in (-1, 1):
        dx = ex + ew / 2 + k * ew * 0.22
        d.ellipse([dx - r, top - r, dx + r, top + r], fill=PIKA)
    q = ease((tl - 0.4) / 0.5)
    if q > 0:
        tc(d, 540, 860, "Nga “askush s’të gjen”", F(FD, 60, 650), mix(BLACK, LIGHT, q))
        tc(d, 540, 940, "te “të gjithë të gjejnë”.", F(FD, 60, 650), mix(BLACK, PIKA, q))
    c = back((tl - 0.9) / 0.45)
    if c > 0:
        bw, bh = 700 * c, 140 * c
        d.rounded_rectangle(B(540 - bw / 2, 1160 - bh / 2, 540 + bw / 2, 1160 + bh / 2), radius=S(30 * c), fill=PIKA)
        if c > 0.85:
            tc(d, 540, 1124, "Na shkruaj në DM", F(FD, 64, 700), INK)
    k = ease((tl - 1.3) / 0.5)
    if k > 0:
        tc(d, 540, 1290, "@webpike", F(FB, 40, 600), mix(BLACK, (160, 164, 170), k))
    return img


FUNCS = [s_hook, s_before, s_wipe, s_logo, s_web, s_insta, s_maps, s_ai, s_summary, s_cta]


def frame(t):
    si = next((i for i, (a, b) in enumerate(SCENES) if a <= t < b), len(SCENES) - 1)
    img = FUNCS[si](t, t - SCENES[si][0])
    d = ImageDraw.Draw(img)
    d.rectangle([0, S(H - 10), int(S(W) * t / DUR), S(H)], fill=PIKA)
    return img.resize((W, H), Image.LANCZOS)


def main():
    if "--only-frames" in sys.argv:
        for ts in [float(x) for x in ARGS[2].split(",")]:
            frame(ts).resize((540, 960)).save(f"{ARGS[1]}/f_{ts:05.2f}.png")
        return
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
           "-i", "-", "-an", "-c:v", "libx264", "-preset", "veryfast", "-crf", "19", "-pix_fmt", "yuv420p", "-movflags", "+faststart", OUT]
    pr = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    a, b = (int(x) for x in ARGS[1].split(":")) if len(ARGS) > 1 else (0, int(DUR * FPS))
    for i in range(a, b):
        pr.stdin.write(frame(i / FPS).tobytes())
    pr.stdin.close(); pr.wait()


if __name__ == "__main__":
    main()
