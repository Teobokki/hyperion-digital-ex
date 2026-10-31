set -e
export WINEPREFIX=/workspace/exwifi/.wine WINEDEBUG=-all
cd /workspace/hyperion-digital-ex
PY='C:\Python311\python.exe'
V=1.1.13
wine "$PY" -m PyInstaller --noconfirm "HYPERION DIGITAL EX.spec" > build_dir.log 2>&1; echo DIR_DONE
wine "C:\\InnoSetup\\ISCC.exe" installer.iss > build_iss.log 2>&1; echo ISS_DONE
wine "$PY" -m PyInstaller --noconfirm --workpath build_onefile --distpath dist_onefile "HYPERION DIGITAL EX onefile.spec" > build_1f.log 2>&1
cp "dist_onefile/HYPERION DIGITAL EX.exe" dist/HYPERION.DIGITAL.EX.Portable.exe; echo ONEFILE_DONE
cd dist && rm -f HYPERION.DIGITAL.EX.$V.Windows.x64.zip && python3 -c "import shutil;shutil.make_archive('HYPERION.DIGITAL.EX.'+'$V'+'.Windows.x64','zip','.','HYPERION DIGITAL EX')" && echo ZIP_DONE
sha256sum HYPERION.DIGITAL.EX.Portable.exe HYPERION.DIGITAL.EX.Setup.$V.exe HYPERION.DIGITAL.EX.$V.Windows.x64.zip
