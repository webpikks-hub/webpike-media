"""Webpikë Reel 04 – "5 fazat e biznesit pa uebfaqe" (cartoon 2.5D, 1080x1920, 17 s).

Usage: python3 make_video_reel04.py OUT_SILENT.mp4 [FRAMES_DIR] [--logo]
  --logo  adds the Webpikë logo + CTA in the clean space of the last scene.
All drawing is original (Pillow). No photoreal people, no third-party logos.
"""
import math, random, subprocess, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS, SS = 1080, 1920, 30, 2
DUR = 17.0
SCENES = [(0, 3.0), (3.0, 6.0), (6.0, 9.0), (9.0, 13.0), (13.0, 17.0)]
CUTS = [a for a, _ in SCENES[1:]]
WITH_LOGO = "--logo" in sys.argv
ARGS = [a for a in sys.argv[1:] if not a.startswith("--")]
OUT = ARGS[0] if ARGS else "reel04.mp4"
FRAMES = ARGS[1] if len(ARGS) > 1 else None

FD = "/home/claude/webpike-media/tools/fonts/SpaceGrotesk%5Bwght%5D.ttf"
FB = "/home/claude/webpike-media/tools/fonts/PlusJakartaSans%5Bwght%5D.ttf"

INK = (20, 22, 26); BLACK = (10, 11, 13); PIKA = (255, 90, 31); PIKA_D = (214, 66, 14)
CREAM = (250, 248, 244); DETI = (14, 124, 107); MUTED = (140, 145, 152); WHITE = (255, 255, 255)
SKIN = (232, 178, 138); SKIN_D = (205, 146, 108); HAIR = (34, 26, 24); HOOD = (36, 38, 44); HOOD_L = (54, 57, 64)


def font(path, size, wght):
    f = ImageFont.truetype(path, int(size * SS))
    try:
        f.set_variation_by_axes([wght])
    except Exception:
        pass
    return f


F_LBL = font(FD, 40, 700)
F_TTL = font(FD, 92, 700)
F_MSG = font(FB, 44, 700)
F_LOGO = font(FD, 150, 700)
F_CTA = font(FD, 58, 650)
F_SM = font(FB, 36, 600)


def ease(t):
    t = max(0.0, min(1.0, t)); return 1 - (1 - t) ** 3


def back(t, s=1.9):
    t = max(0.0, min(1.0, t)); t -= 1; return t * t * ((s + 1) * t + s) + 1


def lerp(a, b, p):
    return a + (b - a) * p


def mix(c1, c2, p):
    return tuple(int(lerp(a, b, p)) for a, b in zip(c1, c2))


class Cam:
    """world (1080x1920 coords) -> canvas pixels, with zoom around (cx, cy) and shake."""
    def __init__(self, cx=540, cy=960, z=1.0, sx=0, sy=0, rot=0):
        self.cx, self.cy, self.z, self.sx, self.sy = cx, cy, z, sx, sy

    def p(self, x, y):
        return (((x - self.cx) * self.z + W / 2 + self.sx) * SS, ((y - self.cy) * self.z + H / 2 + self.sy) * SS)

    def r(self, v):
        return v * self.z * SS

    def box(self, x0, y0, x1, y1):
        a = self.p(x0, y0); b = self.p(x1, y1); return [a[0], a[1], b[0], b[1]]


def bg(dark=True, glow=None, glow_pos=(540, 900), glow_r=900):
    img = Image.new("RGB", (W * SS, H * SS), BLACK if dark else CREAM)
    d = ImageDraw.Draw(img)
    if glow:
        g = Image.new("L", (W * SS // 4, H * SS // 4), 0)
        gd = ImageDraw.Draw(g)
        x, y = glow_pos[0] * SS / 4 * 1, glow_pos[1] * SS / 4
        r = glow_r * SS / 4
        gd.ellipse([x - r, y - r, x + r, y + r], fill=255)
        g = g.filter(ImageFilter.GaussianBlur(r / 2.2)).resize(img.size)
        img = Image.composite(Image.new("RGB", img.size, glow), img, g.point(lambda v: int(v * 0.55)))
        d = ImageDraw.Draw(img)
    col = (32, 34, 40) if dark else (228, 224, 216)
    for y in range(60, H, 72):
        for x in range(60, W, 72):
            d.ellipse([(x - 3) * SS, (y - 3) * SS, (x + 3) * SS, (y + 3) * SS], fill=col)
    return img


BG_CACHE = {}


def get_bg(key, **kw):
    if key not in BG_CACHE:
        BG_CACHE[key] = bg(**kw)
    return BG_CACHE[key].copy()


# ---------------------------------------------------------------- character
NEUTRAL = dict(brow=0, brow_y=0, eye=1.0, pupil=1.0, look=(0, 0), mouth="smile", mopen=0.5, sweat=0, blush=0.5,
               messy=0)


def draw_owner(d, cam, hx, hy, e, t, tilt=0):
    """Young owner: dark quiff, short beard, black hoodie with orange strings. Head centre (hx, hy)."""
    e = {**NEUTRAL, **e}
    R = 165
    P = cam.p; S = cam.r
    # body / hoodie
    bx, by = hx, hy + R + 40
    d.rounded_rectangle(cam.box(bx - 330, by + 40, bx + 330, by + 900), radius=S(200), fill=HOOD)
    d.rounded_rectangle(cam.box(bx - 300, by + 60, bx + 300, by + 900), radius=S(180), fill=HOOD_L)
    d.rounded_rectangle(cam.box(bx - 300, by + 90, bx + 300, by + 900), radius=S(180), fill=HOOD)
    # hood collar
    d.ellipse(cam.box(bx - 190, by - 10, bx + 190, by + 150), fill=HOOD_L)
    # neck
    d.rounded_rectangle(cam.box(hx - 62, hy + R - 60, hx + 62, by + 70), radius=S(40), fill=SKIN_D)
    # strings
    for k in (-1, 1):
        x = bx + k * 70
        d.line([P(x, by + 110), P(x + k * 6, by + 300)], fill=PIKA, width=int(S(12)))
        d.ellipse(cam.box(x + k * 6 - 13, by + 290, x + k * 6 + 13, by + 316), fill=PIKA)
    # orange shoulder stripe (brand)
    d.rounded_rectangle(cam.box(bx - 330, by + 230, bx - 290, by + 900), radius=S(14), fill=PIKA)
    d.rounded_rectangle(cam.box(bx + 290, by + 230, bx + 330, by + 900), radius=S(14), fill=PIKA)

    hx += tilt
    # ears
    for k in (-1, 1):
        d.ellipse(cam.box(hx + k * R - 32, hy - 20, hx + k * R + 32, hy + 60), fill=SKIN_D)
        d.ellipse(cam.box(hx + k * R - 20, hy - 6, hx + k * R + 20, hy + 46), fill=SKIN)
    # head with shading
    d.ellipse(cam.box(hx - R, hy - R * 1.08, hx + R, hy + R * 1.02), fill=SKIN_D)
    d.ellipse(cam.box(hx - R + 6, hy - R * 1.08, hx + R - 22, hy + R * 0.98), fill=SKIN)
    # beard (jaw shadow)
    d.chord(cam.box(hx - R + 4, hy - R * 0.2, hx + R - 4, hy + R * 1.02), 15, 165, fill=(150, 104, 80))
    d.chord(cam.box(hx - R + 30, hy - R * 0.1, hx + R - 30, hy + R * 0.86), 20, 160, fill=SKIN)
    # hair
    m = e["messy"]
    d.chord(cam.box(hx - R - 4, hy - R * 1.14, hx + R + 4, hy - R * 0.02), 180, 360, fill=HAIR)
    d.ellipse(cam.box(hx - R * 0.9, hy - R * 1.35, hx + R * 0.6, hy - R * 0.55), fill=HAIR)  # quiff
    d.ellipse(cam.box(hx - R * 0.2, hy - R * 1.28, hx + R * 0.95, hy - R * 0.62), fill=HAIR)
    for k in (-1, 1):
        d.rounded_rectangle(cam.box(hx + k * R - (4 if k < 0 else 24), hy - R * 0.62, hx + k * R + (24 if k < 0 else 4), hy - R * 0.05), radius=cam.r(10), fill=HAIR)
    if m > 0:  # messy spikes
        rnd = random.Random(int(t * 8))
        for i in range(7):
            a = math.pi * (1.05 + i * 0.13)
            x0, y0 = hx + math.cos(a) * R * 0.9, hy - R * 0.55 + math.sin(a) * R * 0.75
            L = (50 + rnd.random() * 60) * m
            d.polygon([P(x0 - 20, y0), P(x0 + 20, y0), P(x0 + math.cos(a) * L, y0 + math.sin(a) * L - 10)], fill=HAIR)
    # hair highlight (orange rim)
    d.arc(cam.box(hx - R * 0.6, hy - R * 1.28, hx + R * 0.5, hy - R * 0.7), 200, 300, fill=(90, 60, 50), width=int(S(8)))

    # eyes
    ey = hy - 10 + e["brow_y"] * 0.2
    es = e["eye"]
    lx, ly = e["look"]
    for k in (-1, 1):
        ex = hx + k * 66
        rw, rh = 40 * es, 46 * es
        d.ellipse(cam.box(ex - rw, ey - rh, ex + rw, ey + rh), fill=WHITE, outline=(60, 40, 35), width=int(S(4)))
        pr = 19 * e["pupil"] * min(es, 1.3)
        px, py = ex + lx * rw * 0.45, ey + ly * rh * 0.45
        d.ellipse(cam.box(px - pr, py - pr, px + pr, py + pr), fill=(28, 22, 20))
        d.ellipse(cam.box(px - pr * 0.35 + pr * 0.3, py - pr * 0.75, px + pr * 0.25 + pr * 0.3, py - pr * 0.15), fill=WHITE)
        # brows: angle >0 = worried (inner up), <0 = angry
        ang = e["brow"] * k
        by_ = ey - rh - 26 + e["brow_y"]
        x0, x1 = ex - 44, ex + 44
        y0 = by_ - ang * 18 * (-1 if k < 0 else 1) * -1
        yl = by_ + ang * 22 * (1 if k > 0 else -1) * (1 if k > 0 else 1)
        # inner end is towards centre
        inner_x = ex - k * 44; outer_x = ex + k * 44
        d.line([P(inner_x, by_ - e["brow"] * 20), P(outer_x, by_ + e["brow"] * 8)], fill=HAIR, width=int(S(16)))
    # nose
    d.arc(cam.box(hx - 20, hy + 20, hx + 22, hy + 64), 300, 110, fill=SKIN_D, width=int(S(7)))
    # blush
    if e["blush"]:
        for k in (-1, 1):
            d.ellipse(cam.box(hx + k * 105 - 28, hy + 52, hx + k * 105 + 28, hy + 78), fill=mix(SKIN, (240, 120, 100), e["blush"] * 0.6))
    # mouth
    my = hy + 100
    mo = e["mopen"]
    mt = e["mouth"]
    if mt == "smile":
        d.chord(cam.box(hx - 62, my - 34 - 10 * mo, hx + 62, my + 30 + 30 * mo), 0, 180, fill=(110, 30, 30))
        d.chord(cam.box(hx - 52, my - 34 - 10 * mo, hx + 52, my - 2), 0, 180, fill=WHITE)
    elif mt == "o":
        rw, rh = 30 + 20 * mo, 34 + 60 * mo
        d.ellipse(cam.box(hx - rw, my - rh * 0.5, hx + rw, my + rh), fill=(90, 22, 26))
        d.ellipse(cam.box(hx - rw * 0.6, my + rh * 0.45, hx + rw * 0.6, my + rh * 0.95), fill=(220, 90, 90))
    elif mt == "grit":
        d.rounded_rectangle(cam.box(hx - 64, my - 18, hx + 64, my + 34), radius=S(14), fill=WHITE, outline=(110, 30, 30), width=int(S(5)))
        d.line([P(hx - 60, my + 8), P(hx + 60, my + 8)], fill=(180, 170, 165), width=int(S(4)))
        for i in range(-2, 3):
            d.line([P(hx + i * 24, my - 16), P(hx + i * 24, my + 32)], fill=(180, 170, 165), width=int(S(3)))
    elif mt == "flat":
        d.line([P(hx - 40, my + 6), P(hx + 40, my + 2)], fill=(110, 30, 30), width=int(S(9)))
    elif mt == "smirk":
        d.arc(cam.box(hx - 50, my - 40, hx + 64, my + 24), 20, 150, fill=(110, 30, 30), width=int(S(10)))
    # sweat
    if e["sweat"] > 0:
        sx, sy = hx + R * 0.82, hy - R * 0.5 + (t * 140 % 90)
        s = 26 * e["sweat"]
        d.polygon([P(sx, sy - s * 1.6), P(sx - s, sy), P(sx + s, sy)], fill=(140, 200, 255))
        d.ellipse(cam.box(sx - s, sy - s, sx + s, sy + s), fill=(140, 200, 255))


def hand(d, cam, x, y, r=48):
    d.ellipse(cam.box(x - r, y - r, x + r, y + r), fill=SKIN_D)
    d.ellipse(cam.box(x - r + 5, y - r, x + r - 8, y + r - 6), fill=SKIN)


def sleeve(d, cam, x0, y0, x1, y1):
    d.line([cam.p(x0, y0), cam.p(x1, y1)], fill=HOOD_L, width=int(cam.r(96)))
    d.line([cam.p(x0, y0), cam.p(x1, y1)], fill=HOOD, width=int(cam.r(80)))


def phone_screen(w, h, t, scene):
    """Abstract IG-style business profile: avatar, stats bars, colourful grid (no text, no logos)."""
    img = Image.new("RGB", (w, h), (250, 250, 250))
    d = ImageDraw.Draw(img)
    u = w / 100
    d.ellipse([6 * u, 8 * u, 28 * u, 30 * u], fill=PIKA)
    d.ellipse([10 * u, 12 * u, 24 * u, 26 * u], fill=(255, 210, 180))
    for i in range(3):
        d.rounded_rectangle([36 * u + i * 21 * u, 13 * u, 50 * u + i * 21 * u, 18 * u], radius=u, fill=(40, 40, 40))
        d.rounded_rectangle([34 * u + i * 21 * u, 21 * u, 52 * u + i * 21 * u, 24 * u], radius=u, fill=(190, 190, 190))
    d.rounded_rectangle([6 * u, 36 * u, 60 * u, 40 * u], radius=u, fill=(60, 60, 60))
    d.rounded_rectangle([6 * u, 44 * u, 80 * u, 47 * u], radius=u, fill=(200, 200, 200))
    cols = [(255, 170, 120), (250, 205, 120), (240, 130, 100), (120, 190, 170), (255, 140, 80), (200, 160, 130),
            (250, 190, 150), (130, 170, 200), (240, 110, 70)]
    off = (t * 60) % (33 * u) if scene == 1 else 0
    top = 54 * u
    for i in range(18):
        r, c = divmod(i, 3)
        x0 = c * 33.6 * u; y0 = top + r * 33.6 * u - off
        if y0 > h or y0 + 33 * u < top:
            continue
        d.rectangle([x0 + 0.6 * u, max(top, y0), x0 + 33 * u, y0 + 33 * u], fill=cols[i % 9])
        # little food plate motif
        cx, cy = x0 + 17 * u, y0 + 17 * u
        if cy > top:
            d.ellipse([cx - 9 * u, cy - 9 * u, cx + 9 * u, cy + 9 * u], fill=(255, 250, 240))
            d.ellipse([cx - 5 * u, cy - 5 * u, cx + 5 * u, cy + 5 * u], fill=cols[(i + 4) % 9])
    return img


def draw_phone(img, cam, x, y, w, h, t, scene, angle=0):
    d = ImageDraw.Draw(img)
    pw, ph = int(cam.r(w)), int(cam.r(h))
    ph_img = Image.new("RGBA", (pw, ph), (0, 0, 0, 0))
    pd = ImageDraw.Draw(ph_img)
    pd.rounded_rectangle([0, 0, pw - 1, ph - 1], radius=pw * 0.14, fill=(16, 16, 18))
    m = int(pw * 0.05)
    scr = phone_screen(pw - 2 * m, ph - 2 * m, t, scene)
    mask = Image.new("L", scr.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, scr.size[0] - 1, scr.size[1] - 1], radius=pw * 0.1, fill=255)
    ph_img.paste(scr, (m, m), mask)
    pd.rounded_rectangle([pw * 0.38, m * 1.3, pw * 0.62, m * 1.3 + pw * 0.06], radius=pw * 0.03, fill=(16, 16, 18))
    if angle:
        ph_img = ph_img.rotate(angle, resample=Image.BICUBIC, expand=True)
    cx, cy = cam.p(x, y)
    img.paste(ph_img, (int(cx - ph_img.size[0] / 2), int(cy - ph_img.size[1] / 2)), ph_img)


def label(img, n, title, t_local, fade_out=None):
    d = ImageDraw.Draw(img)
    p = back(t_local / 0.45)
    if fade_out is not None and t_local > fade_out:
        p = 1 - ease((t_local - fade_out) / 0.35)
        if p <= 0:
            return
    if p <= 0:
        return
    y = 170 + (1 - p) * -120
    s = f"FAZA {n}/5"
    tw = d.textlength(s, font=F_LBL)
    x0 = 540 * SS - (tw + 60 * SS) / 2
    d.rounded_rectangle([x0, y * SS, x0 + tw + 60 * SS, (y + 70) * SS], radius=35 * SS, fill=PIKA)
    d.text((x0 + 30 * SS, (y + 12) * SS), s, font=F_LBL, fill=INK)
    tw2 = d.textlength(title, font=F_TTL)
    # shadow + text
    d.text((540 * SS - tw2 / 2 + 5 * SS, (y + 95) * SS), title, font=F_TTL, fill=(0, 0, 0))
    d.text((540 * SS - tw2 / 2, (y + 90) * SS), title, font=F_TTL, fill=WHITE)


def speed_lines(d, cx, cy, t, col=(255, 255, 255), n=22, r0=520):
    rnd = random.Random(int(t * 15))
    for i in range(n):
        a = rnd.random() * math.tau
        r1 = r0 + rnd.random() * 120
        r2 = r1 + 120 + rnd.random() * 260
        d.line([((cx + math.cos(a) * r1) * SS, (cy + math.sin(a) * r1) * SS),
                ((cx + math.cos(a) * r2) * SS, (cy + math.sin(a) * r2) * SS)], fill=col, width=int(4 * SS))


# ---------------------------------------------------------------- websites (abstract, no text)
def site_competitor(w, h):
    img = Image.new("RGB", (w, h), (246, 243, 236))
    d = ImageDraw.Draw(img); u = w / 100
    d.rectangle([0, 0, w, 8 * u], fill=(255, 255, 255))
    d.ellipse([3 * u, 2 * u, 7 * u, 6 * u], fill=DETI)
    for i in range(4):
        d.rounded_rectangle([60 * u + i * 9 * u, 3.4 * u, 66 * u + i * 9 * u, 4.8 * u], radius=u, fill=(150, 150, 150))
    d.rectangle([0, 8 * u, w, 40 * u], fill=(16, 72, 64))
    d.ellipse([58 * u, 10 * u, 92 * u, 44 * u], fill=(240, 200, 150))
    d.ellipse([63 * u, 15 * u, 87 * u, 39 * u], fill=(220, 120, 70))
    d.ellipse([70 * u, 20 * u, 78 * u, 28 * u], fill=(120, 170, 90))
    d.rounded_rectangle([6 * u, 16 * u, 46 * u, 21 * u], radius=u, fill=WHITE)
    d.rounded_rectangle([6 * u, 23.5 * u, 36 * u, 28.5 * u], radius=u, fill=WHITE)
    d.rounded_rectangle([6 * u, 32 * u, 22 * u, 36.5 * u], radius=2 * u, fill=(255, 190, 90))
    for i in range(3):
        x0 = 6 * u + i * 30 * u
        d.rounded_rectangle([x0, 46 * u, x0 + 26 * u, 80 * u], radius=2 * u, fill=WHITE)
        d.rounded_rectangle([x0 + 2 * u, 48 * u, x0 + 24 * u, 64 * u], radius=1.5 * u, fill=[(230, 160, 110), (140, 190, 160), (240, 210, 140)][i])
        d.rounded_rectangle([x0 + 2 * u, 67 * u, x0 + 18 * u, 69 * u], radius=u, fill=(60, 60, 60))
        d.rounded_rectangle([x0 + 2 * u, 72 * u, x0 + 22 * u, 73.5 * u], radius=u, fill=(180, 180, 180))
    return img


def site_premium(w, h, mobile=False):
    img = Image.new("RGB", (w, h), (14, 15, 18))
    d = ImageDraw.Draw(img); u = w / 100
    if not mobile:
        d.rectangle([0, 0, w, 8 * u], fill=(20, 21, 25))
        for k in range(2):
            d.ellipse([3 * u + k * 2.6 * u, 3 * u, 5 * u + k * 2.6 * u, 5 * u], fill=PIKA)
        for i in range(4):
            d.rounded_rectangle([58 * u + i * 8 * u, 3.4 * u, 64 * u + i * 8 * u, 4.6 * u], radius=u, fill=(110, 110, 115))
        d.rounded_rectangle([90 * u, 2.4 * u, 97 * u, 5.6 * u], radius=u, fill=PIKA)
        d.rounded_rectangle([6 * u, 16 * u, 50 * u, 22 * u], radius=u, fill=(245, 245, 245))
        d.rounded_rectangle([6 * u, 24.5 * u, 42 * u, 30.5 * u], radius=u, fill=PIKA)
        d.rounded_rectangle([6 * u, 34 * u, 40 * u, 35.5 * u], radius=u, fill=(120, 120, 125))
        d.rounded_rectangle([6 * u, 41 * u, 22 * u, 46 * u], radius=2.5 * u, fill=PIKA)
        d.rounded_rectangle([24 * u, 41 * u, 38 * u, 46 * u], radius=2.5 * u, outline=(200, 200, 200), width=max(1, int(0.3 * u)))
        d.ellipse([56 * u, 11 * u, 94 * u, 49 * u], fill=(40, 30, 26))
        d.ellipse([60 * u, 15 * u, 90 * u, 45 * u], fill=(250, 240, 228))
        d.ellipse([66 * u, 21 * u, 84 * u, 39 * u], fill=PIKA)
        d.ellipse([70 * u, 25 * u, 77 * u, 32 * u], fill=(255, 180, 120))
        for i in range(4):
            x0 = 6 * u + i * 22.5 * u
            d.rounded_rectangle([x0, 54 * u, x0 + 20 * u, 74 * u], radius=2 * u, fill=(26, 27, 32))
            d.ellipse([x0 + 6 * u, 57 * u, x0 + 14 * u, 65 * u], fill=[PIKA, (255, 160, 100), (240, 120, 60), (255, 200, 150)][i])
            d.rounded_rectangle([x0 + 3 * u, 68 * u, x0 + 17 * u, 69.5 * u], radius=u, fill=(160, 160, 165))
    else:
        d.rectangle([0, 0, w, 12 * u], fill=(20, 21, 25))
        for k in range(2):
            d.ellipse([7 * u + k * 6 * u, 4 * u, 11 * u + k * 6 * u, 8 * u], fill=PIKA)
        for k in range(3):
            d.rounded_rectangle([80 * u, 3.5 * u + k * 2.5 * u, 92 * u, 4.6 * u + k * 2.5 * u], radius=u, fill=(200, 200, 200))
        d.ellipse([20 * u, 16 * u, 80 * u, 76 * u], fill=(250, 240, 228))
        d.ellipse([30 * u, 26 * u, 70 * u, 66 * u], fill=PIKA)
        d.ellipse([40 * u, 36 * u, 54 * u, 50 * u], fill=(255, 180, 120))
        d.rounded_rectangle([8 * u, 84 * u, 80 * u, 92 * u], radius=2 * u, fill=(245, 245, 245))
        d.rounded_rectangle([8 * u, 96 * u, 62 * u, 104 * u], radius=2 * u, fill=PIKA)
        d.rounded_rectangle([8 * u, 112 * u, 56 * u, 124 * u], radius=6 * u, fill=PIKA)
        for i in range(2):
            d.rounded_rectangle([8 * u + i * 44 * u, 132 * u, 48 * u + i * 44 * u, 170 * u], radius=3 * u, fill=(26, 27, 32))
            d.ellipse([20 * u + i * 44 * u, 138 * u, 36 * u + i * 44 * u, 154 * u], fill=[(255, 160, 100), PIKA][i])
    return img


def coeffs(src, dst):
    import numpy as np
    A = []
    for (x, y), (X, Y) in zip(dst, src):
        A.append([x, y, 1, 0, 0, 0, -X * x, -X * y]); A.append([0, 0, 0, x, y, 1, -Y * x, -Y * y])
    B = [c for p in src for c in p]
    return np.linalg.solve(np.array(A, float), np.array(B, float)).tolist()


def warp_paste(img, src_img, quad):
    """paste src_img onto img (canvas px) at the 4-point quad (tl, tr, br, bl)."""
    w, h = src_img.size
    xs = [p[0] for p in quad]; ys = [p[1] for p in quad]
    x0, y0, x1, y1 = int(min(xs)), int(min(ys)), int(max(xs)) + 1, int(max(ys)) + 1
    loc = [(x - x0, y - y0) for x, y in quad]
    c = coeffs([(0, 0), (w, 0), (w, h), (0, h)], loc)
    rgba = src_img.convert("RGBA")
    out = rgba.transform((x1 - x0, y1 - y0), Image.PERSPECTIVE, c, Image.BICUBIC)
    img.paste(out, (x0, y0), out)


# ---------------------------------------------------------------- scenes
def scene1(t, tl):
    img = get_bg("s1", dark=True, glow=(70, 40, 20), glow_pos=(540, 1000), glow_r=700)
    z = lerp(0.82, 1.32, ease(tl / 3.0) * 0.6 + (tl / 3.0) * 0.4)
    cam = Cam(540, lerp(1150, 980, ease(tl / 3)), z)
    d = ImageDraw.Draw(img)
    bob = math.sin(tl * 3) * 6
    e = dict(mouth="smile", mopen=0.3 + 0.2 * math.sin(tl * 4), look=(-0.3, 0.9), brow=-0.1, blush=0.7)
    if int(tl * 10) % 26 == 0:  # blink
        e["eye"] = 0.12
    draw_owner(d, cam, 540, 900 + bob, e, t, tilt=8)
    # arm + phone
    sleeve(d, cam, 300, 1500, 380, 1330)
    draw_phone(img, cam, 400, 1300 + bob, 230, 440, t, 1, angle=-8)
    d = ImageDraw.Draw(img)
    hand(d, cam, 340, 1450 + bob)
    # floating hearts
    for i in range(5):
        ht = (tl * 0.9 + i * 0.37) % 1.4
        if ht > 1.2:
            continue
        x = 230 + math.sin(i * 2 + ht * 4) * 50 + (i - 2) * 22
        y = 1180 - ht * 380
        s = 26 * (1 - ht / 1.4) + 8
        cx, cy = cam.p(x, y)
        r = cam.r(s)
        col = PIKA if i % 2 else (255, 130, 90)
        d.ellipse([cx - r, cy - r, cx, cy], fill=col); d.ellipse([cx, cy - r, cx + r, cy], fill=col)
        d.polygon([(cx - r, cy - r * 0.45), (cx + r, cy - r * 0.45), (cx, cy + r * 0.9)], fill=col)
    label(img, 1, "Vetëbesimi", tl)
    return img


def scene2(t, tl):
    img = get_bg("s2", dark=True, glow=(90, 20, 10), glow_pos=(540, 900), glow_r=650)
    d = ImageDraw.Draw(img)
    hit = 0.55  # message arrives
    shock = ease((tl - hit - 0.15) / 0.25)
    z = lerp(1.25, 1.75, ease((tl - hit) / 0.35)) if tl > hit else 1.2
    shake = (math.sin(tl * 90) * 14, math.cos(tl * 77) * 10) if hit + 0.1 < tl < hit + 1.0 else (0, 0)
    cam = Cam(540, 960, z, shake[0], shake[1])
    if tl > hit:
        speed_lines(d, 540, 900, t, col=(70, 30, 20), n=26, r0=420)
    e = dict(mouth="smile", mopen=0.3, look=(-0.3, 0.9))
    if tl > hit:
        e = dict(mouth="o", mopen=0.3 + 0.7 * shock, eye=1 + 0.45 * shock, pupil=lerp(1, 0.45, shock),
                 brow=0.2 + 0.5 * shock, brow_y=-40 * shock, look=(0, 0), sweat=shock, blush=0)
    draw_owner(d, cam, 540, 900, e, t)
    sleeve(d, cam, 300, 1500, 380, 1330)
    draw_phone(img, cam, 400, 1330, 230, 440, t, 2, angle=-8)
    d = ImageDraw.Draw(img)
    hand(d, cam, 340, 1480)
    # message bubble (fixed to screen, not camera)
    p = back((tl - hit) / 0.35)
    if p > 0:
        bw, bh = 640, 150
        bx, by = 540 - bw / 2, 1480 - (1 - p) * 120
        sc = p
        cx, cy = 540, by + bh / 2
        box = [(cx - bw / 2 * sc) * SS, (cy - bh / 2 * sc) * SS, (cx + bw / 2 * sc) * SS, (cy + bh / 2 * sc) * SS]
        d.rounded_rectangle([box[0] + 8 * SS, box[1] + 10 * SS, box[2] + 8 * SS, box[3] + 10 * SS], radius=40 * SS, fill=(0, 0, 0))
        d.rounded_rectangle(box, radius=40 * SS * sc, fill=WHITE)
        if p > 0.8:
            d.ellipse([box[0] + 26 * SS, cy * SS - 36 * SS, box[0] + 98 * SS, cy * SS + 36 * SS], fill=(120, 190, 170))
            d.ellipse([box[0] + 44 * SS, cy * SS - 24 * SS, box[0] + 80 * SS, cy * SS + 4 * SS], fill=(240, 250, 246))
            d.chord([box[0] + 34 * SS, cy * SS + 2 * SS, box[0] + 90 * SS, cy * SS + 46 * SS], 180, 360, fill=(240, 250, 246))
            d.text((box[0] + 124 * SS, cy * SS - 30 * SS), "A keni uebfaqe?", font=F_MSG, fill=INK)
    # big ?! marks
    if tl > hit + 0.3:
        for i, (x, y, s) in enumerate([(230, 560, 1.0), (850, 520, 1.25), (800, 760, 0.8)]):
            q = back((tl - hit - 0.3 - i * 0.12) / 0.3)
            if q <= 0:
                continue
            f = font(FD, 150 * s * q, 700)
            ch = "?" if i != 1 else "?!"
            d.text(((x + 5) * SS, (y + 6) * SS + math.sin(tl * 8 + i) * 10 * SS), ch, font=f, fill=(0, 0, 0))
            d.text((x * SS, y * SS + math.sin(tl * 8 + i) * 10 * SS), ch, font=f, fill=PIKA)
    label(img, 2, "Paniku", tl)
    return img


def scene3(t, tl):
    img = get_bg("s3", dark=True, glow=(60, 60, 70), glow_pos=(540, 1100), glow_r=650)
    d = ImageDraw.Draw(img)
    sh = (math.sin(tl * 70) * 9, math.cos(tl * 63) * 7)
    cam = Cam(540, 1010, 1.05 + 0.08 * math.sin(tl * 1.5), sh[0], sh[1])
    # popping error windows behind him
    rnd = random.Random(7)
    for i in range(9):
        st = i * 0.28
        p = back((tl - st) / 0.25)
        if p <= 0:
            continue
        x = rnd.choice([110, 230, 760, 860, 180, 820, 300, 700, 540]) + rnd.uniform(-40, 40)
        y = 480 + rnd.uniform(0, 520)
        w_, h_ = 300 * p, 210 * p
        rot = rnd.uniform(-12, 12)
        win = Image.new("RGBA", (int(320 * SS), int(230 * SS)), (0, 0, 0, 0))
        wd = ImageDraw.Draw(win)
        wd.rounded_rectangle([0, 0, 300 * SS, 210 * SS], radius=18 * SS, fill=(240, 240, 242))
        wd.rounded_rectangle([0, 0, 300 * SS, 40 * SS], radius=18 * SS, fill=(200, 200, 206))
        wd.rectangle([0, 22 * SS, 300 * SS, 40 * SS], fill=(200, 200, 206))
        for k, c in enumerate([(255, 95, 86), (255, 189, 46), (39, 201, 63)]):
            wd.ellipse([(16 + k * 26) * SS, 12 * SS, (32 + k * 26) * SS, 28 * SS], fill=c)
        kind = i % 3
        if kind == 0:  # red X
            wd.ellipse([110 * SS, 75 * SS, 190 * SS, 155 * SS], fill=(230, 60, 50))
            wd.line([(130 * SS, 95 * SS), (170 * SS, 135 * SS)], fill=WHITE, width=int(10 * SS))
            wd.line([(170 * SS, 95 * SS), (130 * SS, 135 * SS)], fill=WHITE, width=int(10 * SS))
        elif kind == 1:  # spinner
            a0 = (tl * 500) % 360
            wd.arc([110 * SS, 75 * SS, 190 * SS, 155 * SS], a0, a0 + 270, fill=(120, 120, 130), width=int(12 * SS))
        else:  # broken page
            wd.rectangle([40 * SS, 70 * SS, 260 * SS, 90 * SS], fill=(190, 190, 195))
            wd.rectangle([40 * SS, 105 * SS, 200 * SS, 120 * SS], fill=(210, 210, 215))
            wd.polygon([(200 * SS, 140 * SS), (240 * SS, 180 * SS), (160 * SS, 180 * SS)], fill=(255, 189, 46))
            wd.line([(200 * SS, 152 * SS), (200 * SS, 166 * SS)], fill=INK, width=int(5 * SS))
        win = win.resize((max(2, int(320 * SS * p)), max(2, int(230 * SS * p))))
        win = win.rotate(rot, resample=Image.BICUBIC, expand=True)
        img.paste(win, (int(x * SS - win.size[0] / 2), int(y * SS - win.size[1] / 2)), win)
    d = ImageDraw.Draw(img)
    e = dict(mouth="grit" if int(tl * 6) % 3 else "o", mopen=0.6, eye=1.15, pupil=0.7, brow=-0.6 if int(tl * 4) % 2 else 0.6,
             brow_y=-10, look=(math.sin(tl * 14) * 0.9, 0.6), sweat=1.0, blush=0, messy=min(1, tl / 1.2))
    draw_owner(d, cam, 540, 900 + math.sin(tl * 20) * 8, e, t, tilt=math.sin(tl * 9) * 14)
    # laptop (back side towards viewer, plain – no logos)
    lx0, lx1, ly0, ly1 = 210, 870, 1250, 1640
    d.rounded_rectangle(cam.box(lx0, ly0, lx1, ly1), radius=cam.r(30), fill=(58, 60, 66))
    d.rounded_rectangle(cam.box(lx0 + 10, ly0 + 10, lx1 - 10, ly1 - 10), radius=cam.r(24), fill=(72, 74, 80))
    d.rectangle(cam.box(lx0 - 50, ly1 - 6, lx1 + 50, ly1 + 40), fill=(44, 46, 52))
    # frantic hands
    for k in (-1, 1):
        hx = 540 + k * 260 + math.sin(tl * 38 + k) * 40
        hy = 1660 + math.cos(tl * 45 + k * 2) * 26
        sleeve(d, cam, 540 + k * 330, 1900, hx, hy)
        hand(d, cam, hx, hy, 52)
        for j in range(3):  # motion streaks
            d.arc(cam.box(hx - 90 - j * 18, hy - 90 - j * 18, hx + 90 + j * 18, hy + 90 + j * 18), 200 + k * 60, 250 + k * 60,
                  fill=(200, 200, 205), width=int(cam.r(5)))
    # flying papers
    for i in range(5):
        pt = (tl * 0.8 + i * 0.21) % 1.0
        px = [110, 270, 810, 970, 160][i] + math.sin(pt * 6 + i) * 50
        py = 1500 - pt * 1100
        pa = Image.new("RGBA", (int(110 * SS), int(140 * SS)), (245, 245, 240, 255))
        ImageDraw.Draw(pa).rectangle([14 * SS, 24 * SS, 90 * SS, 32 * SS], fill=(190, 190, 190))
        pa = pa.rotate(pt * 400 + i * 50, expand=True, resample=Image.BICUBIC)
        img.paste(pa, (int(px * SS - pa.size[0] / 2), int(py * SS - pa.size[1] / 2)), pa)
    label(img, 3, "Kaosi", tl)
    return img


def scene4(t, tl):
    # 0–1.5: competitor site push-in on screen; 1.5–4: face lit by screen, shock → realization
    if tl < 1.5:
        img = get_bg("s4a", dark=True, glow=(10, 70, 60), glow_pos=(540, 960), glow_r=800)
        d = ImageDraw.Draw(img)
        z = lerp(0.9, 1.15, ease(tl / 1.5))
        sw, sh = 900 * z, 580 * z
        cx, cy = 540, 980
        q = [((cx - sw / 2) * SS, (cy - sh / 2) * SS), ((cx + sw / 2) * SS, (cy - sh / 2 + 20) * SS),
             ((cx + sw / 2) * SS, (cy + sh / 2 - 20) * SS), ((cx - sw / 2) * SS, (cy + sh / 2) * SS)]
        d.rounded_rectangle([q[0][0] - 24 * SS, q[0][1] - 24 * SS, q[2][0] + 24 * SS, q[3][1] + 24 * SS], radius=30 * SS, fill=(30, 32, 36))
        site = site_competitor(1000, 640)
        # scroll reveal
        warp_paste(img, site, q)
        # sparkle stars
        d = ImageDraw.Draw(img)
        for i in range(6):
            a = tl * 2 + i
            x = 540 + math.cos(a * 1.3 + i) * 470; y = 980 + math.sin(a + i * 2) * 380
            s = (12 + 8 * math.sin(tl * 9 + i)) * SS
            d.polygon([(x * SS, y * SS - s * 2), (x * SS + s * 0.5, y * SS), (x * SS, y * SS + s * 2), (x * SS - s * 0.5, y * SS)], fill=(160, 255, 220))
            d.polygon([(x * SS - s * 2, y * SS), (x * SS, y * SS - s * 0.5), (x * SS + s * 2, y * SS), (x * SS, y * SS + s * 0.5)], fill=(160, 255, 220))
        label(img, 4, "E vërteta", tl)
        return img
    k = tl - 1.5
    img = get_bg("s4b", dark=True, glow=(14, 110, 95), glow_pos=(540, 1050), glow_r=520)
    d = ImageDraw.Draw(img)
    cam = Cam(540, lerp(980, 930, ease(k / 2.5)), lerp(1.35, 1.6, ease(k / 2.5)))
    real = ease((k - 1.1) / 0.6)
    if real < 0.01:
        e = dict(mouth="o", mopen=0.9, eye=1.5, pupil=0.4, brow=0.6, brow_y=-45, look=(0, 0.3), blush=0)
    else:
        e = dict(mouth="smirk", mopen=0.2, eye=lerp(1.5, 0.95, real), pupil=lerp(0.4, 1.15, real), brow=lerp(0.6, -0.35, real),
                 brow_y=lerp(-45, 4, real), look=(0.5 * real, 0.2), blush=0.3 * real)
    draw_owner(d, cam, 540, 900, e, t)
    # dramatic teal screen light from below + dark vignette
    ov = Image.new("L", img.size, 0)
    od = ImageDraw.Draw(ov)
    od.rectangle([0, int(1250 * SS), img.size[0], img.size[1]], fill=110)
    ov = ov.filter(ImageFilter.GaussianBlur(120 * SS / 2))
    img = Image.composite(Image.new("RGB", img.size, (14, 130, 112)), img, ov)
    d = ImageDraw.Draw(img)
    if real > 0:  # lightbulb
        p = back((k - 1.2) / 0.4)
        bx, by = 540, 520
        r = 58 * p
        if r > 2:
            g = Image.new("L", (img.size[0] // 4, img.size[1] // 4), 0)
            ImageDraw.Draw(g).ellipse([(bx - 200) * SS / 4, (by - 200) * SS / 4, (bx + 200) * SS / 4, (by + 200) * SS / 4], fill=int(200 * p))
            g = g.filter(ImageFilter.GaussianBlur(30)).resize(img.size)
            img = Image.composite(Image.new("RGB", img.size, PIKA), img, g)
            d = ImageDraw.Draw(img)
            d.ellipse([(bx - r) * SS, (by - r) * SS, (bx + r) * SS, (by + r) * SS], fill=(255, 230, 140))
            d.rounded_rectangle([(bx - r * 0.45) * SS, (by + r * 0.8) * SS, (bx + r * 0.45) * SS, (by + r * 1.4) * SS], radius=8 * SS, fill=(170, 170, 175))
            for i in range(8):
                a = i * math.tau / 8
                d.line([((bx + math.cos(a) * r * 1.4) * SS, (by + math.sin(a) * r * 1.4) * SS),
                        ((bx + math.cos(a) * r * 1.9) * SS, (by + math.sin(a) * r * 1.9) * SS)], fill=(255, 220, 120), width=int(8 * SS))
    label(img, 4, "E vërteta", tl)
    return img


PARTS = [(random.Random(i).uniform(0, 1080), random.Random(i * 3).uniform(0, 1920), random.Random(i * 7).uniform(0.4, 1.0),
          random.Random(i * 11).uniform(0, 6.28)) for i in range(90)]


def scene5(t, tl):
    img = get_bg("s5", dark=True, glow=(110, 38, 8), glow_pos=(540, 1080), glow_r=620)
    d = ImageDraw.Draw(img)
    # particles drifting up
    for i, (x, y, s, ph) in enumerate(PARTS):
        yy = (y - tl * 160 * s) % 1920
        xx = x + math.sin(tl * 1.5 + ph) * 20
        r = (2 + 5 * s) * SS
        a = 0.5 + 0.5 * math.sin(tl * 3 + ph)
        c = mix((60, 20, 5), PIKA if i % 3 else (255, 180, 120), a)
        d.ellipse([xx * SS - r, yy * SS - r, xx * SS + r, yy * SS + r], fill=c)
    # devices rise in with fake-3D perspective sway
    p = ease((tl - 0.15) / 0.9)
    sway = math.sin(tl * 1.1) * 0.06
    lift = (1 - p) * 500
    # laptop
    cx, cy = 560, 1050 + lift
    sw, sh = 780, 490
    k = sway * sw
    q = [((cx - sw / 2) * SS, (cy - sh / 2 + k * 0.4) * SS), ((cx + sw / 2) * SS, (cy - sh / 2 - k * 0.4) * SS),
         ((cx + sw / 2) * SS, (cy + sh / 2 + k * 0.4) * SS), ((cx - sw / 2) * SS, (cy + sh / 2 - k * 0.4) * SS)]
    frame_q = [(q[0][0] - 22 * SS, q[0][1] - 22 * SS), (q[1][0] + 22 * SS, q[1][1] - 22 * SS),
               (q[2][0] + 22 * SS, q[2][1] + 22 * SS), (q[3][0] - 22 * SS, q[3][1] + 22 * SS)]
    # shadow
    sh_img = Image.new("L", (img.size[0] // 4, img.size[1] // 4), 0)
    ImageDraw.Draw(sh_img).ellipse([(cx - 460) * SS / 4, (cy + 300) * SS / 4, (cx + 460) * SS / 4, (cy + 380) * SS / 4], fill=180)
    sh_img = sh_img.filter(ImageFilter.GaussianBlur(14)).resize(img.size)
    img = Image.composite(Image.new("RGB", img.size, (0, 0, 0)), img, sh_img)
    d = ImageDraw.Draw(img)
    d.polygon(frame_q, fill=(28, 29, 33))
    d.line(frame_q + [frame_q[0]], fill=(70, 72, 78), width=int(3 * SS))
    warp_paste(img, site_premium(1000, 630), q)
    d = ImageDraw.Draw(img)
    base_y = cy + sh / 2 + 22
    d.polygon([((cx - 470) * SS, (base_y + k * 0.4 * 0) * SS), ((cx + 470) * SS, base_y * SS), ((cx + 520) * SS, (base_y + 34) * SS),
               ((cx - 520) * SS, (base_y + 34) * SS)], fill=(52, 54, 60))
    d.rectangle([(cx - 520) * SS, (base_y + 34) * SS, (cx + 520) * SS, (base_y + 44) * SS], fill=(36, 38, 42))
    # phone in front, right
    p2 = ease((tl - 0.45) / 0.9)
    pcx, pcy = 860, 1240 + (1 - p2) * 600
    pw, ph = 250, 510
    kk = -sway * pw * 1.4
    pq = [((pcx - pw / 2) * SS, (pcy - ph / 2 - kk) * SS), ((pcx + pw / 2) * SS, (pcy - ph / 2 + kk) * SS),
          ((pcx + pw / 2) * SS, (pcy + ph / 2 - kk) * SS), ((pcx - pw / 2) * SS, (pcy + ph / 2 + kk) * SS)]
    body = [(pq[0][0] - 14 * SS, pq[0][1] - 14 * SS), (pq[1][0] + 14 * SS, pq[1][1] - 14 * SS), (pq[2][0] + 14 * SS, pq[2][1] + 14 * SS),
            (pq[3][0] - 14 * SS, pq[3][1] + 14 * SS)]
    d.polygon(body, fill=(22, 22, 25))
    d.line(body + [body[0]], fill=PIKA, width=int(4 * SS))
    warp_paste(img, site_premium(300, 600, mobile=True), pq)
    # orange flash transition at start
    if tl < 0.45:
        f = 1 - ease(tl / 0.45)
        fl = Image.new("RGB", img.size, PIKA)
        img = Image.blend(img, fl, f * 0.95)
    d = ImageDraw.Draw(img)
    label(img, 5, "Zgjidhja", tl, fade_out=1.9)
    # clean space for logo (top) – optional logo
    if WITH_LOGO:
        pl = ease((tl - 2.2) / 0.6)
        if pl > 0:
            col = mix(BLACK, (243, 241, 236), pl)
            word = "Webpik"
            wl = d.textlength(word + "e", font=F_LOGO)
            x = 540 * SS - wl / 2
            y = (360 + (1 - pl) * 40) * SS
            d.text((x, y), word + "e", font=F_LOGO, fill=col)
            ex = x + d.textlength(word, font=F_LOGO); ew = d.textlength("e", font=F_LOGO)
            r = F_LOGO.size * 0.07 * pl
            top = y + F_LOGO.size * 0.18
            for kq in (-1, 1):
                dx = ex + ew / 2 + kq * ew * 0.22
                d.ellipse([dx - r, top - r, dx + r, top + r], fill=PIKA)
        pc = ease((tl - 2.6) / 0.5)
        if pc > 0:
            bw, bh = 640, 124
            bx, by = 540 - bw / 2, 1600 + (1 - pc) * 40
            d.rounded_rectangle([bx * SS, by * SS, (bx + bw) * SS, (by + bh) * SS], radius=26 * SS, fill=mix(BLACK, PIKA, pc))
            s = "Na shkruaj në DM"
            d.text((540 * SS - d.textlength(s, font=F_CTA) / 2, (by + 26) * SS), s, font=F_CTA, fill=mix(BLACK, INK, pc))
            s2 = "@webpike"
            d.text((540 * SS - d.textlength(s2, font=F_SM) / 2, (by + 150) * SS), s2, font=F_SM, fill=mix(BLACK, MUTED, pc))
    return img


FUNCS = [scene1, scene2, scene3, scene4, scene5]


def frame(t):
    si = next((i for i, (a, b) in enumerate(SCENES) if a <= t < b), 4)
    a, _ = SCENES[si]
    img = FUNCS[si](t, t - a)
    # quick white flash on cuts (viral edit feel)
    for c in CUTS[:3]:
        if 0 <= t - c < 0.08:
            img = Image.blend(img, Image.new("RGB", img.size, WHITE), 0.6)
    d = ImageDraw.Draw(img)
    d.rectangle([0, (H - 10) * SS, int(W * SS * t / DUR), H * SS], fill=PIKA)
    return img.resize((W, H), Image.LANCZOS)


def main():
    n = int(DUR * FPS)
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
           "-i", "-", "-an", "-c:v", "libx264", "-preset", "veryfast", "-crf", "19", "-pix_fmt", "yuv420p",
           "-movflags", "+faststart", OUT]
    if FRAMES:
        for ts in [float(x) for x in ARGS[2].split(",")] if len(ARGS) > 2 else (1.5, 4.3, 7.5, 9.8, 12.6, 16.5):
            frame(ts).resize((540, 960)).save(f"{FRAMES}/f_{ts:05.2f}.png")
        if "--only-frames" in sys.argv:
            return
    pr = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for i in range(n):
        pr.stdin.write(frame(i / FPS).tobytes())
    pr.stdin.close(); pr.wait()


if __name__ == "__main__":
    main()
