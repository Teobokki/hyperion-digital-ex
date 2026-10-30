"""EX CONNECT - the HYPERION DIGITAL EX service that installs, updates, detects and launches EX apps.
Resumable (HTTP Range) downloads that survive restarts, SHA-256 verification, silent Inno Setup installs.
©2026 EX Inc./HYPERION DIGITAL ©2026"""
import hashlib, json, os, re, shutil, ssl, subprocess, sys, threading, time, urllib.request, urllib.error, zipfile
from ex_catalog import CATALOG, KNOWN_SIZES
import ex_remote as rm

APP_VERSION = "1.1.12"
UA = {"User-Agent": "HYPERION-DIGITAL-EX/" + APP_VERSION + " (EX CONNECT)"}
RAW = "https://raw.githubusercontent.com/Teobokki/%s/main/latest.json"
API = "https://api.github.com/repos/Teobokki/%s/releases/tags/v%s"
SELF_REPO = "hyperion-digital-ex"
SELF_LATEST_URL = os.environ.get("HDX_SELF_LATEST_URL") or (RAW % SELF_REPO)
WIN = sys.platform == "win32"
BUNDLED_ART = os.path.join(getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__))), "assets", "apps")
CREATE_NO_WINDOW = 0x08000000


def vtuple(v):
    """'1.0.5.1' -> (1, 0, 5, 1); always 4 parts so '1.0.5' == '1.0.5.0' and 1.0.5.1 > 1.0.5."""
    t = [int(x) for x in re.findall(r"\d+", str(v or ""))[:4]]
    return tuple(t + [0] * (4 - len(t)))


def clean_env():
    """Environment for child processes (games, Setups, update scripts).

    A PyInstaller onefile parent exports _PYI_* / _MEIPASS2 variables. If a child PyInstaller app (or the same exe
    relaunched after an update) inherits them, it reuses the parent's _MEI temp folder: the old code keeps running and
    the parent shows 'Failed to remove temporary directory'. Strip them and ask the child's bootloader to start fresh."""
    env = {k: v for k, v in os.environ.items() if not (k.upper().startswith("_PYI") or k.upper().startswith("_MEIPASS")
                                                        or k.upper() in ("TCL_LIBRARY", "TK_LIBRARY", "QT_PLUGIN_PATH", "QML2_IMPORT_PATH"))}
    mei = getattr(sys, "_MEIPASS", None)
    if mei and "PATH" in env:
        env["PATH"] = os.pathsep.join(x for x in env["PATH"].split(os.pathsep) if not os.path.normcase(x).startswith(os.path.normcase(mei)))
    env["PYINSTALLER_RESET_ENVIRONMENT"] = "1"
    return env


def safe_cwd():
    return os.environ.get("TEMP") or os.path.expanduser("~")


def data_dir():
    base = os.environ.get("LOCALAPPDATA") or os.path.expanduser("~/.local/share")
    d = os.path.join(base, "HYPERION DIGITAL EX")
    os.makedirs(d, exist_ok=True)
    return d


def downloads_folder():
    return os.path.join(os.path.expanduser("~"), "Downloads")


def _ctx():
    try:
        return ssl.create_default_context()
    except Exception:
        return None


NOCACHE = {"Cache-Control": "no-cache, no-store, max-age=0", "Pragma": "no-cache", "Expires": "0"}


def fetch_json(url, timeout=12):
    url += ("&" if "?" in url else "?") + "t=%d" % int(time.time() * 1000)     # cache-buster
    req = urllib.request.Request(url, headers=dict(UA, **NOCACHE))
    with urllib.request.urlopen(req, timeout=timeout, context=_ctx()) as r:
        return json.loads(r.read(2_000_000).decode("utf-8-sig"))


def main_sha(repo, timeout=8):
    """Commit SHA of main, read from git's smart-HTTP ref list on github.com (not CDN-cached, no API rate limit)."""
    req = urllib.request.Request("https://github.com/Teobokki/%s.git/info/refs?service=git-upload-pack" % repo,
                                 headers=dict(NOCACHE, **{"User-Agent": "git/2.45 " + UA["User-Agent"]}))
    with urllib.request.urlopen(req, timeout=timeout, context=_ctx()) as r:
        m = re.search(rb"([0-9a-f]{40}) refs/heads/main\b", r.read(400_000))
    return m.group(1).decode() if m else None


def fetch_bytes(url, limit, timeout=20):
    if not rm.allowed_url(url):
        raise ValueError("blocked URL")
    req = urllib.request.Request(url, headers=dict(UA, **NOCACHE))
    with urllib.request.urlopen(req, timeout=timeout, context=_ctx()) as r:
        return r.read(limit)


def fetch_latest(repo, timeout=8, path="latest.json"):
    """latest.json exactly as it is on main right now.

    1.1.10: raw.githubusercontent.com caches main/latest.json for 5 minutes and IGNORES query strings (a fresh '?t=' is
    still an x-cache HIT), so the old cache-buster did nothing. Reading it at main's current commit SHA gives a URL that
    has never been cached. Falls back to main (busted, no-cache) and then to the API copy."""
    errs = []
    try:
        sha = main_sha(repo, timeout)
        if sha:
            return fetch_json("https://raw.githubusercontent.com/Teobokki/%s/%s/%s" % (repo, sha, path), timeout), "main@" + sha[:7]
    except Exception as e:
        errs.append(e)
    try:
        return fetch_json("https://raw.githubusercontent.com/Teobokki/%s/main/%s" % (repo, path), timeout), "raw main"
    except Exception as e:
        errs.append(e)
    import base64
    c = fetch_json("https://api.github.com/repos/Teobokki/%s/contents/%s?ref=main" % (repo, path), timeout)
    return json.loads(base64.b64decode(c["content"]).decode("utf-8-sig")), "api"


def file_version(path):
    if not WIN:
        return None
    try:
        import ctypes
        from ctypes import wintypes
        ver = ctypes.windll.version
        size = ver.GetFileVersionInfoSizeW(path, None)
        if not size:
            return None
        buf = ctypes.create_string_buffer(size)
        ver.GetFileVersionInfoW(path, 0, size, buf)
        p = ctypes.c_void_p(); ln = wintypes.UINT()
        if not ver.VerQueryValueW(buf, "\\", ctypes.byref(p), ctypes.byref(ln)):
            return None
        ffi = ctypes.cast(p, ctypes.POINTER(ctypes.c_uint32 * 13)).contents
        ms, ls = ffi[2], ffi[3]
        parts = [ms >> 16, ms & 0xFFFF, ls >> 16, ls & 0xFFFF]   # all 4 parts: 1.0.5.1 must not read as 1.0.5
        if parts[3] == 0:
            parts = parts[:3]
        return ".".join(str(x) for x in parts)
    except Exception:
        return None


def uninstall_entries():
    """All Inno/MSI uninstall registry entries (HKCU + HKLM, both views)."""
    out = []
    if not WIN:
        return out
    import winreg
    roots = [(winreg.HKEY_CURRENT_USER, 0), (winreg.HKEY_LOCAL_MACHINE, winreg.KEY_WOW64_64KEY),
             (winreg.HKEY_LOCAL_MACHINE, winreg.KEY_WOW64_32KEY)]
    for root, view in roots:
        try:
            k = winreg.OpenKey(root, r"Software\Microsoft\Windows\CurrentVersion\Uninstall", 0, winreg.KEY_READ | view)
        except OSError:
            continue
        i = 0
        while True:
            try:
                sub = winreg.EnumKey(k, i)
            except OSError:
                break
            i += 1
            try:
                sk = winreg.OpenKey(k, sub, 0, winreg.KEY_READ | view)
                e = {"key": sub}
                for n in ("DisplayName", "DisplayVersion", "InstallLocation", "UninstallString", "QuietUninstallString", "DisplayIcon"):
                    try:
                        e[n] = str(winreg.QueryValueEx(sk, n)[0])
                    except OSError:
                        pass
                if e.get("DisplayName"):
                    out.append(e)
            except OSError:
                pass
    return out


def reg_entry(key):
    """HKCU (then HKLM) ...\\Uninstall\\<AppId>_is1 for one title: its DisplayVersion / InstallLocation."""
    if not WIN or not key:
        return None
    import winreg
    for root, view in ((winreg.HKEY_CURRENT_USER, 0), (winreg.HKEY_LOCAL_MACHINE, winreg.KEY_WOW64_64KEY), (winreg.HKEY_LOCAL_MACHINE, winreg.KEY_WOW64_32KEY)):
        try:
            sk = winreg.OpenKey(root, "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\" + key, 0, winreg.KEY_READ | view)
        except OSError:
            continue
        e = {"key": key}
        for n in ("DisplayName", "DisplayVersion", "InstallLocation", "UninstallString", "QuietUninstallString", "DisplayIcon"):
            try:
                e[n] = str(winreg.QueryValueEx(sk, n)[0])
            except OSError:
                pass
        return e
    return None


def newest(*vs):
    """highest of the given version strings (all 4 parts compared numerically); None if none is known."""
    vs = [str(v) for v in vs if v and str(v) != "?" and re.search(r"\d", str(v))]
    return max(vs, key=vtuple) if vs else None


def _norm(s):
    return re.sub(r"[^A-Z0-9]", "", (s or "").upper().replace("\u2122", ""))


class Job:
    def __init__(self, **kw):
        self.app_id = kw["app_id"]; self.url = kw["url"]; self.name = kw["name"]; self.kind = kw.get("kind", "installer")
        self.part = kw["part"]; self.total = kw.get("total", 0); self.sha256 = kw.get("sha256"); self.version = kw.get("version")
        self.target = kw.get("target"); self.state = kw.get("state", "queued"); self.done = 0; self.speed = 0.0
        self.error = ""; self.pause_flag = False; self.cancel_flag = False; self.created = kw.get("created", time.time())
        if os.path.exists(self.part):
            self.done = os.path.getsize(self.part)

    def to_json(self):
        return {k: getattr(self, k) for k in ("app_id", "url", "name", "kind", "part", "total", "sha256", "version", "target", "state", "created")}

    @property
    def fraction(self):
        return (self.done / self.total) if self.total else 0.0


class ExConnect:
    """Thread-based service. `notify(event, app_id)` is called from worker threads (Qt signal in the UI)."""

    def __init__(self, notify=lambda *a: None):
        self.notify = notify
        self.dir = data_dir()
        self.state_path = os.path.join(self.dir, "state.json")
        self.lock = threading.RLock()
        self.state = self._load(self.state_path, {})
        self.state.setdefault("settings", {"library": os.path.join(self.dir, "library"), "method": "setup", "startup": False})
        self.state.setdefault("playtime", {}); self.state.setdefault("last_played", {}); self.state.setdefault("jobs", [])
        self.state.setdefault("ex_installs", {}); self.state.pop("wishlist", None)   # old saved wishlist data is ignored and dropped
        self.cache = self._load(os.path.join(self.dir, "catalog_cache.json"), {})
        # 1.1.11: the title list comes from the remote catalog.json (last good copy cached); ex_catalog.py is only the fallback
        self.catalog = {}; self.cat_dir = rm.cache_dir(self.dir); self.catalog_error = None; self.catalog_skipped = []
        self.cat_meta = {"schema": 1, "catalog_version": "built-in", "featured": ["fireout-shine"], "known_sizes": dict(KNOWN_SIZES),
                         "rows": rm.parse_rows({})}
        self.cat_source = "built-in"; self.catalog_sha = None; self.last_catalog_diff = ([], [])
        titles = []
        for a in CATALOG:
            try:
                titles.append(rm.validate_title(a))
            except Exception:
                pass
        doc = self._load(os.path.join(self.cat_dir, "catalog.json"), None)
        if doc:
            try:
                self.cat_meta, titles, self.catalog_skipped = rm.parse(doc); self.cat_source = "cached"; self.catalog_sha = doc.get("_sha")
            except Exception:
                pass
        self.installed = {}; self.jobs = []
        first = "seen_titles" not in self.state
        self.state.setdefault("seen_titles", {})
        self._apply_titles(titles)
        if first:                               # nothing is NEW on the very first run
            self.state["seen_titles"] = {aid: 0 for aid in self.catalog}
        self.online = None; self.synced_at = self.cache.get("synced_at"); self.self_latest = None
        self.check_errors = {}; self.checked_at = {}; self.sources = {}; self._sig = None; self._refreshing = threading.Lock()
        self.installed = {}; self.running = {}
        self.jobs = [Job(**j) for j in self.state["jobs"] if j.get("state") not in ("done", "cancelled") and j.get("app_id") in self.catalog]
        for j in self.jobs:
            if j.state in ("downloading", "queued", "verifying", "error"):
                j.state = "queued"  # survive restarts: carry on where we left off
        self.throttle = float(os.environ.get("HDH_THROTTLE_KBPS", "0") or 0)
        self._wake = threading.Event()
        self.scan()
        threading.Thread(target=self._worker, daemon=True).start()

    # ---------- persistence ----------
    def _load(self, p, d):
        try:
            with open(p, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return d

    def save(self):
        with self.lock:
            self.state["jobs"] = [j.to_json() for j in self.jobs if j.state not in ("done", "cancelled")]
            tmp = self.state_path + ".tmp"
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(self.state, f, indent=1)
            os.replace(tmp, self.state_path)

    @property
    def settings(self):
        return self.state["settings"]

    def library_dir(self):
        d = self.settings.get("library") or os.path.join(self.dir, "library")
        os.makedirs(d, exist_ok=True)
        return d

    # ---------- remote store catalog (1.1.11) ----------
    def _apply_titles(self, titles):
        """swap in a new title list; keeps live latest.json / asset data; returns (new ids, changed ids)"""
        old = self.catalog; new = {}
        for t in titles:
            d = dict(t); o = old.get(t["id"]) or {}; c = self.cache.get("apps", {}).get(t["id"], {})
            for k in ("latest", "assets", "assets_ver"):
                d[k] = o.get(k) if o.get(k) is not None else c.get(k, {} if k == "assets" else None)
            new[t["id"]] = d
        for aid, o in old.items():              # a title dropped from the catalog stays while it is installed or downloading
            if aid not in new and (aid in self.installed or self.job_for(aid)):
                new[aid] = o
        added = [a for a in new if a not in old]
        changed = [a for a in new if a in old and rm.fingerprint(new[a]) != rm.fingerprint(old[a])]
        seen = self.state["seen_titles"]
        for a in new:
            seen.setdefault(a, time.time())
        self.catalog = new
        return added, changed

    def is_new(self, aid):
        t = self.state.get("seen_titles", {}).get(aid, 0)
        return bool(t) and time.time() - t < 14 * 86400

    def rows(self):
        """1.1.12: ordered store sections from catalog.json (GAMES, APPS & TOOLS, EBOOKS, ...)"""
        return self.cat_meta.get("rows") or rm.parse_rows({})

    def row_of(self, aid):
        t = self.catalog.get(aid) or {}
        rid = t.get("row") or rm.row_key(self.rows(), t.get("category")) or "APPS"
        return next((r for r in self.rows() if r["id"] == rid), self.rows()[-1])

    def featured(self):
        return [a for a in self.cat_meta.get("featured", []) if a in self.catalog] or list(self.catalog)[:1]

    def sync_catalog(self):
        """read catalog.json at main's commit SHA, validate, fetch changed art, apply. Returns (new ids, changed ids)."""
        sha = main_sha(rm.REPO)
        if not sha:
            raise ValueError("no main branch")
        doc = fetch_json("https://raw.githubusercontent.com/%s/%s/%s/%s" % (rm.OWNER, rm.REPO, sha, rm.PATH))
        meta, titles, skipped = rm.parse(doc)
        art_changed, errs = rm.sync_art(self.dir, titles, sha, fetch_bytes, BUNDLED_ART)
        added, changed = self._apply_titles(titles)
        changed = sorted(set(changed) | (set(art_changed) - set(added)))
        self.cat_meta, self.catalog_skipped, self.cat_source, self.catalog_sha = meta, skipped, "live main@" + sha[:7], sha
        self.catalog_art_errors = errs; self.catalog_error = None
        doc["_sha"] = sha
        tmp = os.path.join(self.cat_dir, "catalog.json.tmp")
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(doc, f, ensure_ascii=False)
        os.replace(tmp, os.path.join(self.cat_dir, "catalog.json"))
        self.save()
        return added, changed

    def check_store(self, on_done=None):
        """CHECK FOR STORE UPDATES: catalog.json + art only (game versions are CHECK FOR UPDATES)"""
        def run():
            try:
                self.last_catalog_diff = self.sync_catalog(); self.store_check = ("ok", self.last_catalog_diff, time.time())
            except Exception as e:
                self.catalog_error = "%s: %s" % (type(e).__name__, str(e)[:100]); self.store_check = ("error", self.catalog_error, time.time())
            self.notify("store_checked", "")
            if on_done:
                on_done()
        threading.Thread(target=run, daemon=True).start()

    def art_path(self, aid, name):
        p = os.path.join(self.cat_dir, "art", aid, name)
        return p if os.path.exists(p) else None

    # ---------- catalog sync ----------
    def refresh(self, block=False, on_done=None):
        def run():
            t_start = time.time()
            ok = 0
            threads = []

            def one(aid):
                nonlocal ok
                app = self.catalog[aid]
                try:
                    lj, src = fetch_latest(app.get("latest_repo") or app["repo"], timeout=8, path=app.get("latest_path") or "latest.json")
                    if not lj.get("version"):
                        raise ValueError("latest.json has no version")
                    ok += 1
                except Exception as e:      # 1.1.10: remembered and shown - no silent 'up to date' from stale data
                    self.check_errors[aid] = "%s: %s" % (type(e).__name__, str(e)[:80]); return
                self.check_errors.pop(aid, None); self.checked_at[aid] = time.time(); self.sources[aid] = src
                app["latest"] = lj
                ver = str(lj.get("version", app["version"]))
                if app.get("assets_ver") == ver and app.get("assets"):
                    return
                try:
                    rel = fetch_json(API % (app["repo"], ver))
                    app["assets"] = {a["name"]: {"size": a.get("size", 0), "sha256": (a.get("digest") or "").replace("sha256:", "") or None}
                                     for a in rel.get("assets", [])}
                    app["assets_ver"] = ver
                except Exception:
                    pass
            if not self._refreshing.acquire(blocking=False):      # one sync at a time
                if on_done:
                    on_done()
                return
            try:
                diff = self.sync_catalog()
                self.last_catalog_diff = diff
                if diff[0] or diff[1]:
                    self.notify("catalog_changed", "")
            except Exception as e:                  # offline / bad file: keep the last good (cached) catalog
                self.catalog_error = "%s: %s" % (type(e).__name__, str(e)[:100]); self.last_catalog_diff = ([], [])
            for aid in list(self.catalog):
                t = threading.Thread(target=one, args=(aid,), daemon=True); t.start(); threads.append(t)
            try:
                self.self_latest = fetch_json(SELF_LATEST_URL)
            except Exception:
                pass
            for t in threads:
                t.join(20)
            self.online = ok > 0
            if ok:
                self.synced_at = time.time()
                apps = {aid: {"latest": a.get("latest"), "assets": a.get("assets", {}), "assets_ver": a.get("assets_ver")} for aid, a in list(self.catalog.items())}
                try:
                    with open(os.path.join(self.dir, "catalog_cache.json"), "w", encoding="utf-8") as f:
                        json.dump({"apps": apps, "synced_at": self.synced_at}, f)
                except Exception:
                    pass
                self.cache = {"apps": apps, "synced_at": self.synced_at}
            self._refreshing.release()
            self.scan()
            self.last_check = time.time(); self.last_check_secs = time.time() - t_start
            self.notify("catalog", "")
            if on_done:
                on_done()
        if block:
            run()
        else:
            threading.Thread(target=run, daemon=True).start()

    def latest_version(self, aid):
        a = self.catalog[aid]
        return str((a.get("latest") or {}).get("version") or a["version"])

    def notes(self, aid):
        return (self.catalog[aid].get("latest") or {}).get("notes", "")

    def _asset(self, aid, kind):
        a = self.catalog[aid]; lj = a.get("latest") or {}
        ver = self.latest_version(aid)
        if kind == "installer":
            url = lj.get("installer_url") or lj.get("url")
        elif kind == "portable":
            url = lj.get("portable_url")
        else:
            url = lj.get("full_url")
        if not url and not lj:  # offline fallback: well-known asset names
            url = None
        if not url or not rm.allowed_url(url):       # 1.1.11: downloads only from github.com/Teobokki
            return None
        name = urllib.request.unquote(url.rsplit("/", 1)[-1])
        fresh = a.get("assets_ver") == ver       # 1.1.10: asset lists of an OLDER release are never used to reject a new file
        meta = (a.get("assets") or {}).get(name, {}) if fresh else {}
        if fresh and a.get("assets") and name not in a["assets"]:
            return None  # e.g. latest.json lists a zip the release doesn't carry
        return {"url": url, "name": name, "size": meta.get("size") or self.cat_meta.get("known_sizes", {}).get(name) or KNOWN_SIZES.get(name, 0), "sha256": meta.get("sha256"), "version": ver}

    def install_choice(self, aid):
        """(kind, asset) that EX CONNECT would use for a fresh install."""
        prefer = ["installer", "zip"] if self.settings.get("method", "setup") == "setup" else ["zip", "installer"]
        for k in prefer:
            a = self._asset(aid, k)
            if a:
                return k, a
        return None, None

    def size_text(self, aid):
        k, a = self.install_choice(aid)
        return human(a["size"]) if a and a["size"] else "—"

    # ---------- detection ----------
    def scan(self):
        entries = uninstall_entries()
        local = os.environ.get("LOCALAPPDATA", "")
        found = {}
        for aid, app in self.catalog.items():
            exe = app["exe"]; info = None
            # 1. the title's own Inno Setup key: HKCU\...\Uninstall\<AppId>_is1 (DisplayVersion + InstallLocation),
            #    then any Apps & features entry whose name matches (installs made by older Setups)
            own = reg_entry(app.get("reg"))
            names = [_norm(x) for x in (app["name"], app["folder"]) if _norm(x)]     # (a katakana-only name normalises to '' and matched every entry)
            cands = ([own] if own else []) + [e for e in entries if any(_norm(e["DisplayName"]).startswith(n) for n in names)]
            for e in cands:
                loc = e.get("InstallLocation", "").strip('"')
                p = os.path.join(loc, exe) if loc else ""
                if p and os.path.exists(p):
                    info = {"exe": p, "version": newest(file_version(p), e.get("DisplayVersion")), "source": "Setup install",
                            "reg_version": e.get("DisplayVersion"), "file_version": file_version(p),
                            "uninstall": e.get("QuietUninstallString") or e.get("UninstallString")}
                    break
            # 2. default per-user install folder (%LOCALAPPDATA%\Programs\<folder>)
            if not info and local:
                p = os.path.join(local, "Programs", app["folder"], exe)
                if os.path.exists(p):
                    un = os.path.join(local, "Programs", app["folder"], "unins000.exe")
                    info = {"exe": p, "version": file_version(p), "source": "Setup install", "file_version": file_version(p),
                            "uninstall": ('"%s"' % un) if os.path.exists(un) else None}
            # 3. EX CONNECT library (zip installs)
            if not info:
                root = os.path.join(self.library_dir(), aid)
                p = find_exe(root, exe)
                if p:
                    mark = self._load(os.path.join(root, "ex_connect_install.json"), {})
                    info = {"exe": p, "version": file_version(p) or mark.get("version"), "source": "EX CONNECT library", "library": root}
            # 4. portable copies in Downloads (tracked even when a Setup install exists, so they get updated too)
            portables = []
            for n in app.get("portable", []):
                p = os.path.join(downloads_folder(), n)
                if os.path.exists(p):
                    portables.append({"exe": p, "version": file_version(p) or self.state["ex_installs"].get(p) or "?"})
            if not info and portables:
                info = {"exe": portables[0]["exe"], "version": portables[0]["version"], "source": "Portable (Downloads)", "portable": portables[0]["exe"]}
            if info:
                info["version"] = info.get("version") or self.state["ex_installs"].get(info["exe"]) or "?"
                info["portables"] = portables
                try:
                    info["mtime"] = os.path.getmtime(info["exe"])
                except OSError:
                    pass
                found[aid] = info
        self.installed = found
        return found

    def signature(self):
        """what is installed right now (paths, versions, exe times) - changes when a game updates itself outside the store"""
        return tuple(sorted((aid, i.get("exe"), i.get("version"), i.get("mtime"), tuple((pc["exe"], pc["version"]) for pc in i.get("portables", [])))
                            for aid, i in self.installed.items()))

    def rescan_changed(self):
        """cheap local re-check (registry + exe versions, no network); True if anything installed changed"""
        old = self._sig if self._sig is not None else self.signature()
        self.scan(); self._sig = self.signature()
        return self._sig != old

    def updates(self):
        """every installed title with a newer release (shown even while it is running)"""
        return [aid for aid in self.catalog if self.outdated_copies(aid)]

    def status(self, aid):
        """install | play | update | playing | queued | downloading | paused | verifying | installing | error"""
        j = self.job_for(aid)
        if j and j.state in ("queued", "downloading", "paused", "verifying", "installing", "error"):
            return j.state
        if aid in self.running:
            return "playing"
        inf = self.installed.get(aid)
        if not inf:
            return "install"
        if self.outdated_copies(aid):
            return "update"
        return "play"

    def outdated_copies(self, aid):
        """[(kind, exe, version)] of installed copies older than latest.json."""
        inf = self.installed.get(aid)
        if not inf:
            return []
        latest = vtuple(self.latest_version(aid)); out = []
        def old(v):
            return v in (None, "?") or latest > vtuple(v)
        main_kind = "portable" if inf.get("portable") else ("zip" if inf.get("library") else "installer")
        if old(inf.get("version")):
            out.append((main_kind, inf["exe"], inf.get("version")))
        for pc in inf.get("portables", []):
            if pc["exe"] != inf["exe"] and old(pc["version"]):
                out.append(("portable", pc["exe"], pc["version"]))
        return out

    # ---------- downloads ----------
    def job_for(self, aid):
        for j in self.jobs:
            if j.app_id == aid and j.state not in ("done", "cancelled"):
                return j
        return None

    def install(self, aid, update=False):
        if self.job_for(aid):
            return
        plan = []
        if update:
            for kind, exe, _v in self.outdated_copies(aid):
                if kind == "portable" and self._asset(aid, "portable"):
                    plan.append(("portable", self._asset(aid, "portable"), exe))
                elif kind == "zip" and self._asset(aid, "zip"):
                    plan.append(("zip", self._asset(aid, "zip"), None))
                elif kind != "portable":
                    k, a = self.install_choice(aid)
                    if a:
                        plan.append((k, a, None))
        if not plan:
            k, a = self.install_choice(aid)
            if a:
                plan.append((k, a, None))
        if not plan:
            self.notify("error", aid); return
        dl = os.path.join(self.dir, "downloads"); os.makedirs(dl, exist_ok=True)
        with self.lock:
            for kind, asset, target in plan:
                tag = "" if not target else "." + hashlib.sha1(target.lower().encode()).hexdigest()[:8]
                self.jobs.append(Job(app_id=aid, url=asset["url"], name=asset["name"], kind=kind, part=os.path.join(dl, asset["name"] + tag + ".part"),
                                     total=asset["size"], sha256=asset["sha256"], version=asset["version"], target=target))
        self.save(); self._wake.set(); self.notify("jobs", aid)

    def pause(self, aid):
        j = self.job_for(aid)
        if j and j.state in ("queued", "downloading"):
            j.pause_flag = True
            if j.state == "queued":
                j.state = "paused"
            self.save(); self.notify("jobs", aid)

    def resume(self, aid):
        j = self.job_for(aid)
        if j and j.state in ("paused", "error"):
            j.pause_flag = False; j.error = ""; j.state = "queued"; self.save(); self._wake.set(); self.notify("jobs", aid)

    def cancel(self, aid):
        j = self.job_for(aid)
        if not j:
            return
        j.cancel_flag = True
        if j.state != "downloading":
            self._finish_cancel(j)

    def _finish_cancel(self, j):
        j.state = "cancelled"
        try:
            os.remove(j.part)
        except OSError:
            pass
        self.save(); self.notify("jobs", j.app_id)

    def _worker(self):
        while True:
            nxt = None
            with self.lock:
                for j in self.jobs:
                    if j.state == "queued":
                        nxt = j; break
            if not nxt:
                self._wake.wait(2); self._wake.clear(); continue
            try:
                self._run(nxt)
            except Exception as e:  # never kill the service thread
                nxt.state = "error"; nxt.error = str(e)[:200]
            self.save(); self.notify("jobs", nxt.app_id)

    def _run(self, j):
        j.state = "downloading"; self.notify("jobs", j.app_id)
        backoff = 2
        while True:
            if j.cancel_flag:
                return self._finish_cancel(j)
            if j.pause_flag:
                j.state = "paused"; j.speed = 0; return
            have = os.path.getsize(j.part) if os.path.exists(j.part) else 0
            j.done = have
            if j.total and have >= j.total:
                break
            hdr = dict(UA)
            if have:
                hdr["Range"] = "bytes=%d-" % have
            try:
                req = urllib.request.Request(j.url, headers=hdr)
                with urllib.request.urlopen(req, timeout=45, context=_ctx()) as r:
                    mode = "ab"
                    if have and r.status == 200:
                        have = 0; mode = "wb"
                    cr = r.headers.get("Content-Range")
                    if cr and "/" in cr and cr.rsplit("/", 1)[1].isdigit():
                        j.total = int(cr.rsplit("/", 1)[1])
                    elif r.headers.get("Content-Length"):
                        j.total = have + int(r.headers["Content-Length"])
                    j.done = have; t0 = time.time(); b0 = have; last = 0
                    with open(j.part, mode) as f:
                        while True:
                            if j.cancel_flag or j.pause_flag:
                                break
                            chunk = r.read(65536 if not self.throttle else 8192)
                            if not chunk:
                                break
                            f.write(chunk); j.done += len(chunk)
                            now = time.time()
                            if self.throttle:
                                need = (j.done - b0) / (self.throttle * 1024) - (now - t0)
                                if need > 0:
                                    time.sleep(min(need, 1))
                                now = time.time()
                            if now - t0 > 0.5:
                                j.speed = (j.done - b0) / (now - t0)
                            if now - last > 0.25:
                                last = now; f.flush(); self.notify("progress", j.app_id)
                            if now - t0 > 6:
                                t0, b0 = now, j.done
                backoff = 2; j.error = ""
                if j.total and j.done >= j.total:
                    break
                if not j.total and not (j.cancel_flag or j.pause_flag):
                    break
            except urllib.error.HTTPError as e:
                if e.code == 416:
                    if j.total and have >= j.total:
                        break
                    os.remove(j.part); continue
                j.error = "HTTP %d, retrying…" % e.code
            except Exception as e:
                j.error = "Connection lost, retrying… (%s)" % type(e).__name__
            if j.error:
                self.notify("progress", j.app_id)
                for _ in range(int(backoff * 4)):
                    if j.cancel_flag or j.pause_flag:
                        break
                    time.sleep(0.25)
                backoff = min(backoff * 2, 30)
        # ---- verify ----
        j.state = "verifying"; j.speed = 0; self.notify("jobs", j.app_id)
        h = hashlib.sha256()
        with open(j.part, "rb") as f:
            for b in iter(lambda: f.read(1 << 20), b""):
                h.update(b)
        digest = h.hexdigest()
        size_ok = not j.total or os.path.getsize(j.part) == j.total
        if (j.sha256 and digest.lower() != j.sha256.lower()) or not size_ok:
            os.remove(j.part); j.state = "error"; j.error = "Verification failed: the download was corrupted. Press Resume to download it again."
            return
        j.verified = "SHA-256 " + digest[:16] + "…" + (" (matches GitHub release digest)" if j.sha256 else "")
        final = j.part[:-5]
        os.replace(j.part, final)
        # ---- install ----
        j.state = "installing"; self.notify("jobs", j.app_id)
        try:
            self._install_file(j, final)
            j.state = "done"
        except Exception as e:
            j.state = "error"; j.error = "Install failed: %s" % e
            try:
                os.replace(final, j.part)
            except OSError:
                pass
            return
        try:
            os.remove(final)
        except OSError:
            pass
        self.scan(); self.notify("installed", j.app_id)

    def _install_file(self, j, path):
        app = self.catalog[j.app_id]
        if j.kind == "installer":
            # 1.1.10: per-user Setup (PrivilegesRequired=lowest), started DETACHED from the store with a clean environment and
            # RunAsInvoker, so it never asks for admin/UAC and is not tied to the store's process or _MEI folder
            env = clean_env(); env["__COMPAT_LAYER"] = "RunAsInvoker"
            flags = (0x00000008 | 0x00000200) if WIN else 0        # DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP
            pr = subprocess.Popen([path, "/VERYSILENT", "/SUPPRESSMSGBOXES", "/NORESTART", "/SP-", "/CLOSEAPPLICATIONS"],
                                  creationflags=flags, env=env, cwd=safe_cwd(), close_fds=True,
                                  stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            rc = pr.wait()
            if rc != 0:
                raise RuntimeError("Setup exit code %d" % rc)
            self.scan()
            inf = self.installed.get(j.app_id)
            if inf:
                self.state["ex_installs"][inf["exe"]] = j.version
        elif j.kind == "zip":
            root = os.path.join(self.library_dir(), j.app_id)
            tmp = root + ".new"
            shutil.rmtree(tmp, ignore_errors=True)
            with zipfile.ZipFile(path) as z:
                z.extractall(tmp)
            shutil.rmtree(root, ignore_errors=True)
            os.replace(tmp, root)
            with open(os.path.join(root, "ex_connect_install.json"), "w") as f:
                json.dump({"version": j.version, "app": app["name"], "installed": time.time()}, f)
            if not find_exe(root, app["exe"]):
                raise RuntimeError("%s not found in the zip" % app["exe"])
        elif j.kind == "portable":
            tgt = j.target or os.path.join(downloads_folder(), app["portable"][0])
            new = tgt + ".new"
            shutil.copyfile(path, new)
            if os.path.exists(tgt):
                old = tgt + ".old"
                try:
                    os.remove(old)
                except OSError:
                    pass
                os.replace(tgt, old)
            os.replace(new, tgt)
            self.state["ex_installs"][tgt] = j.version
        self.save()

    # ---------- play / uninstall ----------
    def play(self, aid):
        inf = self.installed.get(aid)
        if not inf or aid in self.running:
            return False
        exe = inf["exe"]
        p = subprocess.Popen([exe], cwd=os.path.dirname(exe), close_fds=True, env=clean_env())
        self.running[aid] = (p, time.time())
        self.state["last_played"][aid] = time.time(); self.save()
        threading.Thread(target=self._watch, args=(aid, p), daemon=True).start()
        self.notify("jobs", aid)
        return True

    def _watch(self, aid, p):
        t0 = time.time()
        p.wait()
        self.state["playtime"][aid] = self.state["playtime"].get(aid, 0) + (time.time() - t0)
        self.running.pop(aid, None); self.save(); self.notify("jobs", aid)

    def playtime(self, aid):
        t = self.state["playtime"].get(aid, 0)
        if aid in self.running:
            t += time.time() - self.running[aid][1]
        return t

    def uninstall(self, aid):
        inf = self.installed.get(aid)
        if not inf:
            return

        def run():
            try:
                if inf.get("uninstall"):
                    cmd = inf["uninstall"]
                    exe = cmd.split('"')[1] if cmd.startswith('"') else cmd.split(" /")[0]
                    subprocess.run([exe, "/VERYSILENT", "/SUPPRESSMSGBOXES", "/NORESTART"], creationflags=CREATE_NO_WINDOW if WIN else 0,
                                   env=clean_env(), cwd=safe_cwd(), close_fds=True)
                    time.sleep(1.5)
                elif inf.get("library"):
                    shutil.rmtree(inf["library"], ignore_errors=True)
                elif inf.get("portable"):
                    os.remove(inf["portable"])
            except Exception:
                pass
            self.scan(); self.notify("installed", aid)
        threading.Thread(target=run, daemon=True).start()


    def connected_count(self):
        return len(self.installed)


def find_exe(root, exe, depth=3):
    if not os.path.isdir(root):
        return None
    for cur, dirs, files in os.walk(root):
        if cur[len(root):].count(os.sep) >= depth:
            dirs[:] = []
        for f in files:
            if f.lower() == exe.lower():
                return os.path.join(cur, f)
    return None


def human(n):
    n = float(n or 0)
    for u in ("B", "KB", "MB", "GB"):
        if n < 1024 or u == "GB":
            return ("%.0f %s" if u in ("B", "KB") else "%.1f %s") % (n, u)
        n /= 1024


def human_time(s):
    s = int(s)
    if s < 60:
        return "%ds" % s
    if s < 3600:
        return "%dm %02ds" % (s // 60, s % 60)
    return "%dh %02dm" % (s // 3600, (s % 3600) // 60)
