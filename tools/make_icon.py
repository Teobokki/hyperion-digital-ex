"""Build the HYPERION DIGITAL EX app icon from assets/icon_source_3.0.jpg
(white brush H on black). Crops tight around the H, keeps a black square
background, and writes a Windows-compatible .ico: 16/24/32/48/64/128 as
32bpp DIB (plus AND mask) and 256 as PNG.
©2026 EX Inc./HYPERION DIGITAL ©2026"""
import io, os, struct
from PIL import Image

A = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets")
SRC = os.path.join(A, "icon_source_3.0.jpg")
SIZES_DIB = (16, 24, 32, 48, 64, 128)
SIZE_PNG = 256


def _bbox(im, thresh=16):
    w, h = im.size
    px = im.load()
    minx, miny, maxx, maxy = w, h, 0, 0
    for y in range(h):
        for x in range(w):
            r, g, b = px[x, y][:3]
            if r + g + b > thresh:
                if x < minx: minx = x
                if y < miny: miny = y
                if x > maxx: maxx = x
                if y > maxy: maxy = y
    if maxx < minx:
        return (0, 0, w, h)
    return (minx, miny, maxx + 1, maxy + 1)


def _square_crop(im, pad_frac=0.16):
    """Crop a square around the H, padded, keeping the black background."""
    box = _bbox(im.convert("RGB"), 16)
    x0, y0, x1, y1 = box
    bw, bh = x1 - x0, y1 - y0
    cx, cy = (x0 + x1) / 2.0, (y0 + y1) / 2.0
    side = int(round(max(bw, bh) * (1 + 2 * pad_frac)))
    if side % 2:
        side += 1
    w, h = im.size
    sx = int(round(cx - side / 2.0))
    sy = int(round(cy - side / 2.0))
    sx = max(0, min(sx, w - side))
    sy = max(0, min(sy, h - side))
    return im.crop((sx, sy, sx + side, sy + side)), (sx, sy, sx + side, sy + side, side)


def _crush_black(im, thresh=18):
    """Force near-black JPEG noise to pure black; leave the H's AA alone."""
    im = im.convert("RGB")
    px = im.load()
    w, h = im.size
    for y in range(h):
        for x in range(w):
            r, g, b = px[x, y]
            if r + g + b <= thresh:
                px[x, y] = (0, 0, 0)
    return im


def _png_bytes(im):
    buf = io.BytesIO()
    im.convert("RGBA").save(buf, format="PNG")
    return buf.getvalue()


def _dib32(im):
    """32bpp BITMAPINFOHEADER + bottom-up BGRA XOR + 1bpp AND mask."""
    im = im.convert("RGBA")
    w, h = im.size
    pixels = list(im.getdata())
    xor = bytearray()
    and_rows = []
    and_row_sz = ((w + 31) // 32) * 4
    for y in range(h - 1, -1, -1):
        row_and = bytearray(and_row_sz)
        for x in range(w):
            r, g, b, a = pixels[y * w + x]
            xor += bytes((b, g, r, a))
            if a < 128:
                row_and[x // 8] |= 0x80 >> (x % 8)
        and_rows.append(row_and)
    and_mask = b"".join(and_rows)
    header = struct.pack(
        "<IIIHHIIIIII",
        40, w, h * 2, 1, 32, 0, len(xor), 0, 0, 0, 0,
    )
    return header + xor + and_mask


def write_ico(path, images):
    entries, blobs = [], []
    for im in images:
        im = im.convert("RGBA")
        w, h = im.size
        blob = _png_bytes(im) if (w, h) == (SIZE_PNG, SIZE_PNG) else _dib32(im)
        entries.append((w, h, blob))
        blobs.append(blob)
    offset = 6 + 16 * len(entries)
    out = bytearray(struct.pack("<HHH", 0, 1, len(entries)))
    for w, h, blob in entries:
        out += struct.pack(
            "<BBBBHHII",
            0 if w >= 256 else w,
            0 if h >= 256 else h,
            0, 0, 1, 32, len(blob), offset,
        )
        offset += len(blob)
    for blob in blobs:
        out += blob
    with open(path, "wb") as f:
        f.write(out)


def main():
    src = Image.open(SRC).convert("RGB")
    crop, info = _square_crop(src, pad_frac=0.16)
    crop = _crush_black(crop)
    master = crop.resize((1024, 1024), Image.Resampling.LANCZOS)
    master = _crush_black(master)
    rgba = master.convert("RGBA")  # opaque black square
    icon256 = rgba.resize((256, 256), Image.Resampling.LANCZOS)
    icon64 = rgba.resize((64, 64), Image.Resampling.LANCZOS)
    icon256.save(os.path.join(A, "icon256.png"))
    icon64.save(os.path.join(A, "icon64.png"))
    frames = [rgba.resize((s, s), Image.Resampling.LANCZOS) for s in SIZES_DIB]
    frames.append(icon256)
    ico_path = os.path.join(A, "icon.ico")
    write_ico(ico_path, frames)
    print("source", src.size, "crop", info, "->", ico_path)


if __name__ == "__main__":
    main()
