import subprocess, math, sys
from PIL import Image, ImageDraw, ImageFont

W, H, FPS = 1080, 1920, 30
OUT = sys.argv[1] if len(sys.argv) > 1 else "/home/claude/webpike-media/videos/webpike-reel-07-video.mp4"
FD = "/home/claude/webpike-media/tools/fonts/SpaceGrotesk%5Bwght%5D.ttf"
FB = "/home/claude/webpike-media/tools/fonts/PlusJakartaSans%5Bwght%5D.ttf"

SURF = (250, 248, 244); INK = (20, 22, 26); MUTED = (91, 96, 104)
PIKA = (255, 90, 31); PIKA_SOFT = (255, 227, 214); DETI = (14, 124, 107); LINE = (228, 224, 216)


def font(path, size, wght):
    f = ImageFont.truetype(path, size)
    try:
        f.set_variation_by_axes([wght])
    except Exception:
        pass
    return f

F_HUGE = font(FD, 128, 700)
F_BIG = font(FD, 96, 700)
F_MED = font(FD, 64, 600)
F_BODY = font(FB, 46, 500)
F_SMALL = font(FB, 38, 600)


def ease(t):
    t = max(0.0, min(1.0, t))
    return 1 - (1 - t) ** 3


def wrap(draw, text, f, maxw):
    words, lines, cur = text.split(), [], ""
    for w in words:
        test = (cur + " " + w).strip()
        if draw.textlength(test, font=f) <= maxw:
            cur = test
        else:
            lines.append(cur); cur = w
    if cur:
        lines.append(cur)
    return lines


def dot_grid(d, bg_dark):
    col = (44, 47, 53) if bg_dark else LINE
    for y in range(60, H, 72):
        for x in range(60, W, 72):
            d.ellipse([x - 3, y - 3, x + 3, y + 3], fill=col)


def text_block(img, lines, f, x, y, color, t_local, stagger=0.12, lh=1.12, accent=None):
    d = ImageDraw.Draw(img)
    size = f.size
    for i, ln in enumerate(lines):
        p = ease((t_local - i * stagger) / 0.5)
        if p <= 0:
            continue
        dy = int((1 - p) * 60)
        c = tuple(int(bg + (fg - bg) * p) for fg, bg in zip(color, img.getpixel((5, 5))[:3]))
        if accent and accent in ln:
            pre, post = ln.split(accent, 1)
            d.text((x, y + i * size * lh + dy), pre, font=f, fill=c)
            px = x + d.textlength(pre, font=f)
            ac = tuple(int(bg + (fg - bg) * p) for fg, bg in zip(PIKA, img.getpixel((5, 5))[:3]))
            d.text((px, y + i * size * lh + dy), accent, font=f, fill=ac)
            d.text((px + d.textlength(accent, font=f), y + i * size * lh + dy), post, font=f, fill=c)
        else:
            d.text((x, y + i * size * lh + dy), ln, font=f, fill=c)
    return y + len(lines) * size * lh


def logo(d, cx, cy, f, color, scale_p=1.0):
    word = "Webpik"
    wlen = d.textlength(word + "e", font=f)
    x = cx - wlen / 2
    d.text((x, cy), word + "e", font=f, fill=color)
    # orange ë dots
    ex = x + d.textlength(word, font=f)
    ew = d.textlength("e", font=f)
    r = f.size * 0.07 * scale_p
    top = cy + f.size * 0.18
    for k in (-1, 1):
        dx = ex + ew / 2 + k * ew * 0.22
        d.ellipse([dx - r, top - r, dx + r, top + r], fill=PIKA)




SCENES = [(0, 3.2), (3.2, 7.4), (7.4, 11.4), (11.4, 14.6)]
DUR = 14.6
CUTS = [a for a, _ in SCENES[1:]]
WHITE = (255, 255, 255)
QUERY = "restorant afër meje"

RESULTS = [
    ("Restoranti Ura", "Menyja · Orari · Rezervo", True),
    ("Pizzeria Dielli", "Menyja · Lokacioni", True),
    ("Biznesi yt", "Nuk shfaqet…", False),
]
CHECKS = [
    "Shfaqesh në Google dhe Maps",
    "Menyja, orari e lokacioni në një vend",
    "Klienti të gjen ty – jo konkurrencën",
]


def mix(a, b, p):
    return tuple(int(a[i] + (b[i] - a[i]) * p) for i in range(3))


def search_bar(d, y, tl):
    M = 90
    d.rounded_rectangle([M, y, W - M, y + 130], radius=65, fill=WHITE, outline=LINE, width=4)
    # magnifier
    cx, cy = M + 70, y + 62
    d.ellipse([cx - 22, cy - 22, cx + 22, cy + 22], outline=MUTED, width=6)
    d.line([cx + 15, cy + 15, cx + 34, cy + 34], fill=MUTED, width=7)
    n = int(max(0, min(len(QUERY), (tl - 0.2) / 1.1 * len(QUERY))))
    txt = QUERY[:n]
    d.text((M + 120, y + 34), txt, font=F_BODY, fill=INK)
    if n < len(QUERY) or int(tl * 2.5) % 2 == 0:
        x = M + 120 + d.textlength(txt, font=F_BODY) + 4
        d.rectangle([x, y + 36, x + 4, y + 96], fill=PIKA)


def result_card(d, i, y, tl, delay):
    name, sub, ok = RESULTS[i]
    p = ease((tl - delay) / 0.5)
    if p <= 0:
        return
    M = 90
    x = M + (1 - p) * 80
    if ok:
        d.rounded_rectangle([x, y, W - M, y + 200], radius=26, fill=WHITE, outline=LINE, width=3)
        # pin
        px, py = x + 75, y + 82
        d.ellipse([px - 30, py - 30, px + 30, py + 30], fill=DETI)
        d.polygon([(px - 22, py + 18), (px + 22, py + 18), (px, py + 58)], fill=DETI)
        d.ellipse([px - 11, py - 11, px + 11, py + 11], fill=WHITE)
        d.text((x + 140, y + 38), name, font=F_MED, fill=INK)
        d.text((x + 140, y + 118), sub, font=F_SMALL, fill=DETI)
    else:
        # dashed empty card
        x0, x1, y0, y1 = x, W - M, y, y + 200
        for xx in range(int(x0), int(x1), 40):
            d.line([xx, y0, min(xx + 22, x1), y0], fill=PIKA, width=4)
            d.line([xx, y1, min(xx + 22, x1), y1], fill=PIKA, width=4)
        for yy in range(int(y0), int(y1), 40):
            d.line([x0, yy, x0, min(yy + 22, y1)], fill=PIKA, width=4)
            d.line([x1, yy, x1, min(yy + 22, y1)], fill=PIKA, width=4)
        d.text((x + 60, y + 38), name, font=F_MED, fill=MUTED)
        d.text((x + 60, y + 118), sub, font=F_SMALL, fill=PIKA)


def check_row(d, i, y, tl, delay):
    p = ease((tl - delay) / 0.5)
    if p <= 0:
        return
    M = 90
    x = M + (1 - p) * 80
    d.rounded_rectangle([x, y, W - M, y + 220], radius=28, fill=WHITE, outline=LINE, width=3)
    cx, cy = x + 95, y + 110
    d.ellipse([cx - 50, cy - 50, cx + 50, cy + 50], fill=DETI if i != 2 else PIKA)
    d.line([cx - 24, cy + 2, cx - 6, cy + 22, cx + 26, cy - 20], fill=WHITE, width=12, joint="curve")
    lines = wrap(d, CHECKS[i], F_BODY, W - M - (x + 190) - 30)
    ty = y + 110 - len(lines) * 58 / 2
    for k, ln in enumerate(lines):
        d.text((x + 190, ty + k * 58), ln, font=F_BODY, fill=INK)


def frame(t):
    si = next(i for i, (a, b) in enumerate(SCENES) if a <= t < b) if t < DUR else 3
    a, b = SCENES[si]
    tl = t - a
    dark = si in (0, 3)
    img = Image.new("RGB", (W, H), INK if dark else SURF)
    d = ImageDraw.Draw(img)
    dot_grid(d, dark)
    fg = (243, 241, 236) if dark else INK
    M = 90

    if si == 0:
        for k in range(2):
            p = ease((tl - k * 0.15) / 0.4)
            r = 22 * p
            d.ellipse([M + k * 64 - r + 22, 540 - r, M + k * 64 + r + 22, 540 + r], fill=PIKA)
        text_block(img, ["A të gjen", "klienti në", "Google?"], F_HUGE, M, 620, fg, tl - 0.3, accent="Google?")
        p = ease((tl - 1.3) / 0.5)
        if p > 0:
            d = ImageDraw.Draw(img)
            d.text((M, 1100 + (1 - p) * 30), "Çdo ditë dikush kërkon biznesin tënd.", font=F_BODY,
                   fill=mix(INK, (163, 167, 174), p))

    elif si == 1:
        text_block(img, ["Klienti kërkon:"], F_MED, M, 300, MUTED, tl)
        search_bar(d, 420, tl)
        result_card(d, 0, 640, tl, 1.5)
        result_card(d, 1, 880, tl, 1.9)
        result_card(d, 2, 1120, tl, 2.4)
        p = ease((tl - 2.9) / 0.5)
        if p > 0:
            d.text((M, 1400 + (1 - p) * 30), "Pa uebfaqe, je i padukshëm.", font=F_MED, fill=mix(SURF, INK, p))

    elif si == 2:
        text_block(img, ["Me uebfaqe:"], F_BIG, M, 300, INK, tl, accent="uebfaqe:")
        for i in range(3):
            check_row(d, i, 520 + i * 270, tl, 0.4 + i * 0.7)

    else:
        p = ease(tl / 0.6)
        logo(d, W / 2, 620 - (1 - p) * 40, F_HUGE, (243, 241, 236), p)
        p2 = ease((tl - 0.5) / 0.5)
        if p2 > 0:
            for j, s in enumerate(["Bëhu i dukshëm", "aty ku të kërkojnë."]):
                d.text((W / 2 - d.textlength(s, font=F_MED) / 2, 840 + j * 80), s, font=F_MED,
                       fill=mix(INK, (243, 241, 236), p2))
        p3 = ease((tl - 1.0) / 0.5)
        if p3 > 0:
            bw, bh = 640, 130
            bx, by = W / 2 - bw / 2, 1080 + (1 - p3) * 40
            d.rounded_rectangle([bx, by, bx + bw, by + bh], radius=24, fill=PIKA)
            s = "Na shkruaj në DM"
            d.text((W / 2 - d.textlength(s, font=F_MED) / 2, by + 28), s, font=F_MED, fill=INK)
        p4 = ease((tl - 1.4) / 0.5)
        if p4 > 0:
            s = "@webpike"
            d.text((W / 2 - d.textlength(s, font=F_SMALL) / 2, 1280), s, font=F_SMALL,
                   fill=mix(INK, (163, 167, 174), p4))

    d.rectangle([0, H - 10, int(W * t / DUR), H], fill=PIKA)
    return img


def main():
    n = int(DUR * FPS)
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
           "-r", str(FPS), "-i", "-", "-an", "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
           "-pix_fmt", "yuv420p", "-movflags", "+faststart", OUT]
    pr = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for i in range(n):
        pr.stdin.write(frame(i / FPS).tobytes())
    pr.stdin.close(); pr.wait()
    if len(sys.argv) > 2:
        for ts in (2.9, 7.1, 11.1, 14.4):
            frame(ts).resize((540, 960)).save(f"{sys.argv[2]}/frame_{ts}.png")


main()
