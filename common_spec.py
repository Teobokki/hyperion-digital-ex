datas = [('assets', 'assets')]
EXC = ['numpy', 'cv2', 'panda3d', 'direct', 'fitz', 'pymupdf', 'webview', 'clr', 'pythonnet', 'imageio_ffmpeg', 'PIL',
       'matplotlib', 'scipy', 'pandas', 'IPython', 'pytest', 'PyQt5', 'wx', 'bottle', 'comtypes', 'winpty', 'tkinter',
       'PySide6.QtNetwork', 'PySide6.QtQml', 'PySide6.QtQuick', 'PySide6.QtOpenGL', 'PySide6.QtSql', 'PySide6.QtTest',
       'PySide6.QtDBus', 'PySide6.QtPdf', 'PySide6.QtSvg', 'PySide6.QtXml', 'PySide6.QtConcurrent', 'PySide6.QtPrintSupport']
# 1.1.15: resilient catalog/latest.json mirrors (jsDelivr/gitHack) + IPv4 prefer for Windows DNS 11001; prior 1.1.14 COKA pin; 1.1.13 TLS truststore/certifi
from PyInstaller.utils.hooks import collect_data_files
datas += collect_data_files('certifi')
HID = ['truststore', 'certifi']
