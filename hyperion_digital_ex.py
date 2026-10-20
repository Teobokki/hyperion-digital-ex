"""HYPERION DIGITAL EX - the EX Inc. store and library. EX CONNECT installs and plays every EX app right here.
©2026 EX Inc./HYPERION DIGITAL ©2026"""
import os, sys, time, json, subprocess, webbrowser
from PySide6.QtCore import Qt, QObject, Signal, QTimer, QRectF, QPointF, QSize, QUrl
from PySide6.QtGui import (QPixmap, QPainter, QColor, QLinearGradient, QFont, QIcon, QPainterPath, QBrush, QPen,
                           QDesktopServices, QFontDatabase)
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QLabel, QPushButton, QHBoxLayout, QVBoxLayout,
                               QGridLayout, QStackedWidget, QScrollArea, QFrame, QLineEdit, QProgressBar, QListWidget,
                               QListWidgetItem, QMessageBox, QDialog, QFileDialog, QCheckBox, QComboBox, QSizePolicy, QToolButton)
import ex_connect as xc
from ex_catalog import GAMES, APPS, UPCOMING
SOON = {a["id"]: a for a in UPCOMING}

APP_NAME = "HYPERION DIGITAL EX"
APP_VERSION = xc.APP_VERSION
PUBLISHER = "EX Inc./HYPERION DIGITAL"
COPYRIGHT = "\u00a92026 EX Inc./HYPERION DIGITAL \u00a92026"
RELEASES = "https://github.com/Teobokki/hyperion-digital-ex/releases/latest"

BG = "#0e1319"; BG2 = "#131a22"; PANEL = "#18212b"; PANEL2 = "#1f2a36"; LINE = "#2a3746"
FG = "#e8eef5"; MUTED = "#8fa1b3"; ACCENT = "#5cb8ff"; GREEN = "#6fbf2a"; GREEN2 = "#4f9a14"; ORANGE = "#f0a63a"; RED = "#e5534b"


def res(*p):
    return os.path.join(getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__))), *p)


def art(aid, name):
    return res("assets", "apps", aid, name)


def shots(aid):
    d = res("assets", "apps", aid)
    return sorted([os.path.join(d, f) for f in os.listdir(d) if f.startswith("shot")], key=lambda p: int(p.rsplit("shot", 1)[1].split(".")[0]))


_PIX = {}


def pix(path):
    if path not in _PIX:
        _PIX[path] = QPixmap(path)
    return _PIX[path]


def cover_pix(p, w, h, radius=0):
    """scale/crop pixmap to fill w x h"""
    if p.isNull():
        out = QPixmap(w, h); out.fill(QColor(PANEL)); return out
    s = p.scaled(w, h, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
    s = s.copy((s.width() - w) // 2, (s.height() - h) // 2, w, h)
    if not radius:
        return s
    out = QPixmap(w, h); out.fill(Qt.transparent)
    qp = QPainter(out); qp.setRenderHint(QPainter.Antialiasing)
    path = QPainterPath(); path.addRoundedRect(QRectF(0, 0, w, h), radius, radius)
    qp.setClipPath(path); qp.drawPixmap(0, 0, s); qp.end()
    return out


QSS = f"""
* {{ font-family: 'Segoe UI', 'Yu Gothic UI', 'Meiryo', 'MS Gothic', 'Arial'; color: {FG}; }}
QMainWindow, #root {{ background: {BG}; }}
QScrollArea, QScrollArea > QWidget > QWidget {{ background: transparent; border: none; }}
QScrollBar:vertical {{ background: {BG}; width: 10px; margin: 0; }}
QScrollBar::handle:vertical {{ background: #2c3a49; border-radius: 5px; min-height: 30px; }}
QScrollBar::add-line, QScrollBar::sub-line {{ height: 0; }}
QScrollBar:horizontal {{ background: {BG}; height: 10px; }}
QScrollBar::handle:horizontal {{ background: #2c3a49; border-radius: 5px; }}
#topbar {{ background: qlineargradient(x1:0,y1:0,x2:0,y2:1, stop:0 #17202b, stop:1 #111821); border-bottom: 1px solid {LINE}; }}
#brand {{ font-size: 17px; font-weight: 800; letter-spacing: 2px; }}
#brandsub {{ font-size: 17px; font-weight: 300; letter-spacing: 2px; color: {ACCENT}; }}
QPushButton#nav {{ background: transparent; border: none; font-size: 14px; font-weight: 700; color: {MUTED}; padding: 8px 8px; }}
QPushButton#nav:hover {{ color: {FG}; }}
QPushButton#nav[active="true"] {{ color: {ACCENT}; border-bottom: 2px solid {ACCENT}; }}
QLineEdit {{ background: {PANEL}; border: 1px solid {LINE}; border-radius: 6px; padding: 7px 10px; color: {FG}; selection-background-color: {ACCENT}; }}
QLineEdit:focus {{ border: 1px solid {ACCENT}; }}
QPushButton {{ background: {PANEL2}; border: 1px solid {LINE}; border-radius: 5px; padding: 7px 14px; font-weight: 600; }}
QPushButton:hover {{ background: #283646; }}
QPushButton:disabled {{ color: #6b7a89; }}
QPushButton#primary {{ background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 {GREEN}, stop:1 {GREEN2}); border: none; font-size: 15px; font-weight: 800; letter-spacing: 1px; padding: 10px 26px; color: white; }}
QPushButton#primary:disabled {{ background: #2a3a4c; color: #b7c6d6; }}
QPushButton#primary[mode="playing"]:disabled {{ background: #2f7a40; color: #d8ffc8; }}
QPushButton#primary:hover {{ background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #82d93a, stop:1 #5cb01a); }}
QPushButton#primary[mode="update"] {{ background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #4aa8ff, stop:1 #2f7fd6); }}
QPushButton#primary[mode="busy"] {{ background: #2a3a4c; color: {MUTED}; }}
QPushButton#primary[mode="playing"] {{ background: #2f7a40; color: #d8ffc8; }}
QPushButton#ghost {{ background: transparent; border: 1px solid {LINE}; color: {MUTED}; }}
QPushButton#ghost:hover {{ color: {FG}; border-color: {ACCENT}; }}
QPushButton#link {{ background: transparent; border: none; color: {ACCENT}; padding: 2px; font-weight: 600; }}
QPushButton#badge {{ background: #13261a; border: 1px solid #2d6b3c; border-radius: 13px; padding: 4px 12px; font-weight: 700; color: #9be57c; }}
QPushButton#badge[off="true"] {{ background: #2a1717; border-color: #6b2d2d; color: #f29a9a; }}
QPushButton#update {{ background: #2f7fd6; border: none; border-radius: 13px; padding: 4px 12px; font-weight: 700; }}
QProgressBar {{ background: #0b1016; border: 1px solid {LINE}; border-radius: 4px; height: 10px; text-align: center; font-size: 10px; }}
QProgressBar::chunk {{ background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #3d8fe0, stop:1 {ACCENT}); border-radius: 3px; }}
#h1 {{ font-size: 30px; font-weight: 800; }}
#h2 {{ font-size: 13px; font-weight: 800; letter-spacing: 2px; color: {MUTED}; }}
#muted {{ color: {MUTED}; }}
#small {{ color: {MUTED}; font-size: 11px; }}
#card {{ background: {PANEL}; border: 1px solid {LINE}; border-radius: 8px; }}
#card:hover {{ background: {PANEL2}; border: 1px solid {ACCENT}; }}
#panel {{ background: {PANEL}; border: 1px solid {LINE}; border-radius: 8px; }}
#infobox {{ background: rgba(0,0,0,0.25); border-radius: 6px; }}
QListWidget {{ background: {BG2}; border: none; outline: none; }}
QListWidget::item {{ padding: 6px 8px; border-radius: 4px; color: {MUTED}; }}
QListWidget::item:selected {{ background: #24364a; color: {FG}; }}
QListWidget::item:hover {{ background: #1a2633; color: {FG}; }}
#footer {{ background: #0a0e13; border-top: 1px solid {LINE}; }}
QCheckBox, QComboBox {{ font-size: 13px; }}
QComboBox {{ background: {PANEL}; border: 1px solid {LINE}; border-radius: 5px; padding: 6px 10px; }}
QComboBox QAbstractItemView {{ background: {PANEL}; selection-background-color: #24364a; }}
QMessageBox {{ background: {PANEL}; }}
QToolTip {{ background: {PANEL2}; color: {FG}; border: 1px solid {LINE}; }}
"""


class Bridge(QObject):
    event = Signal(str, str)


class ClickLabel(QLabel):
    clicked = Signal()

    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            self.clicked.emit()


def fit(b):
    """never let a top-bar button shrink below its text (no clipped labels)"""
    b.ensurePolished(); b.setMinimumWidth(b.sizeHint().width())


def lbl(text, name=None, wrap=False):
    l = QLabel(text)
    if name:
        l.setObjectName(name)
    l.setWordWrap(wrap)
    return l


# ---------------------------------------------------------------- action bar (Install / Play / Update / progress)
class ActionBar(QWidget):
    def __init__(self, ui, aid, big=True, uninstall=True):
        super().__init__()
        self.ui, self.svc, self.aid = ui, ui.svc, aid; self.allow_uninst = uninstall
        v = QVBoxLayout(self); v.setContentsMargins(0, 0, 0, 0); v.setSpacing(6)
        row = QHBoxLayout(); row.setSpacing(8)
        self.main = QPushButton("INSTALL"); self.main.setObjectName("primary"); self.main.setCursor(Qt.PointingHandCursor)
        self.main.setMinimumWidth(170 if big else 120); self.main.clicked.connect(self.on_main)
        self.pause = QPushButton("Pause"); self.pause.setObjectName("ghost"); self.pause.clicked.connect(self.on_pause)
        self.cancel = QPushButton("Cancel"); self.cancel.setObjectName("ghost"); self.cancel.clicked.connect(lambda: self.svc.cancel(self.aid))
        self.uninst = QPushButton("Uninstall"); self.uninst.setObjectName("ghost"); self.uninst.clicked.connect(self.on_uninstall)
        row.addWidget(self.main); row.addWidget(self.pause); row.addWidget(self.cancel); row.addStretch(1); row.addWidget(self.uninst)
        v.addLayout(row)
        self.bar = QProgressBar(); self.bar.setRange(0, 1000); self.bar.setTextVisible(False); self.bar.setFixedHeight(10)
        self.info = lbl("", "small", True)
        v.addWidget(self.bar); v.addWidget(self.info)
        self.refresh()

    def refresh(self):
        st = self.svc.status(self.aid); j = self.svc.job_for(self.aid); inf = self.svc.installed.get(self.aid)
        latest = self.svc.latest_version(self.aid)
        text = {"install": "INSTALL", "play": "PLAY", "update": "UPDATE", "playing": "PLAYING", "queued": "QUEUED",
                "downloading": "DOWNLOADING", "paused": "RESUME", "verifying": "VERIFYING", "installing": "INSTALLING", "error": "RETRY"}[st]
        mode = {"update": "update", "playing": "playing", "queued": "busy", "downloading": "busy", "verifying": "busy", "installing": "busy"}.get(st, "")
        if st == "update":
            text = "UPDATE TO %s" % latest
        self.main.setText(("\u25B6  " if st == "play" else ("\u2B06  " if st == "update" else "")) + text)
        if self.main.property("mode") != mode:
            self.main.setProperty("mode", mode); self.main.style().unpolish(self.main); self.main.style().polish(self.main)
        self.main.setEnabled(st not in ("queued", "downloading", "verifying", "installing", "playing"))
        active = st in ("queued", "downloading", "paused", "verifying", "installing", "error")
        self.pause.setVisible(st in ("queued", "downloading")); self.cancel.setVisible(st in ("queued", "downloading", "paused", "error"))
        self.uninst.setVisible(self.allow_uninst and bool(inf) and not active and st != "playing")
        self.bar.setVisible(active)
        if j:
            self.bar.setValue(int(j.fraction * 1000))
            if st == "installing":
                self.bar.setRange(0, 0)
            else:
                self.bar.setRange(0, 1000)
            self.info.setText(job_text(j))
        elif st == "playing":
            self.info.setText("EX CONNECT: running %s · this session %s" % (self.svc.catalog[self.aid]["name"], xc.human_time(time.time() - self.svc.running[self.aid][1])))
        elif inf:
            if st == "update":
                old = self.svc.outdated_copies(self.aid)
                copies = ", ".join("%s %s" % ("Portable" if k == "portable" else "Installed", v or "?") for k, _e, v in old)
                self.info.setText("Update available: %s  ·  you have %s  ·  EX CONNECT updates every copy" % (latest, copies))
                self.info.setStyleSheet("color:%s;font-weight:700" % ACCENT)
            else:
                self.info.setStyleSheet("")
                self.info.setText("Installed %s (%s)  ·  Up to date  ·  Play time %s" % (inf["version"], inf["source"], xc.human_time(self.svc.playtime(self.aid))))
        else:
            self.info.setText("Free  ·  %s download  ·  Version %s  ·  installs with EX CONNECT" % (self.svc.size_text(self.aid), latest))

    def on_main(self):
        st = self.svc.status(self.aid)
        if st == "install":
            self.svc.install(self.aid)
        elif st == "update":
            self.svc.install(self.aid, update=True)
        elif st == "play":
            try:
                self.svc.play(self.aid)
            except Exception as e:
                QMessageBox.warning(self, APP_NAME, "Could not start %s:\n%s" % (self.svc.catalog[self.aid]["name"], e))
        elif st in ("paused", "error"):
            self.svc.resume(self.aid)
        self.ui.refresh_all()

    def on_pause(self):
        self.svc.pause(self.aid)

    def on_uninstall(self):
        a = self.svc.catalog[self.aid]; inf = self.svc.installed.get(self.aid) or {}
        if QMessageBox.question(self, APP_NAME, "Uninstall %s?\n\n%s" % (a["name"], inf.get("exe", ""))) == QMessageBox.Yes:
            self.svc.uninstall(self.aid)


def job_text(j):
    if j.state == "downloading":
        t = "%s of %s" % (xc.human(j.done), xc.human(j.total) if j.total else "?")
        if j.speed > 0:
            t += "  ·  %s/s" % xc.human(j.speed)
            if j.total:
                t += "  ·  %s left" % xc.human_time((j.total - j.done) / max(j.speed, 1))
        if j.error:
            t += "  ·  " + j.error
        return "Downloading %s  ·  %d%%  ·  %s" % (j.name, int(j.fraction * 100), t)
    if j.state == "paused":
        return "Paused at %d%% (%s of %s). Resumes from where it stopped, even after a restart." % (int(j.fraction * 100), xc.human(j.done), xc.human(j.total))
    if j.state == "queued":
        return "Queued: %s (%d%% already downloaded)" % (j.name, int(j.fraction * 100))
    if j.state == "verifying":
        return "Verifying SHA-256 of %s…" % j.name
    if j.state == "installing":
        return "Installing silently with EX CONNECT…  " + getattr(j, "verified", "")
    if j.state == "error":
        return "Error: " + j.error
    return j.state


# ---------------------------------------------------------------- hero carousel
class Hero(QWidget):
    open_app = Signal(str)

    def __init__(self, ui, ids):
        super().__init__()
        self.ui, self.ids, self.i, self.prev, self.t = ui, ids, 0, None, 1.0
        self.setFixedHeight(400); self.setCursor(Qt.PointingHandCursor)
        self.timer = QTimer(self, interval=6500, timeout=lambda: self.go(self.i + 1)); self.timer.start()
        self.anim = QTimer(self, interval=16, timeout=self._tick)
        self.btn = QPushButton("View in store", self); self.btn.setObjectName("primary"); self.btn.clicked.connect(lambda: self.open_app.emit(self.ids[self.i]))
        self.l = QPushButton("\u2039", self); self.r = QPushButton("\u203A", self)
        for b, d in ((self.l, -1), (self.r, 1)):
            b.setFixedSize(40, 64); b.setStyleSheet("QPushButton{background:rgba(0,0,0,0.35);border:none;font-size:30px;border-radius:6px} QPushButton:hover{background:rgba(92,184,255,0.45)}")
            b.clicked.connect(lambda _=False, d=d: self.go(self.i + d))
            b.setVisible(len(ids) > 1)
        if len(ids) <= 1:
            self.timer.stop()

    def go(self, n):
        if len(self.ids) <= 1:
            return
        self.prev = self.i; self.i = n % len(self.ids); self.t = 0.0; self.anim.start(); self.timer.start()

    def _tick(self):
        self.t = min(1.0, self.t + 0.06); self.update()
        if self.t >= 1:
            self.anim.stop()

    def resizeEvent(self, e):
        self.btn.move(56, 312); self.l.move(8, self.height() // 2 - 32); self.r.move(self.width() - 48, self.height() // 2 - 32)

    def mousePressEvent(self, e):
        w = self.width(); n = len(self.ids)
        x0 = w / 2 - n * 11
        if e.position().y() > self.height() - 30:
            k = int((e.position().x() - x0) // 22)
            if 0 <= k < n:
                return self.go(k)
        self.open_app.emit(self.ids[self.i])

    def paintEvent(self, e):
        qp = QPainter(self); qp.setRenderHint(QPainter.Antialiasing); qp.setRenderHint(QPainter.SmoothPixmapTransform)
        w, h = self.width(), self.height()
        path = QPainterPath(); path.addRoundedRect(QRectF(0, 0, w, h), 10, 10); qp.setClipPath(path)
        def draw(aid, op):
            qp.setOpacity(op); qp.drawPixmap(0, 0, cover_pix(pix(art(aid, "hero.jpg")), w, h))
        if self.prev is not None and self.t < 1:
            draw(self.ids[self.prev], 1.0)
        draw(self.ids[self.i], self.t if self.prev is not None else 1.0)
        qp.setOpacity(1)
        g = QLinearGradient(0, 0, w * 0.75, 0); g.setColorAt(0, QColor(8, 12, 18, 235)); g.setColorAt(0.55, QColor(8, 12, 18, 120)); g.setColorAt(1, QColor(8, 12, 18, 0))
        qp.fillRect(0, 0, w, h, g)
        g2 = QLinearGradient(0, h * 0.6, 0, h); g2.setColorAt(0, QColor(0, 0, 0, 0)); g2.setColorAt(1, QColor(0, 0, 0, 160)); qp.fillRect(0, 0, w, h, g2)
        a = self.ui.svc.catalog[self.ids[self.i]]
        qp.drawPixmap(56, 52, pix(art(a["id"], "icon.png")).scaled(72, 72, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        qp.setPen(QColor(ACCENT)); f = QFont("Segoe UI", 9); f.setBold(True); f.setLetterSpacing(QFont.AbsoluteSpacing, 2); qp.setFont(f)
        qp.drawText(56, 148, ("FEATURED  ·  " + a["category"]).upper())
        qp.setPen(QColor(FG)); f = QFont("Segoe UI", 30); f.setWeight(QFont.Black); qp.setFont(f)
        qp.drawText(54, 196, a["name"])
        f = QFont("Segoe UI", 12); qp.setFont(f); qp.setPen(QColor("#c9d6e3"))
        qp.drawText(QRectF(56, 212, min(560, w - 120), 70), Qt.TextWordWrap, a["tagline"])
        st = self.ui.svc.status(a["id"])
        qp.setPen(QColor("#9be57c" if st in ("play", "playing") else MUTED)); f = QFont("Segoe UI", 10); f.setBold(True); qp.setFont(f)
        qp.drawText(56, 292, {"play": "IN YOUR LIBRARY", "playing": "PLAYING NOW", "update": "UPDATE AVAILABLE"}.get(st, "FREE  ·  v" + self.ui.svc.latest_version(a["id"])))
        n = len(self.ids); x0 = w / 2 - n * 11
        for k in (range(n) if n > 1 else []):
            qp.setBrush(QColor(ACCENT) if k == self.i else QColor(255, 255, 255, 90)); qp.setPen(Qt.NoPen)
            qp.drawRoundedRect(QRectF(x0 + k * 22, h - 18, 16 if k == self.i else 10, 6), 3, 3)


class Banner(QWidget):
    """Featured & Recommended card 1: EX Inc.'s promo banner, shown whole (3:2, letterboxed, no overlays)."""
    clicked = Signal()

    def __init__(self):
        super().__init__()
        self.img = QPixmap(res("assets", "featured_banner_user.jpg")); self.bg = QPixmap(res("assets", "featured_banner_bg.jpg"))
        self.setCursor(Qt.PointingHandCursor); self.setToolTip("Browse games")
        self.setMinimumHeight(360); self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed); self.hover = False

    def resizeEvent(self, e):
        h = int(min(600, max(360, self.width() * 0.42)))
        if self.height() != h:
            self.setFixedHeight(h)

    def enterEvent(self, e):
        self.hover = True; self.update()

    def leaveEvent(self, e):
        self.hover = False; self.update()

    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            self.clicked.emit()

    def paintEvent(self, e):
        qp = QPainter(self); qp.setRenderHint(QPainter.Antialiasing); qp.setRenderHint(QPainter.SmoothPixmapTransform)
        w, h = self.width(), self.height()
        path = QPainterPath(); path.addRoundedRect(QRectF(0, 0, w, h), 10, 10); qp.setClipPath(path)
        qp.drawPixmap(0, 0, cover_pix(self.bg, w, h))
        ih = h; iw = int(ih * self.img.width() / max(1, self.img.height()))
        if iw > w:
            iw = w; ih = int(iw * self.img.height() / self.img.width())
        x, y = (w - iw) // 2, (h - ih) // 2
        qp.drawPixmap(QRectF(x, y, iw, ih), self.img, QRectF(self.img.rect()))
        qp.setClipping(False)
        qp.setPen(QPen(QColor(ACCENT if self.hover else LINE), 2)); qp.setBrush(Qt.NoBrush)
        qp.drawRoundedRect(QRectF(1, 1, w - 2, h - 2), 10, 10)


class DreamVineCard(QFrame):
    """Featured game card (DREAM VINE, PIKNOTT CELESTIKA): store art, name, tagline, latest version and Install/Play/Update."""
    clicked = Signal(str)

    def __init__(self, ui, aid="dream-vine"):
        super().__init__()
        self.ui, self.aid = ui, aid; a = ui.svc.catalog[aid]
        self.img = pix(art(aid, "hero.jpg"))
        self.setCursor(Qt.PointingHandCursor); self.setToolTip("Open %s in the store" % a["name"]); self.hover = False
        v = QVBoxLayout(self); v.setContentsMargins(56, 40, 56, 40); v.setSpacing(10); v.addStretch(1)
        k = lbl("FEATURED  \u00b7  " + a["category"].upper()); k.setStyleSheet("background:transparent;color:%s;font-weight:800;letter-spacing:2px;font-size:12px" % ACCENT); v.addWidget(k)
        t = lbl(a["name"]); t.setStyleSheet("background:transparent;font-size:40px;font-weight:900;color:%s" % FG); v.addWidget(t)
        d = lbl(a["tagline"], None, True); d.setMaximumWidth(620); d.setStyleSheet("background:transparent;color:#dbe6f0;font-size:15px"); v.addWidget(d)
        self.ver = lbl(""); self.ver.setStyleSheet("background:transparent;color:%s;font-weight:700;font-size:12px" % MUTED); v.addWidget(self.ver)
        self.bar = ActionBar(ui, aid, uninstall=False); self.bar.setMaximumWidth(620); self.bar.setStyleSheet("QLabel{background:transparent}")  # keep the app-wide #primary (Library) button style
        v.addWidget(self.bar)
        self.refresh()

    def refresh(self):
        self.ver.setText("LATEST VERSION  v%s  \u00b7  %s" % (self.ui.svc.latest_version(self.aid), self.ui.svc.catalog[self.aid]["genre"]))
        self.bar.refresh()

    def enterEvent(self, e):
        self.hover = True; self.update()

    def leaveEvent(self, e):
        self.hover = False; self.update()

    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            self.clicked.emit(self.aid)

    def paintEvent(self, e):
        qp = QPainter(self); qp.setRenderHint(QPainter.Antialiasing); qp.setRenderHint(QPainter.SmoothPixmapTransform)
        w, h = self.width(), self.height()
        path = QPainterPath(); path.addRoundedRect(QRectF(0, 0, w, h), 10, 10); qp.setClipPath(path)
        qp.drawPixmap(0, 0, cover_pix(self.img, w, h))
        g = QLinearGradient(0, 0, w * 0.8, 0); g.setColorAt(0, QColor(8, 12, 18, 235)); g.setColorAt(0.6, QColor(8, 12, 18, 140)); g.setColorAt(1, QColor(8, 12, 18, 0))
        qp.fillRect(0, 0, w, h, g)
        qp.setClipping(False)
        qp.setPen(QPen(QColor(ACCENT if self.hover else LINE), 2)); qp.setBrush(Qt.NoBrush)
        qp.drawRoundedRect(QRectF(1, 1, w - 2, h - 2), 10, 10)


class FeaturedCarousel(QWidget):
    """Featured & Recommended: card 1 = promo banner (whole, uncropped), cards 2-3 = DREAM VINE, PIKNOTT CELESTIKA. Arrows + dots, 8 s auto-rotate (no hover pause); only the pause/play toggle stops it."""

    def __init__(self, ui, banner):
        super().__init__()
        self.banner = banner; self.games = [DreamVineCard(ui, aid) for aid in ("dream-vine", "piknott-celestika")]
        self.dv = self.games[0]
        for g in self.games:
            g.clicked.connect(ui.open_product)
        self.stack = QStackedWidget(); self.stack.addWidget(banner)
        for g in self.games:
            self.stack.addWidget(g)
        self.stack.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        v = QVBoxLayout(self); v.setContentsMargins(0, 0, 0, 0); v.setSpacing(8); v.addWidget(self.stack)
        row = QHBoxLayout(); row.setSpacing(8); row.addStretch(1)
        self.l = QPushButton("\u2039"); self.r = QPushButton("\u203A"); self.dots = []
        for b, d in ((self.l, -1), (self.r, 1)):
            b.setFixedSize(36, 28); b.setCursor(Qt.PointingHandCursor)
            b.setStyleSheet("QPushButton{background:rgba(255,255,255,0.08);border:none;font-size:20px;border-radius:5px;padding:0} QPushButton:hover{background:rgba(92,184,255,0.45)}")
            b.clicked.connect(lambda _=False, d=d: self.go(self.stack.currentIndex() + d))
        row.addWidget(self.l)
        for k in range(self.stack.count()):
            dt = QPushButton(); dt.setCursor(Qt.PointingHandCursor); dt.clicked.connect(lambda _=False, k=k: self.go(k)); self.dots.append(dt); row.addWidget(dt)
        row.addWidget(self.r)
        self.paused = False; self.pp = QPushButton("\u23F8"); self.pp.setToolTip("Pause rotation"); self.pp.setFixedSize(28, 28); self.pp.setCursor(Qt.PointingHandCursor)
        self.pp.setStyleSheet("QPushButton{background:rgba(255,255,255,0.08);border:none;font-size:13px;border-radius:5px;padding:0} QPushButton:hover{background:rgba(92,184,255,0.45)}")
        self.pp.clicked.connect(self.toggle); row.addWidget(self.pp); row.addStretch(1); v.addLayout(row)
        self.timer = QTimer(self, interval=8000, timeout=lambda: self.go(self.stack.currentIndex() + 1)); self.timer.start()
        self.go(0)

    def resizeEvent(self, e):
        h = int(min(600, max(360, self.width() * 0.42)))
        self.stack.setFixedHeight(h); self.banner.setFixedHeight(h)
        for g in self.games:
            g.setFixedHeight(h)

    def go(self, n):
        n %= self.stack.count(); self.stack.setCurrentIndex(n)
        if not getattr(self, "paused", False):
            self.timer.start()
        for k, dt in enumerate(self.dots):
            dt.setFixedSize(22 if k == n else 10, 8)
            dt.setStyleSheet("QPushButton{background:%s;border:none;border-radius:4px;padding:0}" % (ACCENT if k == n else "rgba(255,255,255,0.35)"))

    def toggle(self):
        self.paused = not self.paused
        if self.paused:
            self.timer.stop()
        else:
            self.timer.start()
        self.pp.setText("\u25B6" if self.paused else "\u23F8"); self.pp.setToolTip("Resume rotation" if self.paused else "Pause rotation")

    def refresh(self):
        for g in self.games:
            g.refresh()


# ---------------------------------------------------------------- upcoming games + wishlist
def fit_pix(p, w, h, radius=0, bg=None):
    """scale pixmap to fit inside w x h (letterboxed, nothing cropped)"""
    out = QPixmap(w, h); out.fill(Qt.transparent)
    qp = QPainter(out); qp.setRenderHint(QPainter.Antialiasing); qp.setRenderHint(QPainter.SmoothPixmapTransform)
    path = QPainterPath(); path.addRoundedRect(QRectF(0, 0, w, h), radius, radius); qp.setClipPath(path)
    qp.fillRect(0, 0, w, h, QColor(bg or "#06080c"))
    if not p.isNull():
        s = p.scaled(w, h, Qt.KeepAspectRatio, Qt.SmoothTransformation); qp.drawPixmap((w - s.width()) // 2, (h - s.height()) // 2, s)
    qp.end()
    return out


def soon_cover(aid):
    return pix(res("assets", SOON[aid]["cover"]))


def soon_tag(aid):
    t = lbl(SOON[aid].get("status", "COMING SOON")); t.setStyleSheet("background:%s;color:#0e1319;font-weight:900;font-size:11px;border-radius:4px;padding:3px 10px" % ORANGE)
    t.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed); t.ensurePolished(); t.setMinimumWidth(t.sizeHint().width() + 4)
    return t


class WishButton(QPushButton):
    def __init__(self, ui, aid):
        super().__init__()
        self.ui, self.aid = ui, aid; self.setObjectName("ghost"); self.setCursor(Qt.PointingHandCursor)
        self.clicked.connect(self.toggle); self.refresh()

    def toggle(self):
        self.ui.svc.toggle_wishlist(self.aid); self.ui.refresh_all()

    def refresh(self):
        on = self.ui.svc.on_wishlist(self.aid)
        self.setText("On Wishlist \u2713" if on else "\u2661  Add to Wishlist")
        self.setStyleSheet("QPushButton{color:%s;font-weight:700}" % ("#9be57c" if on else FG))


class SoonCard(QFrame):
    """Store card for an upcoming (not installable) game."""
    clicked = Signal(str)

    def __init__(self, ui, aid, w=300):
        super().__init__()
        self.ui, self.aid = ui, aid; a = SOON[aid]
        self.setObjectName("card"); self.setCursor(Qt.PointingHandCursor); self.setFixedWidth(w)
        v = QVBoxLayout(self); v.setContentsMargins(0, 0, 0, 10); v.setSpacing(6)
        img = QLabel(); img.setPixmap(fit_pix(soon_cover(aid), w - 2, int((w - 2) * 0.5625), 7)); v.addWidget(img)
        col = QVBoxLayout(); col.setContentsMargins(12, 2, 12, 0); col.setSpacing(2)
        t = lbl(a["name"]); t.setStyleSheet("font-weight:800;font-size:14px;background:transparent"); col.addWidget(t)
        g = lbl(a["genre"], "small"); g.setStyleSheet("background:transparent"); col.addWidget(g)
        v.addLayout(col)
        row = QHBoxLayout(); row.setContentsMargins(12, 0, 12, 0); row.addWidget(soon_tag(aid)); row.addStretch(1)
        self.wish = WishButton(ui, aid); row.addWidget(self.wish); v.addLayout(row)

    def refresh(self):
        self.wish.refresh()

    def mousePressEvent(self, e):
        self.clicked.emit(self.aid)


class SoonPage(QWidget):
    """Store page for an upcoming game: cover (uncropped), name, status tag, publisher, description, wishlist toggle."""
    def __init__(self, ui):
        super().__init__()
        self.ui = ui; self.aid = None; self.wish = None
        self.inner = QWidget(); self.v = QVBoxLayout(self.inner); self.v.setContentsMargins(36, 20, 36, 30); self.v.setSpacing(14)
        lay = QVBoxLayout(self); lay.setContentsMargins(0, 0, 0, 0); lay.addWidget(scroll(self.inner))

    def show_app(self, aid):
        self.aid = aid; clear_layout(self.v)
        back = QPushButton("\u2039  Store"); back.setObjectName("ghost"); back.setFixedWidth(110); back.clicked.connect(lambda: self.ui.go("store")); self.v.addWidget(back)
        self.wish = soon_panel(self.ui, aid, self.v); self.v.addStretch(1)

    def refresh(self):
        if self.wish:
            try:
                self.wish.refresh()
            except RuntimeError:
                pass


def soon_panel(ui, aid, v):
        """Store-page layout for an upcoming game (full uncropped cover + details + wishlist toggle); returns the WishButton."""
        a = SOON[aid]
        row = QHBoxLayout(); row.setSpacing(28)
        cov = QLabel(); cov.setPixmap(fit_pix(soon_cover(aid), 460, 460, 10)); row.addWidget(cov, 0, Qt.AlignTop)
        col = QVBoxLayout(); col.setSpacing(10)
        col.addWidget(soon_tag(aid))
        t = lbl(a["name"], None, True); t.setStyleSheet("font-size:34px;font-weight:900"); col.addWidget(t)
        g = lbl(a["category"] + "  \u00b7  " + a["genre"], "small"); g.setStyleSheet("color:%s" % ACCENT); col.addWidget(g)
        col.addWidget(lbl("Publisher: %s\nDeveloper: %s\nRelease date: %s" % (a["publisher"], a["developer"], a.get("release", "To be announced")), "muted"))
        d = lbl(a["tagline"], None, True); d.setStyleSheet("font-size:15px;color:#dbe6f0"); col.addWidget(d)
        ab = lbl(a["about"], "muted", True); ab.setMaximumWidth(640); col.addWidget(ab)
        br = QHBoxLayout(); wish = WishButton(ui, aid); wish.setMinimumWidth(200); br.addWidget(wish)
        br.addWidget(lbl("Not available to download yet.", "small")); br.addStretch(1); col.addLayout(br)
        col.addStretch(1); row.addLayout(col, 1); v.addLayout(row)
        return wish


class WishlistPage(QWidget):
    def __init__(self, ui):
        super().__init__()
        self.ui = ui
        self.inner = QWidget(); outer = QVBoxLayout(self.inner); outer.setContentsMargins(36, 24, 36, 30); outer.setSpacing(14)
        lay = QVBoxLayout(self); lay.setContentsMargins(0, 0, 0, 0); lay.addWidget(scroll(self.inner))
        # featured upcoming game, always shown in its store-page layout (wishlisted or not)
        outer.addWidget(lbl("WISHLIST", "h2"))
        self.top = []
        for a in UPCOMING:
            self.top.append(soon_panel(ui, a["id"], outer)); outer.addSpacing(10)
        self.v = QVBoxLayout(); self.v.setSpacing(12); outer.addLayout(self.v); outer.addStretch(1)
        self._shown = None

    def refresh(self):
        for w in self.top:
            w.refresh()
        wl = [x for x in self.ui.svc.wishlist() if (x in SOON or x in self.ui.svc.catalog) and x not in [a["id"] for a in UPCOMING]]
        if wl == self._shown:
            return
        self._shown = wl; clear_layout(self.v)
        if wl:
            self.v.addWidget(lbl("ALSO ON YOUR WISHLIST  \u00b7  %d" % len(wl), "h2"))
        for aid in wl:
            soon = aid in SOON; a = SOON[aid] if soon else self.ui.svc.catalog[aid]
            row = QFrame(); row.setObjectName("card"); row.setCursor(Qt.PointingHandCursor)
            h = QHBoxLayout(row); h.setContentsMargins(0, 0, 14, 0); h.setSpacing(14)
            im = QLabel(); im.setPixmap(fit_pix(soon_cover(aid), 232, 131, 7) if soon else cover_pix(pix(art(aid, "capsule.jpg")), 232, 131, 7)); h.addWidget(im)
            col = QVBoxLayout(); col.setSpacing(4)
            t = lbl(a["name"]); t.setStyleSheet("font-weight:800;font-size:16px;background:transparent"); col.addWidget(t)
            g = lbl(a["category"] + "  \u00b7  " + a["genre"], "small"); g.setStyleSheet("background:transparent"); col.addWidget(g)
            if soon:
                tr = QHBoxLayout(); tr.addWidget(soon_tag(aid)); tr.addStretch(1); col.addLayout(tr)
            h.addLayout(col, 1)
            rm = QPushButton("Remove"); rm.setObjectName("ghost"); rm.setCursor(Qt.PointingHandCursor)
            rm.clicked.connect(lambda _=False, aid=aid: (self.ui.svc.toggle_wishlist(aid, False), self.ui.refresh_all())); h.addWidget(rm)
            row.mousePressEvent = lambda e, aid=aid: self.ui.open_product(aid)
            self.v.addWidget(row)


# ---------------------------------------------------------------- store card
class Card(QFrame):
    clicked = Signal(str)

    def __init__(self, ui, aid, w=300):
        super().__init__()
        self.ui, self.aid = ui, aid; a = ui.svc.catalog[aid]
        self.setObjectName("card"); self.setCursor(Qt.PointingHandCursor); self.setFixedWidth(w)
        v = QVBoxLayout(self); v.setContentsMargins(0, 0, 0, 10); v.setSpacing(6)
        img = QLabel(); img.setPixmap(cover_pix(pix(art(aid, "capsule.jpg")), w - 2, int((w - 2) * 0.5625), 7)); v.addWidget(img)
        row = QHBoxLayout(); row.setContentsMargins(12, 2, 12, 0)
        ic = QLabel(); ic.setPixmap(pix(art(aid, "icon.png")).scaled(34, 34, Qt.KeepAspectRatio, Qt.SmoothTransformation)); row.addWidget(ic)
        col = QVBoxLayout(); col.setSpacing(0)
        t = lbl(a["name"]); t.setStyleSheet("font-weight:800;font-size:14px;background:transparent"); col.addWidget(t)
        g = lbl(a["genre"], "small"); g.setStyleSheet("background:transparent"); col.addWidget(g)
        row.addLayout(col, 1); v.addLayout(row)
        self.status = lbl("", "small"); self.status.setContentsMargins(12, 0, 12, 0); v.addWidget(self.status)
        self.refresh()

    def refresh(self):
        s = self.ui.svc.status(self.aid)
        txt = {"install": "Free  ·  %s" % self.ui.svc.size_text(self.aid), "play": "\u2714 In library  ·  v%s" % (self.ui.svc.installed.get(self.aid) or {}).get("version", ""),
               "update": "\u2B06 Update to v%s" % self.ui.svc.latest_version(self.aid), "playing": "\u25B6 Playing now"}.get(s)
        if not txt:
            j = self.ui.svc.job_for(self.aid); txt = "%s %d%%" % (s.capitalize(), int(j.fraction * 100)) if j else s
        col = {"play": "#9be57c", "playing": "#9be57c", "update": ACCENT}.get(s, MUTED if s == "install" else ORANGE)
        self.status.setText(txt); self.status.setStyleSheet("background:transparent;color:%s;font-weight:600" % col)

    def mousePressEvent(self, e):
        self.clicked.emit(self.aid)


class RecCard(QFrame):
    """Wide recommended card: cover art, screenshots, tagline and status."""
    clicked = Signal(str)

    def __init__(self, ui, aid):
        super().__init__()
        self.ui, self.aid = ui, aid; a = ui.svc.catalog[aid]
        self.setObjectName("card"); self.setCursor(Qt.PointingHandCursor); self.setMaximumWidth(1260)
        h = QHBoxLayout(self); h.setContentsMargins(0, 0, 16, 0); h.setSpacing(18)
        img = QLabel(); img.setPixmap(cover_pix(pix(shots(aid)[0]), 300, 300, 7)); h.addWidget(img)
        col = QVBoxLayout(); col.setContentsMargins(0, 16, 0, 16); col.setSpacing(8)
        t = lbl(a["name"]); t.setStyleSheet("font-weight:900;font-size:22px;background:transparent"); col.addWidget(t)
        g = lbl(a["category"] + "  \u00b7  " + a["genre"], "small"); g.setStyleSheet("background:transparent;color:%s" % ACCENT); col.addWidget(g)
        d = lbl(a["tagline"], None, True); d.setStyleSheet("background:transparent;color:#c9d6e3;font-size:13px"); col.addWidget(d)
        strip = QHBoxLayout(); strip.setSpacing(8)
        for p in shots(aid)[1:5]:
            s = QLabel(); s.setPixmap(cover_pix(pix(p), 200, 113, 5)); s.setStyleSheet("background:transparent"); strip.addWidget(s)
        strip.addStretch(1); col.addLayout(strip)
        self.status = lbl("", "small"); col.addWidget(self.status); col.addStretch(1)
        h.addLayout(col, 1)
        self.refresh()

    def refresh(self):
        Card.refresh(self)

    def mousePressEvent(self, e):
        self.clicked.emit(self.aid)


# ---------------------------------------------------------------- pages
def scroll(widget):
    s = QScrollArea(); s.setWidgetResizable(True); s.setWidget(widget); s.setFrameShape(QFrame.NoFrame)
    s.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
    return s


class StorePage(QWidget):
    def __init__(self, ui):
        super().__init__()
        self.ui = ui
        inner = QWidget(); v = QVBoxLayout(inner); v.setContentsMargins(36, 24, 36, 30); v.setSpacing(16)
        v.addWidget(lbl("FEATURED & RECOMMENDED", "h2"))
        self.banner = Banner(); self.banner.clicked.connect(self.scroll_to_games)
        self.featured = FeaturedCarousel(ui, self.banner); v.addWidget(self.featured)
        self.cards = []
        self.sections = {}
        for cat, title in ((GAMES, "GAMES"), (APPS, "APPS & TOOLS")):
            ids = [a["id"] for a in ui.svc.catalog.values() if a["category"] == cat] + [a["id"] for a in UPCOMING if a["category"] == cat]
            hl = lbl("%s  ·  %d" % (title, len(ids)), "h2"); self.sections[cat] = hl
            hdr = QHBoxLayout(); hdr.addWidget(hl); hdr.addStretch(1)
            v.addSpacing(10); v.addLayout(hdr)
            grid = QGridLayout(); grid.setHorizontalSpacing(16); grid.setVerticalSpacing(16)
            for k, aid in enumerate(ids):
                c = (SoonCard if aid in SOON else Card)(ui, aid); c.clicked.connect(ui.open_product); grid.addWidget(c, k // 4, k % 4, Qt.AlignLeft); self.cards.append(c)
            grid.setColumnStretch(4, 1)
            v.addLayout(grid)
        v.addStretch(1)
        self.sc = scroll(inner)
        lay = QVBoxLayout(self); lay.setContentsMargins(0, 0, 0, 0); lay.addWidget(self.sc)

    def scroll_to_games(self):
        self.ui.go("store")
        hl = self.sections[GAMES]
        y = hl.mapTo(self.sc.widget(), QPointF(0, 0).toPoint()).y()
        self.sc.verticalScrollBar().setValue(max(0, y - 12))

    def refresh(self):
        self.featured.refresh()
        for c in self.cards:
            c.refresh()


class SearchPage(QWidget):
    def __init__(self, ui):
        super().__init__()
        self.ui = ui
        inner = QWidget(); self.v = QVBoxLayout(inner); self.v.setContentsMargins(36, 24, 36, 30); self.v.setSpacing(10)
        lay = QVBoxLayout(self); lay.setContentsMargins(0, 0, 0, 0); lay.addWidget(scroll(inner))

    def set_query(self, q):
        while self.v.count():
            it = self.v.takeAt(0)
            if it.widget():
                it.widget().deleteLater()
        ql = q.lower().strip()
        hits = [a for a in self.ui.svc.catalog.values() if ql in (a["name"] + " " + a["genre"] + " " + a["tagline"] + " " + a["category"]).lower()]
        self.v.addWidget(lbl('SEARCH RESULTS FOR "%s"  ·  %d' % (q, len(hits)), "h2"))
        for a in hits:
            row = QFrame(); row.setObjectName("card"); row.setCursor(Qt.PointingHandCursor)
            h = QHBoxLayout(row); h.setContentsMargins(0, 0, 14, 0)
            im = QLabel(); im.setPixmap(cover_pix(pix(art(a["id"], "capsule.jpg")), 232, 108, 7)); h.addWidget(im)
            col = QVBoxLayout(); t = lbl(a["name"]); t.setStyleSheet("font-weight:800;font-size:16px;background:transparent"); col.addWidget(t)
            d = lbl(a["tagline"], "muted", True); d.setStyleSheet("background:transparent"); col.addWidget(d)
            g = lbl(a["category"] + "  ·  " + a["genre"], "small"); g.setStyleSheet("background:transparent"); col.addWidget(g)
            h.addLayout(col, 1)
            row.mousePressEvent = lambda e, aid=a["id"]: self.ui.open_product(aid)
            self.v.addWidget(row)
        if not hits:
            self.v.addWidget(lbl("Nothing found. Try another name.", "muted"))
        self.v.addStretch(1)


class ProductPage(QWidget):
    def __init__(self, ui):
        super().__init__()
        self.ui = ui; self.aid = None; self.bar = None
        self.inner = QWidget(); self.v = QVBoxLayout(self.inner); self.v.setContentsMargins(36, 20, 36, 30); self.v.setSpacing(14)
        lay = QVBoxLayout(self); lay.setContentsMargins(0, 0, 0, 0); self.sc = scroll(self.inner); lay.addWidget(self.sc)

    def show_app(self, aid):
        self.aid = aid; svc = self.ui.svc; a = svc.catalog[aid]
        while self.v.count():
            it = self.v.takeAt(0)
            w = it.widget()
            if w:
                w.deleteLater()
            elif it.layout():
                clear_layout(it.layout())
        crumbs = QHBoxLayout()
        back = QPushButton("\u2190  Store"); back.setObjectName("link"); back.clicked.connect(lambda: self.ui.go("store")); crumbs.addWidget(back)
        crumbs.addWidget(lbl("  /  %s  /  %s" % ("All " + a["category"], a["name"]), "small")); crumbs.addStretch(1)
        self.v.addLayout(crumbs)
        self.v.addWidget(lbl(a["name"], "h1"))
        body = QHBoxLayout(); body.setSpacing(20)
        # gallery
        gal = QVBoxLayout(); gal.setSpacing(8)
        self.shots = shots(aid); self.si = 0
        self.big = ClickLabel(); self.big.setFixedSize(800, 450); self.big.setStyleSheet("background:#000;border-radius:6px"); gal.addWidget(self.big)
        thumbs = QHBoxLayout(); thumbs.setSpacing(6); self.thumbs = []
        for k, p in enumerate(self.shots):
            t = ClickLabel(); t.setPixmap(cover_pix(pix(p), 122, 69, 4)); t.setFixedSize(126, 73); t.setCursor(Qt.PointingHandCursor)
            t.clicked.connect(lambda k=k: self.pick(k)); thumbs.addWidget(t); self.thumbs.append(t)
        thumbs.addStretch(1); gal.addLayout(thumbs)
        self.big.clicked.connect(lambda: self.pick(self.si + 1))
        body.addLayout(gal)
        # side
        side = QVBoxLayout(); side.setSpacing(10)
        cap = QLabel(); cap.setPixmap(cover_pix(pix(art(aid, "capsule.jpg")), 340, 191, 6)); side.addWidget(cap)
        tl = lbl(a["tagline"], None, True); tl.setStyleSheet("font-size:13px;color:#c9d6e3"); tl.setFixedWidth(340); side.addWidget(tl)
        info = QFrame(); info.setObjectName("infobox"); g = QGridLayout(info); g.setContentsMargins(12, 10, 12, 10); g.setVerticalSpacing(5)
        rows = [("CATEGORY", a["category"]), ("GENRE", a["genre"]), ("VERSION", svc.latest_version(aid)), ("DOWNLOAD SIZE", svc.size_text(aid)),
                ("DEVELOPER", "EX Inc."), ("PUBLISHER", PUBLISHER), ("PLATFORM", "Windows 10/11 x64"), ("SOURCE", "github.com/Teobokki/" + a["repo"])]
        for r, (k, val) in enumerate(rows):
            g.addWidget(lbl(k, "small"), r, 0); vv = lbl(val); vv.setStyleSheet("color:%s;font-size:12px" % ACCENT if k == "SOURCE" else "font-size:12px"); g.addWidget(vv, r, 1)
        info.setFixedWidth(340); side.addWidget(info); side.addStretch(1)
        body.addLayout(side); body.addStretch(1)
        self.v.addLayout(body)
        # buy box
        box = QFrame(); box.setObjectName("panel"); bl = QVBoxLayout(box); bl.setContentsMargins(20, 16, 20, 16)
        verb = "Play" if a["category"] == GAMES else "Get"
        bl.addWidget(lbl("%s %s" % (verb, a["name"]), None)); box.findChildren(QLabel)[0].setStyleSheet("font-size:18px;font-weight:800")
        self.bar = ActionBar(self.ui, aid); bl.addWidget(self.bar); box.setMaximumWidth(1160)
        self.v.addWidget(box)
        # about
        about = QFrame(); about.setObjectName("panel"); al = QVBoxLayout(about); al.setContentsMargins(20, 16, 20, 16); al.setSpacing(8)
        al.addWidget(lbl("ABOUT THIS " + ("GAME" if a["category"] == GAMES else "APP"), "h2"))
        d = lbl(a["about"], None, True); d.setStyleSheet("font-size:13px;color:#c9d6e3;line-height:140%"); al.addWidget(d)
        al.addSpacing(6); al.addWidget(lbl("FEATURES", "h2"))
        for f in a["features"]:
            fl = lbl("\u2022  " + f, None, True); fl.setStyleSheet("font-size:13px;color:#c9d6e3"); al.addWidget(fl)
        n = svc.notes(aid)
        if n:
            al.addSpacing(6); al.addWidget(lbl("WHAT'S NEW IN %s" % svc.latest_version(aid), "h2")); nl = lbl(n, "muted", True); al.addWidget(nl)
        about.setMaximumWidth(1160); self.v.addWidget(about)
        self.v.addStretch(1)
        self.pick(0); self.sc.verticalScrollBar().setValue(0)

    def pick(self, k):
        if not self.shots:
            return
        self.si = k % len(self.shots)
        p = pix(self.shots[self.si]).scaled(800, 450, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.big.setAlignment(Qt.AlignCenter); self.big.setPixmap(p)
        for i, t in enumerate(self.thumbs):
            t.setStyleSheet("border:2px solid %s;border-radius:5px" % (ACCENT if i == self.si else "transparent"))

    def refresh(self):
        if self.bar:
            self.bar.refresh()


def clear_layout(l):
    while l.count():
        it = l.takeAt(0)
        if it.widget():
            it.widget().deleteLater()
        elif it.layout():
            clear_layout(it.layout())


class LibraryPage(QWidget):
    def __init__(self, ui):
        super().__init__()
        self.ui = ui; self.aid = None; self.bar = None
        h = QHBoxLayout(self); h.setContentsMargins(0, 0, 0, 0); h.setSpacing(0)
        side = QWidget(); side.setObjectName("libside"); side.setFixedWidth(270); side.setStyleSheet("#libside{background:%s}" % BG2); sv = QVBoxLayout(side); sv.setContentsMargins(10, 12, 10, 10)
        self.filter = QLineEdit(); self.filter.setPlaceholderText("Search your library"); self.filter.textChanged.connect(self.fill); sv.addWidget(self.filter)
        self.list = QListWidget(); self.list.setIconSize(QSize(24, 24)); self.list.currentItemChanged.connect(self.on_pick); sv.addWidget(self.list, 1)
        h.addWidget(side)
        self.detail = QWidget(); self.dv = QVBoxLayout(self.detail); self.dv.setContentsMargins(0, 0, 0, 0); self.dv.setSpacing(0)
        h.addWidget(self.detail, 1)
        self.fill()

    def fill(self):
        q = self.filter.text().lower(); cur = self.aid
        self.list.blockSignals(True); self.list.clear()
        for cat, title in ((GAMES, "GAMES"), (APPS, "APPS & TOOLS")):
            ids = [a["id"] for a in self.ui.svc.catalog.values() if a["category"] == cat and q in a["name"].lower()]
            hdr = QListWidgetItem("%s  (%d)" % (title, len(ids))); hdr.setFlags(Qt.NoItemFlags); f = hdr.font(); f.setBold(True); f.setPointSize(8); hdr.setFont(f)
            hdr.setForeground(QColor("#6f8396")); self.list.addItem(hdr)
            for aid in ids:
                a = self.ui.svc.catalog[aid]; st = self.ui.svc.status(aid)
                suffix = {"playing": "  \u2013 Playing", "update": "  \u2013 Update", "downloading": "  \u2013 Downloading", "paused": "  \u2013 Paused", "installing": "  \u2013 Installing", "queued": "  \u2013 Queued"}.get(st, "")
                it = QListWidgetItem(QIcon(art(aid, "icon.png")), a["name"] + suffix); it.setData(Qt.UserRole, aid)
                if st in ("play", "playing", "update"):
                    it.setForeground(QColor(FG if st != "playing" else "#9be57c"))
                else:
                    it.setForeground(QColor("#6f8396"))
                self.list.addItem(it)
                if aid == cur:
                    self.list.setCurrentItem(it)
        self.list.blockSignals(False)

    def on_pick(self, it, _prev=None):
        if it and it.data(Qt.UserRole):
            self.show_app(it.data(Qt.UserRole))

    def select(self, aid):
        for i in range(self.list.count()):
            if self.list.item(i).data(Qt.UserRole) == aid:
                self.list.setCurrentRow(i); return
        self.show_app(aid)

    def show_app(self, aid):
        self.aid = aid; svc = self.ui.svc; a = svc.catalog[aid]
        clear_layout(self.dv)
        head = QLabel(); head.setFixedHeight(300); head.setScaledContents(False)
        self._head = head; head.resizeEvent = lambda e: self._paint_head()
        self.dv.addWidget(head)
        bar = QFrame(); bar.setObjectName("libbar"); bar.setStyleSheet("#libbar{background:%s;border-bottom:1px solid %s}" % (PANEL, LINE)); bl = QHBoxLayout(bar); bl.setContentsMargins(28, 14, 28, 14)
        self.bar = ActionBar(self.ui, aid); bl.addWidget(self.bar, 1)
        self.dv.addWidget(bar)
        stats = QHBoxLayout(); stats.setContentsMargins(28, 16, 28, 0); stats.setSpacing(36)
        self.stat_labels = {}
        for k in ("PLAY TIME", "LAST PLAYED", "INSTALLED", "LATEST", "LOCATION"):
            col = QVBoxLayout(); col.setSpacing(2); col.addWidget(lbl(k, "small")); vv = lbl(""); vv.setStyleSheet("font-weight:700"); col.addWidget(vv); self.stat_labels[k] = vv; stats.addLayout(col)
        stats.addStretch(1); self.dv.addLayout(stats)
        links = QHBoxLayout(); links.setContentsMargins(24, 10, 28, 0)
        sp = QPushButton("Store page"); sp.setObjectName("link"); sp.clicked.connect(lambda: self.ui.open_product(aid)); links.addWidget(sp)
        of = QPushButton("Open install folder"); of.setObjectName("link"); of.clicked.connect(self.open_folder); links.addWidget(of); links.addStretch(1)
        self.dv.addLayout(links)
        strip = QHBoxLayout(); strip.setContentsMargins(28, 14, 28, 0); strip.setSpacing(10)
        for p in shots(aid)[:5]:
            t = QLabel(); t.setPixmap(cover_pix(pix(p), 200, 113, 5)); strip.addWidget(t)
        strip.addStretch(1); self.dv.addLayout(strip)
        self.dv.addStretch(1)
        self.refresh_stats()
        QTimer.singleShot(0, self._paint_head)

    def _paint_head(self):
        if not self.aid:
            return
        head = self._head; w, h = max(head.width(), 400), head.height(); a = self.ui.svc.catalog[self.aid]
        out = cover_pix(pix(art(self.aid, "hero.jpg")), w, h)
        qp = QPainter(out); qp.setRenderHint(QPainter.Antialiasing)
        g = QLinearGradient(0, h * 0.35, 0, h); g.setColorAt(0, QColor(0, 0, 0, 0)); g.setColorAt(1, QColor(10, 14, 20, 235)); qp.fillRect(0, 0, w, h, g)
        qp.drawPixmap(28, h - 108, pix(art(self.aid, "icon.png")).scaled(80, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        f = QFont("Segoe UI", 28); f.setWeight(QFont.Black); qp.setFont(f); qp.setPen(QColor(FG)); qp.drawText(124, h - 52, a["name"])
        f = QFont("Segoe UI", 11); qp.setFont(f); qp.setPen(QColor("#c9d6e3")); qp.drawText(126, h - 26, a["genre"])
        qp.end(); head.setPixmap(out)

    def refresh_stats(self):
        if not self.aid or not hasattr(self, "stat_labels"):
            return
        svc = self.ui.svc; inf = svc.installed.get(self.aid) or {}
        lp = svc.state["last_played"].get(self.aid)
        try:
            self.stat_labels["PLAY TIME"].setText(xc.human_time(svc.playtime(self.aid)) if svc.playtime(self.aid) else "—")
            self.stat_labels["LAST PLAYED"].setText(time.strftime("%d %b %Y %H:%M", time.localtime(lp)) if lp else "Never")
            self.stat_labels["INSTALLED"].setText(inf.get("version", "Not installed") if inf else "Not installed")
            self.stat_labels["LATEST"].setText(svc.latest_version(self.aid))
            self.stat_labels["LOCATION"].setText(inf.get("source", "—") if inf else "—")
        except RuntimeError:
            pass

    def open_folder(self):
        inf = self.ui.svc.installed.get(self.aid)
        if inf:
            QDesktopServices.openUrl(QUrl.fromLocalFile(os.path.dirname(inf["exe"])))

    def refresh(self):
        self.fill()
        if self.bar:
            try:
                self.bar.refresh()
            except RuntimeError:
                pass
        self.refresh_stats()


class DownloadsPage(QWidget):
    def __init__(self, ui):
        super().__init__()
        self.ui = ui
        inner = QWidget(); self.v = QVBoxLayout(inner); self.v.setContentsMargins(36, 24, 36, 30); self.v.setSpacing(12)
        lay = QVBoxLayout(self); lay.setContentsMargins(0, 0, 0, 0); lay.addWidget(scroll(inner))
        self.rows = {}; self.sig = None

    def refresh(self):
        svc = self.ui.svc
        jobs = [j for j in svc.jobs if j.state != "cancelled"]
        sig = tuple((j.app_id, j.state) for j in jobs)
        if sig != self.sig:
            self.sig = sig; clear_layout(self.v); self.rows = {}
            self.v.addWidget(lbl("DOWNLOADS  ·  EX CONNECT", "h2"))
            note = lbl("Downloads resume from where they stopped (HTTP Range), even after closing HYPERION DIGITAL EX or losing your connection. Every file is checked with SHA-256 before it is installed.", "muted", True)
            self.v.addWidget(note)
            active = [j for j in jobs if j.state != "done"]; done = [j for j in jobs if j.state == "done"]
            if not active:
                self.v.addWidget(lbl("No downloads in progress.", "muted"))
            for j in active + done:
                a = svc.catalog[j.app_id]
                row = QFrame(); row.setObjectName("panel"); h = QHBoxLayout(row); h.setContentsMargins(14, 12, 14, 12); h.setSpacing(14)
                im = QLabel(); im.setPixmap(cover_pix(pix(art(j.app_id, "capsule.jpg")), 178, 100, 5)); h.addWidget(im)
                col = QVBoxLayout(); t = lbl(a["name"]); t.setStyleSheet("font-weight:800;font-size:15px"); col.addWidget(t)
                bar = QProgressBar(); bar.setRange(0, 1000); bar.setTextVisible(False); bar.setFixedHeight(10); col.addWidget(bar)
                info = lbl("", "small", True); col.addWidget(info); h.addLayout(col, 1)
                if j.state != "done":
                    ab = ActionBar(self.ui, j.app_id, big=False); ab.bar.hide(); ab.info.hide(); ab.setFixedWidth(330); h.addWidget(ab)
                else:
                    ab = None; pb = QPushButton("\u25B6  PLAY"); pb.setObjectName("primary"); pb.clicked.connect(lambda _=False, aid=j.app_id: (svc.play(aid), self.ui.refresh_all())); h.addWidget(pb)
                self.rows[id(j)] = (j, bar, info, ab)
                self.v.addWidget(row)
            self.v.addStretch(1)
        for j, bar, info, ab in self.rows.values():
            bar.setValue(int(j.fraction * 1000) if j.state != "done" else 1000)
            info.setText(job_text(j) if j.state != "done" else "Installed v%s  ·  %s" % (j.version, getattr(j, "verified", "verified")))
            if ab:
                ab.refresh(); ab.bar.hide(); ab.info.hide(); ab.uninst.hide()


class ConnectPage(QWidget):
    def __init__(self, ui):
        super().__init__()
        self.ui = ui
        inner = QWidget(); v = QVBoxLayout(inner); v.setContentsMargins(36, 24, 36, 30); v.setSpacing(14)
        top = QFrame(); top.setObjectName("panel"); top.setStyleSheet("#panel{background:qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 #13283a,stop:1 #15202b);border:1px solid #24435e;border-radius:10px}")
        th = QHBoxLayout(top); th.setContentsMargins(26, 22, 26, 22)
        col = QVBoxLayout()
        t = lbl("EX CONNECT"); t.setStyleSheet("font-size:30px;font-weight:900;letter-spacing:3px;background:transparent"); col.addWidget(t)
        s = lbl("The service inside HYPERION DIGITAL EX that installs, updates and launches every EX app and game, right here.", "muted", True); s.setStyleSheet("background:transparent;color:%s" % MUTED); col.addWidget(s)
        self.state = lbl(""); self.state.setStyleSheet("font-size:16px;font-weight:800;background:transparent"); col.addWidget(self.state)
        th.addLayout(col, 1)
        self.stats = {}
        for k in ("CONNECTED APPS", "AVAILABLE", "DOWNLOADS", "PLAYING"):
            c = QVBoxLayout(); n = lbl("0"); n.setStyleSheet("font-size:34px;font-weight:900;color:%s;background:transparent" % ACCENT); n.setAlignment(Qt.AlignCenter)
            c.addWidget(n); kk = lbl(k, "small"); kk.setAlignment(Qt.AlignCenter); kk.setStyleSheet("background:transparent;color:%s" % MUTED); c.addWidget(kk); th.addSpacing(18); th.addLayout(c); self.stats[k] = n
        v.addWidget(top)
        btns = QHBoxLayout()
        rb = QPushButton("Sync catalog && scan for installed apps"); rb.clicked.connect(lambda: (ui.svc.refresh(), ui.svc.scan(), ui.refresh_all())); btns.addWidget(rb)
        btns.addStretch(1); v.addLayout(btns)
        self.table = QGridLayout(); self.table.setHorizontalSpacing(18); self.table.setVerticalSpacing(8)
        tb = QFrame(); tb.setObjectName("panel"); tbl = QVBoxLayout(tb); tbl.setContentsMargins(18, 14, 18, 14); tbl.addLayout(self.table)
        v.addWidget(tb)
        self.details = lbl("", "small", True); v.addWidget(self.details)
        v.addStretch(1)
        lay = QVBoxLayout(self); lay.setContentsMargins(0, 0, 0, 0); lay.addWidget(scroll(inner))

    def refresh(self):
        svc = self.ui.svc
        on = svc.online
        self.state.setText({True: "\u25CF  Online  ·  connected to the Teobokki release channel", False: "\u25CF  Offline  ·  installed apps still play; downloads resume when you are back", None: "\u25CF  Connecting…"}[on])
        self.state.setStyleSheet("font-size:15px;font-weight:800;background:transparent;color:%s" % {True: "#9be57c", False: "#f29a9a", None: ORANGE}[on])
        self.stats["CONNECTED APPS"].setText(str(svc.connected_count())); self.stats["AVAILABLE"].setText(str(len(svc.catalog)))
        self.stats["DOWNLOADS"].setText(str(len([j for j in svc.jobs if j.state not in ("done", "cancelled")]))); self.stats["PLAYING"].setText(str(len(svc.running)))
        clear_layout(self.table)
        for c, h in enumerate(("", "APP", "INSTALLED", "LATEST", "SOURCE", "STATUS")):
            self.table.addWidget(lbl(h, "small"), 0, c)
        for r, a in enumerate(svc.catalog.values(), 1):
            ic = QLabel(); ic.setPixmap(pix(art(a["id"], "icon.png")).scaled(22, 22, Qt.KeepAspectRatio, Qt.SmoothTransformation)); self.table.addWidget(ic, r, 0)
            n = lbl(a["name"]); n.setStyleSheet("font-weight:700"); self.table.addWidget(n, r, 1)
            inf = svc.installed.get(a["id"]) or {}
            self.table.addWidget(lbl(inf.get("version", "—")), r, 2); self.table.addWidget(lbl(svc.latest_version(a["id"])), r, 3)
            self.table.addWidget(lbl(inf.get("source", "Not installed"), "muted"), r, 4)
            st = svc.status(a["id"]); s = lbl({"play": "\u25CF Connected", "playing": "\u25B6 Playing", "update": "\u2B06 Update available", "install": "Available"}.get(st, st.capitalize()))
            s.setStyleSheet("font-weight:700;color:%s" % {"play": "#9be57c", "playing": "#9be57c", "update": ACCENT, "install": MUTED}.get(st, ORANGE)); self.table.addWidget(s, r, 5)
        self.table.setColumnStretch(4, 1)
        syn = time.strftime("%d %b %Y %H:%M", time.localtime(svc.synced_at)) if svc.synced_at else "never"
        self.details.setText("Catalog synced: %s  ·  Library folder: %s  ·  Install method: %s  ·  Downloads: %s" % (
            syn, svc.library_dir(), "Setup (silent)" if svc.settings.get("method", "setup") == "setup" else "Portable zip into library", os.path.join(svc.dir, "downloads")))


class SettingsPage(QWidget):
    def __init__(self, ui):
        super().__init__()
        self.ui = ui; svc = ui.svc
        inner = QWidget(); v = QVBoxLayout(inner); v.setContentsMargins(36, 24, 36, 30); v.setSpacing(12)
        v.addWidget(lbl("SETTINGS", "h2"))
        p = QFrame(); p.setObjectName("panel"); pl = QVBoxLayout(p); pl.setContentsMargins(20, 16, 20, 16); pl.setSpacing(10)
        pl.addWidget(lbl("Library folder (EX CONNECT zip installs)", None))
        r = QHBoxLayout(); self.lib = QLineEdit(svc.library_dir()); r.addWidget(self.lib, 1)
        b = QPushButton("Browse…"); b.clicked.connect(self.browse); r.addWidget(b); pl.addLayout(r)
        pl.addWidget(lbl("Install method", None))
        self.method = QComboBox(); self.method.addItems(["Setup installer, silent (recommended)", "Portable zip into the library folder"])
        self.method.setCurrentIndex(0 if svc.settings.get("method", "setup") == "setup" else 1); pl.addWidget(self.method)
        self.startup = QCheckBox("Launch HYPERION DIGITAL EX when Windows starts"); self.startup.setChecked(bool(svc.settings.get("startup"))); pl.addWidget(self.startup)
        sv = QPushButton("Save settings"); sv.setObjectName("primary"); sv.clicked.connect(self.save); sv.setFixedWidth(200); pl.addWidget(sv)
        v.addWidget(p)
        u = QFrame(); u.setObjectName("panel"); ul = QVBoxLayout(u); ul.setContentsMargins(20, 16, 20, 16)
        ul.addWidget(lbl("HYPERION DIGITAL EX  v%s" % APP_VERSION, None))
        self.ust = lbl("", "muted", True); ul.addWidget(self.ust)
        ub = QPushButton("Check for updates"); ub.clicked.connect(ui.check_self_update); ub.setFixedWidth(200); ul.addWidget(ub)
        ul.addWidget(lbl(COPYRIGHT, "small"))
        v.addWidget(u); v.addStretch(1)
        lay = QVBoxLayout(self); lay.setContentsMargins(0, 0, 0, 0); lay.addWidget(scroll(inner))

    def browse(self):
        d = QFileDialog.getExistingDirectory(self, "Library folder", self.lib.text())
        if d:
            self.lib.setText(os.path.normpath(d))

    def save(self):
        s = self.ui.svc.settings
        s["library"] = self.lib.text().strip() or os.path.join(self.ui.svc.dir, "library")
        s["method"] = "setup" if self.method.currentIndex() == 0 else "zip"
        s["startup"] = self.startup.isChecked(); set_startup(s["startup"])
        self.ui.svc.save(); self.ui.svc.scan(); self.ui.refresh_all()
        QMessageBox.information(self, APP_NAME, "Settings saved.")


def set_startup(on):
    if not xc.WIN or not getattr(sys, "frozen", False):
        return
    import winreg
    k = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_SET_VALUE)
    if on:
        winreg.SetValueEx(k, APP_NAME, 0, winreg.REG_SZ, '"%s" --minimized' % sys.executable)
    else:
        try:
            winreg.DeleteValue(k, APP_NAME)
        except OSError:
            pass


class UpdateDialog(QDialog):
    """'Update available' prompt for HYPERION DIGITAL EX itself: Update now (resumable download, SHA-256 check,
    silent Setup, relaunch) or Later (no more prompts this session)."""
    prog = Signal(float, str)
    failed = Signal(str)

    def __init__(self, main, lj):
        super().__init__(main)
        self.main, self.lj = main, lj
        self.setWindowTitle("HYPERION DIGITAL EX update"); self.setModal(False); self.setFixedWidth(560)
        self.setStyleSheet("QDialog{background:%s;border:1px solid %s}" % (PANEL, LINE))
        v = QVBoxLayout(self); v.setContentsMargins(26, 24, 26, 22); v.setSpacing(12)
        top = QHBoxLayout(); top.setSpacing(16)
        ic = QLabel(); ic.setPixmap(QPixmap(res("assets", "icon256.png")).scaled(76, 76, Qt.KeepAspectRatio, Qt.SmoothTransformation)); top.addWidget(ic, 0, Qt.AlignTop)
        col = QVBoxLayout(); col.setSpacing(4)
        k = lbl("UPDATE AVAILABLE", "h2"); k.setStyleSheet("color:%s;font-size:12px;font-weight:800;letter-spacing:2px" % ACCENT); col.addWidget(k)
        t = lbl("HYPERION DIGITAL EX v%s" % lj.get("version"), None, True); t.setStyleSheet("font-size:21px;font-weight:900"); col.addWidget(t)
        col.addWidget(lbl("You have v%s. The update installs in the background and HYPERION DIGITAL EX restarts by itself." % APP_VERSION, "muted", True))
        top.addLayout(col, 1); v.addLayout(top)
        nb = QFrame(); nb.setObjectName("infobox"); nl = QVBoxLayout(nb); nl.setContentsMargins(14, 10, 14, 12)
        nl.addWidget(lbl("WHAT'S NEW", "small"))
        n = lbl(lj.get("notes") or "Improvements and fixes.", None, True); n.setStyleSheet("font-size:13px;color:#c9d6e3"); nl.addWidget(n)
        v.addWidget(nb)
        self.bar = QProgressBar(); self.bar.setRange(0, 1000); self.bar.setTextVisible(False); self.bar.setFixedHeight(10); self.bar.hide(); v.addWidget(self.bar)
        self.info = lbl("", "small", True); self.info.hide(); v.addWidget(self.info)
        row = QHBoxLayout(); row.addStretch(1)
        self.later = QPushButton("Later"); self.later.setObjectName("ghost"); self.later.setMinimumWidth(110); self.later.clicked.connect(self.on_later); row.addWidget(self.later)
        self.go = QPushButton("Update now"); self.go.setObjectName("primary"); self.go.setMinimumWidth(170); self.go.clicked.connect(self.start); row.addWidget(self.go)
        v.addLayout(row)
        self.prog.connect(self.on_prog); self.failed.connect(self.on_fail)
        self.cancel_flag = False

    def on_later(self):
        self.main.update_dismissed = True; self.cancel_flag = True; self.close()

    def closeEvent(self, e):
        self.main.update_dismissed = True; self.cancel_flag = True; e.accept()

    def on_prog(self, f, text):
        self.bar.setValue(int(f * 1000)); self.info.setText(text)

    def on_fail(self, msg):
        self.info.setText(msg); self.go.setEnabled(True); self.go.setText("Try again"); self.later.setEnabled(True)

    def start(self):
        self.go.setEnabled(False); self.go.setText("Updating\u2026"); self.bar.show(); self.info.show(); self.cancel_flag = False
        import threading
        threading.Thread(target=self.run, daemon=True).start()

    def run(self):
        lj = self.lj; exe = sys.executable
        portable = getattr(sys, "frozen", False) and ("\\Programs\\" not in exe)
        url = (lj.get("portable_url") if portable else None) or lj.get("installer_url") or lj.get("url")
        if not url:
            return self.failed.emit("No download is listed for this update.")
        is_portable_dl = portable and url == lj.get("portable_url")
        name = url.rsplit("/", 1)[-1]
        dl = os.path.join(self.main.svc.dir, "downloads"); os.makedirs(dl, exist_ok=True)
        part = os.path.join(dl, name + ".part"); final = part[:-5]
        sha = size = None
        try:  # expected SHA-256 from the GitHub release
            m = __import__("re").search(r"/releases/download/([^/]+)/", url)
            rel = xc.fetch_json("https://api.github.com/repos/Teobokki/%s/releases/tags/%s" % (xc.SELF_REPO, m.group(1)))
            for a in rel.get("assets", []):
                if a["name"] == name:
                    sha = (a.get("digest") or "").replace("sha256:", "") or None; size = a.get("size")
        except Exception:
            pass
        backoff = 2
        while True:
            if self.cancel_flag:
                return
            have = os.path.getsize(part) if os.path.exists(part) else 0
            if size and have >= size:
                break
            try:
                req = xc.urllib.request.Request(url, headers=dict(xc.UA, **({"Range": "bytes=%d-" % have} if have else {})))
                with xc.urllib.request.urlopen(req, timeout=45, context=xc._ctx()) as r:
                    if have and r.status == 200:
                        have = 0
                    cr = r.headers.get("Content-Range")
                    if cr and cr.rsplit("/", 1)[-1].isdigit():
                        size = int(cr.rsplit("/", 1)[-1])
                    elif r.headers.get("Content-Length") and not size:
                        size = have + int(r.headers["Content-Length"])
                    done = have; t0 = time.time(); last = 0
                    with open(part, "ab" if have else "wb") as f:
                        while not self.cancel_flag:
                            b = r.read(32768)
                            if not b:
                                break
                            f.write(b); done += len(b)
                            if self.main.svc.throttle:
                                time.sleep(len(b) / (self.main.svc.throttle * 1024))
                            if time.time() - last > 0.2:
                                last = time.time(); sp = (done - have) / max(time.time() - t0, 0.01)
                                self.prog.emit(done / size if size else 0, "Downloading %s  \u00b7  %s of %s  \u00b7  %s/s" % (name, xc.human(done), xc.human(size), xc.human(sp)))
                backoff = 2
                if not size or (os.path.getsize(part) >= size):
                    break
            except xc.urllib.error.HTTPError as e:
                if e.code == 416:
                    break
                self.prog.emit(0, "HTTP %d, retrying\u2026" % e.code); time.sleep(backoff); backoff = min(backoff * 2, 30)
            except Exception as e:
                self.prog.emit(self.bar.value() / 1000, "Connection lost, retrying\u2026"); time.sleep(backoff); backoff = min(backoff * 2, 30)
        self.prog.emit(1, "Verifying SHA-256\u2026")
        import hashlib
        h = hashlib.sha256()
        with open(part, "rb") as f:
            for b in iter(lambda: f.read(1 << 20), b""):
                h.update(b)
        if (sha and h.hexdigest() != sha.lower()) or (size and os.path.getsize(part) != size):
            os.remove(part); return self.failed.emit("Verification failed (the download was corrupted). Press Try again.")
        os.replace(part, final)
        self.prog.emit(1, "Verified. Installing and restarting HYPERION DIGITAL EX\u2026")
        try:
            bat = os.path.join(self.main.svc.dir, "self_update.cmd")
            if is_portable_dl:
                body = 'ping 127.0.0.1 -n 3 >nul\r\nmove /y "%s" "%s" >nul\r\nstart "" "%s"\r\n' % (final, exe, exe)
            else:
                inst = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Programs", "HYPERION DIGITAL EX", "HYPERION DIGITAL EX.exe")
                relaunch = exe if (getattr(sys, "frozen", False) and not portable) else inst
                body = ('ping 127.0.0.1 -n 3 >nul\r\n"%s" /VERYSILENT /SUPPRESSMSGBOXES /NORESTART /CLOSEAPPLICATIONS\r\n'
                        'start "" "%s"\r\n' % (final, relaunch))
            with open(bat, "w") as f:
                f.write("@echo off\r\n" + body)
            if os.environ.get("HDX_UPDATE_DRYRUN"):
                return self.prog.emit(1, "Dry run: verified %s, would run %s" % (name, bat))
            subprocess.Popen(["cmd", "/c", bat], creationflags=xc.CREATE_NO_WINDOW, close_fds=True)
            self.main.svc.save()
            os._exit(0)
        except Exception as e:
            self.failed.emit("Could not start the update: %s" % e)


# ---------------------------------------------------------------- main window
class Main(QMainWindow):
    def __init__(self):
        super().__init__()
        self.bridge = Bridge(); self.bridge.event.connect(self.on_event)
        self.svc = xc.ExConnect(notify=lambda ev, aid: self.bridge.event.emit(ev, aid))
        self.setWindowTitle(APP_NAME); self.setWindowIcon(QIcon(res("assets", "icon.ico"))); self.resize(1440, 900); self.setMinimumSize(1180, 720)
        root = QWidget(); root.setObjectName("root"); self.setCentralWidget(root)
        v = QVBoxLayout(root); v.setContentsMargins(0, 0, 0, 0); v.setSpacing(0)
        # top bar
        top = QFrame(); top.setObjectName("topbar"); top.setFixedHeight(64); th = QHBoxLayout(top); th.setContentsMargins(12, 0, 12, 0); th.setSpacing(2)
        logo = QLabel(); logo.setPixmap(QPixmap(res("assets", "icon256.png")).scaled(46, 46, Qt.KeepAspectRatio, Qt.SmoothTransformation)); th.addWidget(logo)
        th.addSpacing(6); th.addWidget(lbl("HYPERION", "brand")); th.addWidget(lbl("DIGITAL EX", "brandsub")); th.addSpacing(14)
        self.navs = {}
        for key, t in (("store", "STORE"), ("library", "LIBRARY"), ("downloads", "DOWNLOADS"), ("connect", "EX CONNECT")):
            b = QPushButton(t); b.setObjectName("nav"); b.setCursor(Qt.PointingHandCursor); b.clicked.connect(lambda _=False, k=key: self.go(k)); th.addWidget(b); self.navs[key] = b
        th.addStretch(1)
        self.search = QLineEdit(); self.search.setPlaceholderText("Search the store"); self.search.setMinimumWidth(90); self.search.setMaximumWidth(150); self.search.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed); self.search.textChanged.connect(self.on_search); th.addWidget(self.search)
        self.selfupd = QPushButton(""); self.selfupd.setObjectName("update"); self.selfupd.hide(); self.selfupd.clicked.connect(self.do_self_update); th.addWidget(self.selfupd)
        self.gu = QPushButton("GAME UPDATES"); self.gu.setObjectName("nav"); self.gu.setCursor(Qt.PointingHandCursor); self.gu.setToolTip("Check all your games and apps for updates now")
        self.gu.clicked.connect(self.game_updates); th.addWidget(self.gu)
        self.wl = QPushButton("WISHLIST"); self.wl.setObjectName("nav"); self.wl.setCursor(Qt.PointingHandCursor); self.wl.setToolTip("Games on your wishlist")
        self.wl.clicked.connect(lambda: self.go("wishlist")); th.addWidget(self.wl)
        self.gu_busy = False; self.gu_dots = 0; self.gu_timer = QTimer(self, interval=250, timeout=self._gu_spin); self.gu_panel = None
        self.badge = QPushButton("\u25CF EX CONNECT"); self.badge.setObjectName("badge"); self.badge.setCursor(Qt.PointingHandCursor); self.badge.clicked.connect(lambda: self.go("connect")); th.addWidget(self.badge)
        gear = QPushButton("SETTINGS"); gear.setObjectName("nav"); gear.setToolTip("Settings"); gear.clicked.connect(lambda: self.go("settings")); th.addWidget(gear)
        self.navs["settings"] = gear; self.navs["wishlist"] = self.wl
        for b in list(self.navs.values()) + [self.gu]:
            fit(b)
        v.addWidget(top)
        self.stack = QStackedWidget(); v.addWidget(self.stack, 1)
        self.pages = {"store": StorePage(self), "library": LibraryPage(self), "product": ProductPage(self), "downloads": DownloadsPage(self),
                      "connect": ConnectPage(self), "settings": SettingsPage(self), "search": SearchPage(self),
                      "soon": SoonPage(self), "wishlist": WishlistPage(self)}
        for p in self.pages.values():
            self.stack.addWidget(p)
        # footer
        foot = QFrame(); foot.setObjectName("footer"); foot.setFixedHeight(30); fh = QHBoxLayout(foot); fh.setContentsMargins(16, 0, 16, 0)
        self.footl = lbl("", "small"); fh.addWidget(self.footl, 1); fh.addWidget(lbl(COPYRIGHT + " · v" + APP_VERSION, "small"))
        v.addWidget(foot)
        self.go("store")
        self.tick = QTimer(self, interval=1000, timeout=self.on_tick); self.tick.start()
        self._last_prog = 0
        self.svc.refresh()
        self.refresh_all()
        self.update_dismissed = False; self.update_dialog = None
        QTimer.singleShot(int(os.environ.get("HDX_FIRST_CHECK_MS", "5000")), self.auto_check)
        self.update_timer = QTimer(self, interval=5 * 60 * 1000, timeout=lambda: (self.auto_check(), self.svc.refresh())); self.update_timer.start()

    def go(self, key):
        self.current = key
        if key != "search" and self.search.text():
            self.search.blockSignals(True); self.search.clear(); self.search.blockSignals(False)
        self.stack.setCurrentWidget(self.pages[key])
        for k, b in self.navs.items():
            on = k == key or (key in ("product", "soon") and k == "store")
            b.setProperty("active", "true" if on else "false"); b.style().unpolish(b); b.style().polish(b)
        if key == "library" and not self.pages["library"].aid:
            first = next(iter(self.svc.installed), None) or next(iter(self.svc.catalog))
            self.pages["library"].select(first)
        self.refresh_all()

    def open_product(self, aid):
        if aid in SOON:
            self.pages["soon"].show_app(aid); self.go("soon"); return
        self.pages["product"].show_app(aid); self.go("product")

    def open_library(self, aid):
        self.go("library"); self.pages["library"].select(aid)

    def on_search(self, t):
        if t.strip():
            self.pages["search"].set_query(t); self.stack.setCurrentWidget(self.pages["search"])
        else:
            self.go("store")

    def on_event(self, ev, aid):
        if ev == "progress":
            now = time.time()
            if now - self._last_prog < 0.2:
                return
            self._last_prog = now
            self.refresh_light(); return
        if ev == "catalog":
            self.update_self_badge(); self.update_gu_badge()
        if ev == "gu_done":
            self.gu_busy = False; self.gu_timer.stop(); self.update_gu_badge(); self.refresh_all(); self.show_gu_panel(); return
        if ev == "selfcheck":
            self.on_self_checked(); return
        if ev == "error":
            QMessageBox.warning(self, APP_NAME, "EX CONNECT could not find a download for %s. Check your connection and try again." % self.svc.catalog[aid]["name"])
        self.refresh_all()

    def refresh_light(self):
        cur = self.stack.currentWidget()
        if cur in (self.pages["downloads"], self.pages["product"], self.pages["library"]):
            if cur is self.pages["library"]:
                cur.bar and cur.bar.refresh()
            else:
                cur.refresh()
        self.update_footer()

    def refresh_all(self):
        n = len([x for x in self.svc.wishlist() if x in SOON or x in self.svc.catalog])
        self.wl.setText("WISHLIST (%d)" % n if n else "WISHLIST"); fit(self.wl)
        for k in ("store", "product", "library", "downloads", "connect", "soon", "wishlist"):
            try:
                self.pages[k].refresh()
            except RuntimeError:
                pass
        self.update_footer()

    def update_footer(self):
        svc = self.svc; on = svc.online
        self.badge.setText(("\u25CF  EX CONNECT  ·  %d" % svc.connected_count()) if (self.selfupd.isVisible() or on) else ("\u25CF  EX CONNECT  ·  %s" % ({True: "Online", False: "Offline", None: "Connecting"}[on])))
        self.badge.setToolTip("EX CONNECT %s · %d apps connected" % ({True: "online", False: "offline", None: "connecting"}[on], svc.connected_count()))
        self.badge.setMinimumWidth(self.badge.sizeHint().width())
        self.badge.setProperty("off", "true" if on is False else "false"); self.badge.style().unpolish(self.badge); self.badge.style().polish(self.badge)
        act = [j for j in svc.jobs if j.state in ("downloading", "verifying", "installing", "queued")]
        if act:
            j = act[0]; a = svc.catalog[j.app_id]["name"]
            t = "%s %s  %d%%" % ({"downloading": "Downloading", "verifying": "Verifying", "installing": "Installing", "queued": "Queued"}[j.state], a, int(j.fraction * 100))
            if j.state == "downloading" and j.speed:
                t += "  ·  %s/s" % xc.human(j.speed)
            if len(act) > 1:
                t += "  ·  +%d queued" % (len(act) - 1)
            self.navs["downloads"].setText("DOWNLOADS (%d)" % len(act))
        else:
            t = ("Playing " + ", ".join(svc.catalog[x]["name"] for x in svc.running)) if svc.running else "EX CONNECT ready"
            self.navs["downloads"].setText("DOWNLOADS")
        self.footl.setText(t)

    def on_tick(self):
        if self.svc.running:
            self.refresh_light()
            if self.stack.currentWidget() is self.pages["library"]:
                self.pages["library"].refresh_stats()
            if self.stack.currentWidget() is self.pages["connect"]:
                self.pages["connect"].refresh()

    # ----- self update -----
    # ----- GAME UPDATES (instant check of every library app) -----
    def updates_list(self):
        return [aid for aid in self.svc.catalog if self.svc.status(aid) == "update"]

    def update_gu_badge(self):
        if self.gu_busy:
            return
        n = len(self.updates_list())
        self.gu.setText("GAME UPDATES (%d)" % n if n else "GAME UPDATES"); fit(self.gu)
        self.gu.setStyleSheet("QPushButton{color:%s}" % ORANGE if n else "")

    def _gu_spin(self):
        self.gu_dots = (self.gu_dots + 1) % 4
        self.gu.setText("CHECKING" + "." * self.gu_dots + " " * (3 - self.gu_dots)); fit(self.gu)

    def game_updates(self):
        if self.gu_busy:
            return
        if self.gu_panel and self.gu_panel.isVisible():
            self.gu_panel.close()
        self.gu_busy = True; self._gu_spin(); self.gu_timer.start()
        self.svc.refresh(on_done=lambda: self.bridge.event.emit("gu_done", ""))

    def show_gu_panel(self):
        svc = self.svc; ups = self.updates_list()
        p = QFrame(self, Qt.Popup); p.setObjectName("gupanel")
        p.setStyleSheet("#gupanel{background:%s;border:1px solid %s;border-radius:8px}" % (PANEL, ACCENT))
        v = QVBoxLayout(p); v.setContentsMargins(16, 14, 16, 14); v.setSpacing(10)
        took = getattr(svc, "last_check_secs", 0)
        head = lbl("GAME UPDATES", "h2"); v.addWidget(head)
        if svc.online is False:
            v.addWidget(lbl("Offline: could not reach the release channel. Try again when you are connected.", "muted", True))
        elif not ups:
            ok = lbl("\u2714  All games and apps are up to date"); ok.setStyleSheet("font-size:15px;font-weight:800;color:#9be57c"); v.addWidget(ok)
        else:
            t = lbl("%d update%s available" % (len(ups), "" if len(ups) == 1 else "s")); t.setStyleSheet("font-size:15px;font-weight:800;color:%s" % ORANGE); v.addWidget(t)
            for aid in ups:
                a = svc.catalog[aid]; inf = svc.installed.get(aid) or {}
                row = QHBoxLayout(); row.setSpacing(10)
                ic = QLabel(); ic.setPixmap(pix(art(aid, "icon.png")).scaled(32, 32, Qt.KeepAspectRatio, Qt.SmoothTransformation)); row.addWidget(ic)
                col = QVBoxLayout(); col.setSpacing(0); n = lbl(a["name"]); n.setStyleSheet("font-weight:800"); col.addWidget(n)
                old = ", ".join(v_ or "?" for _k, _e, v_ in svc.outdated_copies(aid))
                col.addWidget(lbl("installed %s  \u2192  %s" % (old or inf.get("version", "?"), svc.latest_version(aid)), "small")); row.addLayout(col, 1)
                b = QPushButton("\u2B06  UPDATE TO %s" % svc.latest_version(aid)); b.setObjectName("primary"); b.setProperty("mode", "update")
                b.clicked.connect(lambda _=False, aid=aid, b=b: (svc.install(aid, update=True), b.setEnabled(False), b.setText("QUEUED"), self.refresh_all()))
                row.addWidget(b); v.addLayout(row)
            ua = QPushButton("Update all"); ua.setObjectName("ghost")
            ua.clicked.connect(lambda: ([svc.install(x, update=True) for x in self.updates_list()], p.close(), self.go("downloads")))
            v.addWidget(ua, 0, Qt.AlignRight)
        v.addWidget(lbl("Checked %d apps in %.1f s  \u00b7  %s" % (len(svc.catalog), took, time.strftime("%H:%M:%S")), "small"))
        p.setFixedWidth(470); p.adjustSize()
        g = self.gu.mapToGlobal(self.gu.rect().bottomLeft())
        p.move(min(g.x(), self.mapToGlobal(self.rect().topRight()).x() - p.width() - 10), g.y() + 6)
        p.show(); self.gu_panel = p

    def update_self_badge(self):
        lj = self.svc.self_latest
        if lj and xc.vtuple(lj.get("version")) > xc.vtuple(APP_VERSION):
            self.selfupd.setText("\u2B06  Update to %s" % lj["version"]); self.selfupd.show()
            self.pages["settings"].ust.setText("Version %s is available. %s" % (lj["version"], lj.get("notes", "")))
        else:
            self.selfupd.hide()
            if lj:
                self.pages["settings"].ust.setText("You have the latest version.")

    def auto_check(self):
        """Background self-update check: a few seconds after launch, then every 30 minutes."""
        import threading

        def run():
            try:
                self.svc.self_latest = xc.fetch_json(xc.SELF_LATEST_URL)
            except Exception:
                return
            self.bridge.event.emit("selfcheck", "")
        threading.Thread(target=run, daemon=True).start()

    def on_self_checked(self, manual=False):
        self.update_self_badge(); self.update_footer()
        lj = self.svc.self_latest or {}
        newer = xc.vtuple(lj.get("version")) > xc.vtuple(APP_VERSION)
        if newer and (manual or not self.update_dismissed) and not (self.update_dialog and self.update_dialog.isVisible()):
            self.update_dialog = UpdateDialog(self, lj)
            self.update_dialog.show(); self.update_dialog.raise_(); self.update_dialog.activateWindow()

    def check_self_update(self):
        try:
            self.svc.self_latest = xc.fetch_json(xc.SELF_LATEST_URL)
        except Exception as e:
            self.pages["settings"].ust.setText("Could not check for updates (%s)." % type(e).__name__); return
        self.on_self_checked(manual=True)

    def do_self_update(self):
        self.on_self_checked(manual=True)

    def closeEvent(self, e):
        self.svc.save(); e.accept()


def smoke(win, out_dir, phase):
    """Automated walkthrough used for the release screenshots/tests (HDX_SMOKE=1)."""
    log = open(os.path.join(out_dir, "smoke_%s.log" % phase), "a", encoding="utf-8")
    def L(*a):
        log.write(time.strftime("%H:%M:%S ") + " ".join(str(x) for x in a) + "\n"); log.flush()
    def shot(name):
        win.grab().save(os.path.join(out_dir, name)); L("shot", name)
    target = os.environ.get("HDX_SMOKE_APP", "ex-network")
    steps = []
    def at(t, f):
        steps.append((t, f))
    if phase == "gu":
        def comp(name):
            base = win.grab(); p = win.gu_panel
            if p and p.isVisible():
                qp = QPainter(base); pos = win.mapFromGlobal(p.pos()); qp.drawPixmap(pos, p.grab()); qp.end()
            base.save(os.path.join(out_dir, name)); L("shot", name)
        at(7000, lambda: (L("click GAME UPDATES"), setattr(win, "_t0", time.time()), win.game_updates()))
        at(7300, lambda: comp("screenshot_game_updates_checking.png"))
        def wait():
            if win.gu_busy:
                return QTimer.singleShot(100, wait)
            L("check finished in %.2f s (svc %.2f s), updates: %s" % (time.time() - win._t0, win.svc.last_check_secs, win.updates_list()))
            QTimer.singleShot(800, lambda: comp("screenshot_game_updates.png"))
            QTimer.singleShot(1500, lambda: win.close())
        at(7400, wait)
    elif phase == "dvupdate":
        at(7000, lambda: (L("dv", win.svc.installed.get("dream-vine"), "latest", win.svc.latest_version("dream-vine"), "status", win.svc.status("dream-vine"), "outdated", win.svc.outdated_copies("dream-vine")), win.open_library("dream-vine")))
        at(8500, lambda: shot("screenshot_dv_update_button.png"))
        at(9000, lambda: win.open_product("dream-vine"))
        at(10000, lambda: shot("screenshot_dv_update_product.png"))
        at(10500, lambda: win.close())
    elif phase == "banner":
        at(6000, lambda: shot("screenshot_store_banner.png"))
        at(7000, lambda: win.pages["store"].banner.clicked.emit())
        at(8500, lambda: (L("scroll after click", win.pages["store"].sc.verticalScrollBar().value()), shot("screenshot_banner_click_games.png")))
        at(9500, lambda: win.close())
    elif phase == "wishlist2":
        def chk():
            win.resize(1180, 720); QApplication.processEvents()
            L("top bar @%d:" % win.width(), [(b.text(), b.width(), b.sizeHint().width()) for b in (win.gu, win.wl, win.badge, win.navs["settings"])] + [(k, b.width(), b.sizeHint().width()) for k, b in win.navs.items()], "search", win.search.width())
            win.resize(1440, 900); QApplication.processEvents(); win.go("wishlist")
        at(4000, chk)
        at(5500, lambda: (L("size", win.width(), win.height()), shot(os.environ.get("HDX_SMOKE_NAME", "screenshot_wishlist_v112.png"))))
        at(6000, lambda: win.close())
    elif phase == "wishlist":
        at(4000, lambda: (win.svc.toggle_wishlist("fireout-shine", True), win.open_product("fireout-shine")))
        at(5500, lambda: shot("screenshot_fireout_shine.png"))
        at(6000, lambda: win.go("wishlist"))
        at(7000, lambda: shot("screenshot_wishlist.png"))
        at(7500, lambda: win.close())
    elif phase == "featured":
        def both():
            f = win.pages["store"].featured; ims = []
            for k in range(f.stack.count()):
                f.go(k); QApplication.processEvents(); ims.append(f.grab())
            out = QPixmap(ims[0].width(), sum(i.height() + 16 for i in ims)); out.fill(QColor(BG)); qp = QPainter(out); y = 0
            for i in ims:
                qp.drawPixmap(0, y, i); y += i.height() + 16
            qp.end(); out.save(os.path.join(out_dir, os.environ.get("HDX_SMOKE_NAME", "screenshot_featured.png"))); L("shot featured")
        at(5000, both)
        at(6000, lambda: win.close())
    elif phase == "update":
        def comp(name):
            d = win.update_dialog
            base = win.grab(); qp = QPainter(base); qp.fillRect(base.rect(), QColor(0, 0, 0, 140))
            dg = d.grab(); qp.drawPixmap((base.width() - dg.width()) // 2, (base.height() - dg.height()) // 2, dg); qp.end()
            base.save(os.path.join(out_dir, name)); L("shot", name)
        at(9000, lambda: (L("dialog", bool(win.update_dialog), win.svc.self_latest and win.svc.self_latest.get("version")), comp("screenshot_update_prompt.png")))
        at(10000, lambda: win.update_dialog.start())
        at(16000, lambda: comp("screenshot_update_downloading.png"))
        at(36000, lambda: (L("info", win.update_dialog.info.text()), comp("screenshot_update_verified.png")))
        at(41000, lambda: win.close())
    elif phase == "1":
        at(7000, lambda: (L("online", win.svc.online, "installed", sorted(win.svc.installed)), shot("screenshot_store_home.png")))
        at(9000, lambda: win.open_product("piknott-celestika"))
        at(10500, lambda: shot("screenshot_product_page.png"))
        at(11500, lambda: win.open_product(target))
        at(12500, lambda: (win.svc.install(target), L("install started", target)))
        at(19000, lambda: (shot("screenshot_product_downloading.png"), win.go("downloads")))
        at(20500, lambda: (shot("screenshot_download_in_progress.png"), L("job", vars_job(win.svc.job_for(target)))))
        at(21500, lambda: (L("hard exit mid-download to test resume"), win.svc.save(), os._exit(0)))
    else:
        at(4000, lambda: (L("after restart job", vars_job(win.svc.job_for(target))), win.go("downloads")))
        at(5500, lambda: (shot("screenshot_download_resumed.png"), setattr(win.svc, "throttle", 0)))
        def wait_done():
            j = win.svc.job_for(target)
            if j:
                L("waiting", vars_job(j)); QTimer.singleShot(2000, wait_done); return
            L("job finished; installed:", win.svc.installed.get(target)); L("jobs", [(x.state, x.error, getattr(x, "verified", "")) for x in win.svc.jobs])
            win.open_library(target)
            QTimer.singleShot(1500, lambda: (L("play ->", win.svc.play(target)), win.refresh_all()))
            QTimer.singleShot(9000, lambda: (shot("screenshot_library_playing.png"), L("running", list(win.svc.running), "status", win.svc.status(target))))
            QTimer.singleShot(10000, lambda: (win.go("connect"), None))
            QTimer.singleShot(11500, lambda: shot("screenshot_ex_connect.png"))
            QTimer.singleShot(12500, lambda: (win.search.setText("dream"), None))
            QTimer.singleShot(14000, lambda: shot("screenshot_search.png"))
            QTimer.singleShot(15000, lambda: (win.search.clear(), win.go("library"), win.pages["library"].select("dream-vine")))
            QTimer.singleShot(16500, lambda: shot("screenshot_library.png"))
            def end():
                for aid, (p, t0) in list(win.svc.running.items()):
                    L("stopping", aid, "pid", p.pid); p.kill()
                QTimer.singleShot(2500, lambda: (L("playtime", win.svc.state["playtime"]), L("SMOKE OK"), win.close()))
            QTimer.singleShot(18000, end)
        at(7000, wait_done)
    for t, f in steps:
        QTimer.singleShot(t, f)


def vars_job(j):
    return None if not j else {"state": j.state, "done": j.done, "total": j.total, "err": j.error}


def main():
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    app = QApplication(sys.argv); app.setApplicationName(APP_NAME); app.setOrganizationName(PUBLISHER)
    app.setStyle("Fusion"); app.setStyleSheet(QSS); app.setWindowIcon(QIcon(res("assets", "icon.ico")))
    f = QFont("Segoe UI", 10); f.setFamilies(["Segoe UI", "Yu Gothic UI", "Meiryo", "MS Gothic", "Arial"]); app.setFont(f)
    if xc.WIN:
        try:
            import ctypes
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("EXInc.HyperionDigitalEX")
        except Exception:
            pass
    w = Main()
    if "--minimized" in sys.argv:
        w.showMinimized()
    else:
        w.show()
    if os.environ.get("HDX_SMOKE"):
        smoke(w, os.environ.get("HDX_SMOKE_OUT", "."), os.environ["HDX_SMOKE"])
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
