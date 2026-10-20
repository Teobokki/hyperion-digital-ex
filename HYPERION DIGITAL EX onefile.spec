# -*- mode: python ; coding: utf-8 -*-
exec(open('common_spec.py').read())
a = Analysis(['hyperion_digital_ex.py'], datas=datas, excludes=EXC, noarchive=False)
pyz = PYZ(a.pure)
exe = EXE(pyz, a.scripts, a.binaries, a.datas, [], name='HYPERION DIGITAL EX', console=False, upx=False, runtime_tmpdir=None, version='version.txt', icon=['assets/icon.ico'])
