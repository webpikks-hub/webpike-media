import subprocess, math, sys
from PIL import Image, ImageDraw, ImageFont

W, H, FPS = 1080, 1920, 30
OUT = sys.argv[1] if len(sys.argv) > 1 else "/home/claude/webpike_video/webpike_reel1.mp4"
FD = "/home/claude/fonts/SpaceGrotesk%5Bwght%5D.ttf"
FB = "/home/claude/fonts/PlusJakartaSans%5Bwght%5D.ttf"

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


SCENES = [(0, 3.2), (3.2, 6.6), (6.6, 10.6), (10.6, 14.0)]
DUR = 14.0


def frame(t):
    # scene index
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
        # two dots pop in
        for k in range(2):
            p = ease((tl - k * 0.15) / 0.4)
            r = 22 * p
            d.ellipse([M + k * 64 - r + 22, 560 - r, M + k * 64 + r + 22, 560 + r], fill=PIKA)
        lines = ["Biznesi yt", "ende pa", "uebfaqe?"]
        text_block(img, lines, F_HUGE, M, 640, fg, tl - 0.3, accent="uebfaqe?")
        p = ease((tl - 1.4) / 0.5)
        if p > 0:
            d = ImageDraw.Draw(img)
            d.text((M, 1120 + (1 - p) * 30), "Restorant, kafiterie, dyqan, firmë…", font=F_BODY,
                   fill=tuple(int(INK[i] + ((163, 167, 174)[i] - INK[i]) * p) for i in range(3)))

    elif si == 1:
        lines = wrap(d, "Klientët të kërkojnë në Google…", F_BIG, W - 2 * M)
        y = text_block(img, lines, F_BIG, M, 520, INK, tl)
        lines2 = wrap(d, "…dhe gjejnë konkurrencën.", F_BIG, W - 2 * M)
        text_block(img, lines2, F_BIG, M, y + 60, INK, tl - 1.2, accent="konkurrencën.")
        # fake search bar
        p = ease(tl / 0.5)
        d = ImageDraw.Draw(img)
        bx, by = M, 330 - (1 - p) * 40
        d.rounded_rectangle([bx, by, W - M, by + 110], radius=55, fill=(255, 255, 255), outline=LINE, width=3)
        q = "restorant afër meje"
        n = int(len(q) * ease(tl / 1.2))
        d.text((bx + 50, by + 30), q[:n] + ("|" if int(t * 3) % 2 == 0 else ""), font=F_BODY, fill=MUTED)

    elif si == 2:
        text_block(img, ["Webpikë ta", "bën gati."], F_BIG, M, 420, INK, tl, accent="Webpikë")
        items = ["Menyja online", "Rezervime & kontakt", "Harta në Google", "Duket mirë në telefon"]
        for i, it in enumerate(items):
            p = ease((tl - 0.7 - i * 0.4) / 0.4)
            if p <= 0:
                continue
            y = 760 + i * 150
            x = M + (1 - p) * 80
            d.rounded_rectangle([x, y, W - M, y + 120], radius=20, fill=(255, 255, 255), outline=LINE, width=3)
            cx, cy = x + 62, y + 60
            d.ellipse([cx - 28, cy - 28, cx + 28, cy + 28], fill=DETI)
            d.line([(cx - 13, cy + 1), (cx - 3, cy + 12), (cx + 15, cy - 11)], fill=(255, 255, 255), width=7)
            d.text((x + 120, y + 32), it, font=F_BODY, fill=INK)

    else:
        p = ease(tl / 0.6)
        logo(d, W / 2, 640 - (1 - p) * 40, F_HUGE, (243, 241, 236), p)
        p2 = ease((tl - 0.5) / 0.5)
        if p2 > 0:
            s = "Uebfaqe që sjellin klientë."
            d.text((W / 2 - d.textlength(s, font=F_MED) / 2, 860), s, font=F_MED,
                   fill=tuple(int(INK[i] + ((243, 241, 236)[i] - INK[i]) * p2) for i in range(3)))
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
                   fill=tuple(int(INK[i] + ((163, 167, 174)[i] - INK[i]) * p4) for i in range(3)))

    # progress bar
    d.rectangle([0, H - 10, int(W * t / DUR), H], fill=PIKA)
    return img


def main():
    n = int(DUR * FPS)
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
           "-r", str(FPS), "-i", "-", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo",
           "-shortest", "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p",
           "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", OUT]
    pr = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for i in range(n):
        pr.stdin.write(frame(i / FPS).tobytes())
    pr.stdin.close(); pr.wait()
    for ts in (2.5, 6.0, 9.8, 13.5):
        frame(ts).resize((360, 640)).save(OUT.replace(".mp4", f"_t{ts}.png"))


main()
