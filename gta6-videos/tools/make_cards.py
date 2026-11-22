"""Generate 1080x1920 synthwave-style cards (original art, no game assets).

Usage: python make_cards.py spec.json OUT_DIR
spec.json: {"series": "...", "theme": "sunset|ocean|alert|night",
            "cards": [{"kicker": "...", "title": "...", "body": "..."}, ...]}
"""
import json
import math
import random
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H = 1080, 1920
FONT_DIR = "/usr/share/fonts"


def font(weight, size):
    names = {
        "black": "InterDisplay-Black",
        "bold": "InterDisplay-Bold",
        "semibold": "InterDisplay-SemiBold",
        "medium": "Inter-Medium",
    }
    for p in Path(FONT_DIR).rglob(f"{names[weight]}.*"):
        return ImageFont.truetype(str(p), size)
    return ImageFont.truetype("DejaVuSans-Bold.ttf", size)


THEMES = {
    "sunset": dict(sky=["#12052b", "#5b1a6e", "#ff2e88", "#ffb347"], sun=("#ffe066", "#ff4f9a"),
                   sea="#1b0f3d", accent="#ff2e88", accent2="#ffd166"),
    "ocean": dict(sky=["#03102b", "#0a3d62", "#14b8c4", "#a8f0e8"], sun=("#fff3b0", "#38e1d6"),
                  sea="#021a33", accent="#22d3ee", accent2="#fde68a"),
    "alert": dict(sky=["#0d0208", "#3b0a12", "#b3122e", "#ff7a3d"], sun=("#ffb199", "#ff2e3b"),
                  sea="#14050a", accent="#ff3b4f", accent2="#ffd0a8"),
    "night": dict(sky=["#020617", "#1e1b4b", "#7c3aed", "#f472b6"], sun=("#fbcfe8", "#a78bfa"),
                  sea="#0b0a24", accent="#a78bfa", accent2="#f9a8d4"),
}


def hex2rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def gradient(stops, height):
    cols = [hex2rgb(s) for s in stops]
    img = Image.new("RGB", (W, height))
    d = ImageDraw.Draw(img)
    n = len(cols) - 1
    for y in range(height):
        t = y / (height - 1) * n
        i = min(int(t), n - 1)
        d.line([(0, y), (W, y)], fill=lerp(cols[i], cols[i + 1], t - i))
    return img


def palm(d, x, base_y, h, lean, color, rng):
    # trunk
    pts = []
    for i in range(21):
        t = i / 20
        pts.append((x + lean * t * t * h * 0.35, base_y - t * h))
    for i in range(len(pts) - 1):
        w = int(22 - 12 * i / 20)
        d.line([pts[i], pts[i + 1]], fill=color, width=w)
    tx, ty = pts[-1]
    # fronds
    for k in range(9):
        ang = math.radians(-180 + k * 22.5 + rng.uniform(-6, 6))
        L = h * rng.uniform(0.38, 0.5)
        poly = []
        for s in range(13):
            t = s / 12
            px = tx + math.cos(ang) * L * t
            py = ty + math.sin(ang) * L * t + (L * 0.45) * t * t
            poly.append((px, py))
        for s in range(len(poly) - 1):
            d.line([poly[s], poly[s + 1]], fill=color, width=int(26 * (1 - s / 13)) + 3)


def background(theme, seed):
    th = THEMES[theme]
    rng = random.Random(seed)
    horizon = 1390
    img = gradient(th["sky"], H)
    d = ImageDraw.Draw(img, "RGBA")
    # stars
    for _ in range(140):
        x, y = rng.randint(0, W), rng.randint(0, 700)
        a = rng.randint(60, 200)
        r = rng.choice([1, 1, 2])
        d.ellipse([x - r, y - r, x + r, y + r], fill=(255, 255, 255, a))
    # striped sun
    cx, cy, R = W // 2 + rng.randint(-120, 120), horizon - 30, 300
    sun = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(sun)
    c1, c2 = hex2rgb(th["sun"][0]), hex2rgb(th["sun"][1])
    for y in range(cy - R, cy + R):
        t = (y - (cy - R)) / (2 * R)
        half = int(math.sqrt(max(R * R - (y - cy) ** 2, 0)))
        band = (y - (cy - R * 0.1)) % 46
        if y > cy - R * 0.1 and band < 10 + 18 * t:
            continue
        sd.line([(cx - half, y), (cx + half, y)], fill=lerp(c1, c2, t) + (255,))
    glow = sun.filter(ImageFilter.GaussianBlur(60))
    img.paste(glow, (0, 0), glow)
    img.paste(sun, (0, 0), sun)
    d = ImageDraw.Draw(img, "RGBA")
    # sea + perspective grid
    sea = hex2rgb(th["sea"])
    d.rectangle([0, horizon, W, H], fill=sea + (255,))
    acc = hex2rgb(th["accent"])
    for i in range(1, 22):
        y = horizon + (i ** 1.9) * 2.2
        if y > H:
            break
        d.line([(0, y), (W, y)], fill=acc + (110,), width=2)
    for k in range(-14, 15):
        d.line([(W / 2 + k * 18, horizon), (W / 2 + k * 260, H)], fill=acc + (80,), width=2)
    # sun reflection
    for i in range(14):
        y = horizon + 14 + i * 22
        w = 300 - i * 16 + rng.randint(-20, 20)
        d.line([(cx - w // 2, y), (cx + w // 2, y)], fill=hex2rgb(th["sun"][1]) + (90,), width=5)
    # skyline silhouette
    sil = (8, 4, 18, 255)
    x = 0
    while x < W:
        bw = rng.randint(40, 110)
        bh = rng.randint(40, 230) if not (W * 0.3 < x < W * 0.7) else rng.randint(20, 90)
        d.rectangle([x, horizon - bh, x + bw, horizon], fill=sil)
        x += bw + rng.randint(0, 8)
    # palms
    palm(d, 40, horizon + 30, 440, 0.9, sil, rng)
    palm(d, W - 50, horizon + 40, 380, -1.0, sil, rng)
    # darken top area for legibility
    shade = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sh = ImageDraw.Draw(shade)
    for y in range(0, 1300):
        a = int(170 * (1 - y / 1300) ** 1.1)
        sh.line([(0, y), (W, y)], fill=(0, 0, 0, a))
    img = Image.alpha_composite(img.convert("RGBA"), shade)
    return img


def wrap(d, text, f, maxw):
    lines = []
    for para in text.split("\n"):
        words, cur = para.split(), ""
        for w in words:
            t = (cur + " " + w).strip()
            if d.textlength(t, font=f) <= maxw:
                cur = t
            else:
                if cur:
                    lines.append(cur)
                cur = w
        lines.append(cur)
    return lines


def card(spec, i, n, theme, series, out):
    th = THEMES[theme]
    img = background(theme, seed=hash((series, i)) & 0xFFFF)
    d = ImageDraw.Draw(img, "RGBA")
    acc, acc2 = hex2rgb(th["accent"]), hex2rgb(th["accent2"])
    margin = 84
    # series pill
    f_pill = font("bold", 34)
    label = f"GTA 6  •  {series.upper()}"
    tw = d.textlength(label, font=f_pill)
    d.rounded_rectangle([margin, 150, margin + tw + 56, 222], radius=36, fill=acc + (235,))
    d.text((margin + 28, 186), label, font=f_pill, fill=(255, 255, 255), anchor="lm")
    # counter
    f_cnt = font("semibold", 34)
    d.text((W - margin, 186), f"{i + 1:02d}/{n:02d}", font=f_cnt, fill=(255, 255, 255, 210), anchor="rm")
    y = 330
    if spec.get("kicker"):
        f_k = font("bold", 44)
        d.text((margin, y), spec["kicker"].upper(), font=f_k, fill=acc2)
        y += 78
    # title
    size = spec.get("title_size", 108)
    f_t = font("black", size)
    lines = wrap(d, spec["title"], f_t, W - 2 * margin)
    while len(lines) > 4 and size > 70:
        size -= 8
        f_t = font("black", size)
        lines = wrap(d, spec["title"], f_t, W - 2 * margin)
    for ln in lines:
        # neon glow
        glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(glow).text((margin, y), ln, font=f_t, fill=acc + (200,))
        glow = glow.filter(ImageFilter.GaussianBlur(14))
        img = Image.alpha_composite(img, glow)
        d = ImageDraw.Draw(img, "RGBA")
        d.text((margin, y), ln, font=f_t, fill=(255, 255, 255))
        y += int(size * 1.08)
    # accent bar
    y += 24
    d.rectangle([margin, y, margin + 140, y + 10], fill=acc2)
    y += 50
    if spec.get("body"):
        f_b = font("semibold", 50)
        for ln in wrap(d, spec["body"], f_b, W - 2 * margin):
            d.text((margin, y), ln, font=f_b, fill=(255, 255, 255, 235))
            y += 66
    if spec.get("source"):
        f_s = font("medium", 30)
        st = "Fonte: " + spec["source"]
        y += 18
        d.text((margin, y), st, font=f_s, fill=(255, 255, 255, 175))
    img.convert("RGB").save(out, quality=94)


def main():
    spec = json.loads(Path(sys.argv[1]).read_text())
    outdir = Path(sys.argv[2])
    outdir.mkdir(parents=True, exist_ok=True)
    n = len(spec["cards"])
    paths = []
    for i, c in enumerate(spec["cards"]):
        p = outdir / f"card_{i + 1:02d}.jpg"
        card(c, i, n, spec.get("theme", "sunset"), spec["series"], p)
        paths.append(str(p))
    print(",".join(paths))


if __name__ == "__main__":
    main()
