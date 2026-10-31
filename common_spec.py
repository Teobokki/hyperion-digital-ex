datas = [('assets', 'assets')]
EXC = ['numpy', 'cv2', 'panda3d', 'direct', 'fitz', 'pymupdf', 'webview', 'clr', 'pythonnet', 'imageio_ffmpeg', 'PIL',
       'matplotlib', 'scipy', 'pandas', 'IPython', 'pytest', 'PyQt5', 'wx', 'bottle', 'comtypes', 'winpty', 'tkinter',
       'PySide6.QtNetwork', 'PySide6.QtQml', 'PySide6.QtQuick', 'PySide6.QtOpenGL', 'PySide6.QtSql', 'PySide6.QtTest',
       'PySide6.QtDBus', 'PySide6.QtPdf', 'PySide6.QtSvg', 'PySide6.QtXml', 'PySide6.QtConcurrent', 'PySide6.QtPrintSupport']
# 1.1.13: TLS trust - certifi's CA bundle as data + truststore (Windows certificate store verification)
from PyInstaller.utils.hooks import collect_data_files
datas += collect_data_files('certifi')
HID = ['truststore', 'certifi']
