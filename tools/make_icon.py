"""App icon from the user's logo (assets/icon_source_user_h.png: yellow square, black border, black slanted H).
The old controller artwork (icon_source_user.png) is kept in assets but no longer used."""
import os
from PIL import Image
A = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'assets')
src = Image.open(os.path.join(A, 'icon_source_user_h.png')).convert('RGBA')
bbox = src.getchannel('A').getbbox()
if bbox:
    src = src.crop(bbox)
side = max(src.size)
sq = Image.new('RGBA', (side, side), (0, 0, 0, 0)); sq.paste(src, ((side - src.width) // 2, (side - src.height) // 2))
sq.save(os.path.join(A, 'icon_user_transparent.png'))
sq.resize((256, 256), Image.LANCZOS).save(os.path.join(A, 'icon256.png'))
sq.resize((64, 64), Image.LANCZOS).save(os.path.join(A, 'icon64.png'))
sq.resize((256, 256), Image.LANCZOS).save(os.path.join(A, 'icon.ico'), sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
print('ok', sq.size)
