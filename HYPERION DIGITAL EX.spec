# -*- mode: python ; coding: utf-8 -*-
exec(open('common_spec.py').read())
a = Analysis(['hyperion_digital_ex.py'], datas=datas, hiddenimports=HID, excludes=EXC, noarchive=False)
pyz = PYZ(a.pure)
exe = EXE(pyz, a.scripts, [], exclude_binaries=True, name='HYPERION DIGITAL EX', console=False, upx=False, version='version.txt', icon=['assets/icon.ico'])
coll = COLLECT(exe, a.binaries, a.datas, upx=False, name='HYPERION DIGITAL EX')
