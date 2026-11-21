# Karusel 1080x1350: "4 gjëra që duhet t'i ketë uebfaqja e restorantit tënd" (Webpikë)
import os, sys
from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1350
HERE = os.path.dirname(os.path.abspath(__file__))
FD = os.path.join(HERE, "fonts", "SpaceGrotesk%5Bwght%5D.ttf")
FB = os.path.join(HERE, "fonts", "PlusJakartaSans%5Bwght%5D.ttf")
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "..", "images", "post-06")

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

# --- ikonat (forma të thjeshta) ---
def icon_menu(d, cx, cy):
    d.rounded_rectangle([cx-110, cy-150, cx+110, cy+150], radius=34, fill=WHITE, outline=INK, width=8)
    d.rounded_rectangle([cx-60, cy-120, cx+60, cy-80], radius=20, fill=PIKA)
    for k in range(4):
        y = cy - 40 + k*48
        d.line([(cx-70, y), (cx+20, y)], fill=INK, width=10)
        d.ellipse([cx+45, y-8, cx+61, y+8], fill=DETI)

def icon_pin(d, cx, cy):
    d.ellipse([cx-150, cy+90, cx+150, cy+150], fill=LINE)
    d.ellipse([cx-90, cy-150, cx+90, cy+30], fill=PIKA)
    d.polygon([(cx-78, cy-20), (cx+78, cy-20), (cx, cy+120)], fill=PIKA)
    d.ellipse([cx-36, cy-96, cx+36, cy-24], fill=WHITE)

def icon_button(d, cx, cy):
    d.rounded_rectangle([cx-200, cy-60, cx+200, cy+60], radius=60, fill=DETI)
    t = "Rezervo"; tw = d.textlength(t, font=F_MED)
    d.text((cx-tw/2, cy-34), t, font=F_MED, fill=WHITE)
    # dora/kursori
    px, py = cx+150, cy+40
    d.polygon([(px, py), (px, py+110), (px+28, py+82), (px+50, py+130), (px+72, py+120), (px+50, py+74), (px+88, py+72)], fill=INK)

def icon_phone(d, cx, cy):
    d.rounded_rectangle([cx-95, cy-165, cx+95, cy+165], radius=36, fill=INK)
    d.rounded_rectangle([cx-78, cy-135, cx+78, cy+135], radius=20, fill=WHITE)
    d.rounded_rectangle([cx-64, cy-120, cx+64, cy-30], radius=14, fill=PIKA)
    d.line([(cx-64, cy), (cx+40, cy)], fill=INK, width=10)
    d.line([(cx-64, cy+32), (cx+10, cy+32)], fill=MUTED, width=8)
    # rrufe = shpejtësi
    bx, by = cx+120, cy-60
    d.polygon([(bx+20, by-70), (bx-30, by+20), (bx+5, by+20), (bx-15, by+100), (bx+45, by-5), (bx+10, by-5)], fill=PIKA)

ITEMS = [
    ("Menyja online", "Me çmime, e qartë dhe e lehtë për t'u lexuar në telefon — jo një PDF që s'hapet.", icon_menu),
    ("Lokacioni & orari", "Lidhur me Google Maps. Klienti të gjen me një prekje dhe e di kur je hapur.", icon_pin),
    ("Rezervim me një klik", "Një buton i dukshëm për rezervim ose porosi — pa kërkuar, pa pritur.", icon_button),
    ("E shpejtë në telefon", "Shumica e klientëve vijnë nga celulari. Faqja duhet të hapet menjëherë dhe të duket bukur.", icon_phone),
]
N = len(ITEMS) + 2

def slide_hook():
    img, d = base(True)
    for k in range(2):
        cx = M + 22 + k*64; d.ellipse([cx-22, 290-22, cx+22, 290+22], fill=PIKA)
    y = lines_draw(d, ["4 gjëra që", "uebfaqja e", "restorantit tënd", "duhet t'i ketë"], F_HUGE, M, 370, LIGHT, accent="restorantit")
    d.text((M, y+40), "Sa prej tyre i ke ti sot?", font=F_BODY, fill=GREY)
    d.text((M, y+120), "Rrëshqit  →", font=F_MED, fill=PIKA)
    footer(d, 1, N, True); return img

def slide_item(i, title, desc, icon):
    img, d = base(False)
    # numri i madh
    num = f"0{i}"
    d.text((M-8, 170), num, font=F_NUM, fill=PIKA)
    # karta me ikonën
    cx, cy = W - M - 190, 320
    d.ellipse([cx-190, cy-190, cx+190, cy+190], fill=LIGHT, outline=LINE, width=4)
    icon(d, cx, cy)
    y = 610
    y = lines_draw(d, wrap(d, title, F_TITLE, W-2*M), F_TITLE, M, y, INK, lh=1.08)
    d.line([(M, y+30), (M+160, y+30)], fill=PIKA, width=8)
    y += 90
    bl = wrap(d, desc, F_BODY, W-2*M-100)
    lh = int(F_BODY.size*1.45)
    ch = len(bl)*lh + 100
    d.rounded_rectangle([M, y, W-M, y+ch], radius=28, fill=WHITE, outline=LINE, width=3)
    ty = y + 50
    for ln in bl:
        d.text((M+50, ty), ln, font=F_BODY, fill=INK); ty += lh
    # chip "✓ e ke?"
    chip = "A e ke këtë?"; cw = d.textlength(chip, font=F_CHIP)
    cy2 = y + ch + 40
    d.rounded_rectangle([M, cy2, M+cw+120, cy2+76], radius=38, fill=DETI)
    d.ellipse([M+20, cy2+16, M+64, cy2+60], fill=WHITE)
    d.line([(M+31, cy2+38), (M+40, cy2+48), (M+54, cy2+29)], fill=DETI, width=6)
    d.text((M+84, cy2+16), chip, font=F_CHIP, fill=WHITE)
    footer(d, i+1, N, False); return img

def slide_cta():
    img, d = base(True)
    logo(d, W/2, 260, font(FD, 150, 700), LIGHT)
    y = 520
    for ln in ["Të mungon", "ndonjëra?"]:
        tw = d.textlength(ln, font=F_BIG); d.text(((W-tw)/2, y), ln, font=F_BIG, fill=LIGHT); y += 100
    sub = "Ne ta ndërtojmë uebfaqen me të katërtat — për restorante & biznese lokale në Kosovë."
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
slides = [slide_hook()] + [slide_item(i+1, *it) for i, it in enumerate(ITEMS)] + [slide_cta()]
for i, s in enumerate(slides, 1):
    p = os.path.join(OUT, f"webpike-post-06-slide-{i}.jpg"); s.save(p, "JPEG", quality=92); print(p)
