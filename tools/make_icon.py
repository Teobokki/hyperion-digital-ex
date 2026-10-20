"""App icon from the user's artwork (assets/icon_source_user.png): white background made transparent by
flood-filling from the corners only; white inner details (d-pad, buttons, rope stripes) are kept."""
import os
from PIL import Image, ImageDraw, ImageFilter, ImageChops
A = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'assets')
src = Image.open(os.path.join(A, 'icon_source_user.png')).convert('RGBA')
W, H = src.size
# The file's white areas are transparent (it shows as white on a white page). Outside = transparent region
# reachable from the corners. Inner details (d-pad, buttons, rope gaps) are given their white back.
a = src.getchannel('A')
m = Image.eval(a, lambda v: 255 if v >= 128 else 0).convert('RGB')
for c in [(0, 0), (W - 1, 0), (0, H - 1), (W - 1, H - 1)]:
    if m.getpixel(c) == (0, 0, 0):
        ImageDraw.floodfill(m, c, (0, 255, 0), thresh=0)
outside = Image.eval(ImageChops.difference(m, Image.new('RGB', (W, H), (0, 255, 0))).convert('L'), lambda v: 255 if v < 8 else 0)
shape = Image.eval(outside, lambda v: 255 - v)
# the rope's white stripes open onto the outside, so close narrow gaps (they become the same white)
k = 13
closed = shape.filter(ImageFilter.MaxFilter(k)).filter(ImageFilter.MinFilter(k))
closed = ImageChops.lighter(closed, a)
# fill any remaining fully enclosed holes
cm = closed.convert('RGB')
ImageDraw.floodfill(cm, (0, 0), (0, 255, 0), thresh=100)
closed = Image.eval(ImageChops.difference(cm, Image.new('RGB', (W, H), (0, 255, 0))).convert('L'), lambda v: 0 if v < 8 else 255)
closed = ImageChops.lighter(Image.eval(closed, lambda v: v), a)
white = Image.new('RGBA', (W, H), (255, 255, 255, 255)); white.putalpha(closed)
out = Image.alpha_composite(white, src)
alpha = out.getchannel('A')
bbox = alpha.getbbox()
out = out.crop(bbox)
side = max(out.size) + 8
sq = Image.new('RGBA', (side, side), (0, 0, 0, 0)); sq.paste(out, ((side - out.width) // 2, (side - out.height) // 2))
sq.save(os.path.join(A, 'icon_user_transparent.png'))
sq.resize((256, 256), Image.LANCZOS).save(os.path.join(A, 'icon256.png'))
sq.resize((64, 64), Image.LANCZOS).save(os.path.join(A, 'icon64.png'))
sq.resize((256, 256), Image.LANCZOS).save(os.path.join(A, 'icon.ico'), sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
# preview on dark + light
pv = Image.new('RGB', (side * 2, side), (14, 19, 25)); pv.paste(Image.new('RGB', (side, side), (230, 230, 230)), (side, 0))
pv.paste(sq, (0, 0), sq); pv.paste(sq, (side, 0), sq); pv.save('/tmp/sm/icon_preview3.png')
print('ok', bbox, side)
