"""Builds bundled store art from each EX app's REAL local icon/screenshots (no generated art),
plus the HYPERION DIGITAL EX 'H' monogram icon drawn in code."""
import os, json
from PIL import Image, ImageDraw, ImageFont, ImageFilter
W = '/workspace'
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'assets')
SRC = {
 'dream-vine': ('dream-vine/assets/icon.png', ['dream-vine/docs/screenshot_title_v103.png','dream-vine/docs/screenshot_ingame_terrain.png','dream-vine/docs/screenshot_vinebuild_castle.png','dream-vine/docs/screenshot_night_gloomer.png','dream-vine/docs/screenshot_crafting.png','dream-vine/docs/screenshot_vinebuild_temple.png']),
 'piknott-celestika': ('piknott-celestika/assets/icon.png', ['piknott-celestika/assets/cover.jpg','piknott-celestika/docs/screenshot_overworld.png','piknott-celestika/docs/screenshot_battle.png','piknott-celestika/docs/screenshot_catch_wobble.png','piknott-celestika/docs/screenshot_team.png','piknott-celestika/docs/screenshot_map.png','piknott-celestika/docs/screenshot_celestika_dok.png']),
 'fireout-revolution': ('fireout-revolution/logo256.png', ['fireout-revolution/logo256.png']),
 'hyperia': ('hyperia/repo/logo256.png', ['hyperia/repo/logo.jpg', ('hyperia/screenshot.png', (225, 0, 1280, 800))]),
 'ex-creator-studio': ('ex-creator-studio/assets/logo256.png', ['ex-creator-studio/docs/screenshot_character.png','ex-creator-studio/docs/screenshot_board_shots.png','ex-creator-studio/docs/screenshot_ex_studio.png','ex-creator-studio/docs/screenshot_rex_board.png']),
 'ex-network': ('exwifi/repo/logo256.png', ['exwifi/screenshot.png']),
 'ex-sudo-terminal': ('exsudo/repo/logo256.png', ['exsudo/screenshot.png']),
 'dream-vine-launcher': ('dream-vine-launcher/assets/icon256.png', ['dream-vine-launcher/docs/screenshot_play.png','dream-vine-launcher/docs/screenshot_installations.png','dream-vine-launcher/docs/screenshot_first_run_setup.png','dream-vine-launcher/docs/screenshot_settings.png']),
}
EXTRA = json.load(open(os.path.join(OUT, 'extra_shots.json'))) if os.path.exists(os.path.join(OUT, 'extra_shots.json')) else {}

def cover(im, size, right=False):
    """fit an image into size: square/small art is centred over a blurred, darkened copy of itself."""
    tw, th = size
    im = im.convert('RGB')
    w, h = im.size
    if abs(w / h - tw / th) < 0.25 and w >= tw * 0.5:
        s = max(tw / w, th / h); im2 = im.resize((int(w * s + .5), int(h * s + .5)), Image.LANCZOS)
        l = (im2.width - tw) // 2; t = (im2.height - th) // 2
        return im2.crop((l, t, l + tw, t + th))
    s = max(tw / w, th / h); bg = im.resize((int(w * s + 1), int(h * s + 1)), Image.LANCZOS)
    l = (bg.width - tw) // 2; t = (bg.height - th) // 2
    bg = bg.crop((l, t, l + tw, t + th)).filter(ImageFilter.GaussianBlur(28))
    bg = Image.blend(bg, Image.new('RGB', bg.size, (10, 14, 22)), 0.55)
    s = min(tw / w, th / h) * 0.92; fg = im.resize((int(w * s), int(h * s)), Image.LANCZOS)
    bg.paste(fg, ((tw - fg.width - int(tw * 0.06)) if right else (tw - fg.width) // 2, (th - fg.height) // 2))
    return bg

def load(spec):
    if isinstance(spec, (list, tuple)):
        return Image.open(os.path.join(W, spec[0])).crop(tuple(spec[1]))
    return Image.open(os.path.join(W, spec))

for app, (icon, shots) in SRC.items():
    d = os.path.join(OUT, 'apps', app); os.makedirs(d, exist_ok=True)
    for f in os.listdir(d): os.remove(os.path.join(d, f))
    ic = Image.open(os.path.join(W, icon)).convert('RGBA'); ic.thumbnail((256, 256), Image.LANCZOS); ic.save(os.path.join(d, 'icon.png'))
    shots = list(shots) + EXTRA.get(app, [])
    ims = [load(s) for s in shots]
    for i, im in enumerate(ims):
        im = im.convert('RGB')
        if im.width > 1280: im = im.resize((1280, int(im.height * 1280 / im.width)), Image.LANCZOS)
        im.save(os.path.join(d, 'shot%d.jpg' % i), quality=86)
    hero_src = ims[0]
    cover(hero_src, (1600, 600), right=True).save(os.path.join(d, 'hero.jpg'), quality=86)
    cover(ims[1] if len(ims) > 1 and app not in ('piknott-celestika', 'hyperia') else ims[0], (616, 353)).save(os.path.join(d, 'capsule.jpg'), quality=88)

# ---- app icon: the user's own artwork (see tools/make_icon.py) ----
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'make_icon.py')).read())
print('assets ok')
