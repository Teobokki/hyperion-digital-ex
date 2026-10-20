"""EX CONNECT - the HYPERION DIGITAL EX service that installs, updates, detects and launches EX apps.
Resumable (HTTP Range) downloads that survive restarts, SHA-256 verification, silent Inno Setup installs.
©2026 EX Inc./HYPERION DIGITAL ©2026"""
import hashlib, json, os, re, shutil, ssl, subprocess, sys, threading, time, urllib.request, urllib.error, zipfile
from ex_catalog import CATALOG, KNOWN_SIZES

APP_VERSION = "1.1.2"
UA = {"User-Agent": "HYPERION-DIGITAL-EX/" + APP_VERSION + " (EX CONNECT)"}
RAW = "https://raw.githubusercontent.com/Teobokki/%s/main/latest.json"
API = "https://api.github.com/repos/Teobokki/%s/releases/tags/v%s"
SELF_REPO = "hyperion-digital-ex"
SELF_LATEST_URL = os.environ.get("HDX_SELF_LATEST_URL") or (RAW % SELF_REPO)
WIN = sys.platform == "win32"
CREATE_NO_WINDOW = 0x08000000


def vtuple(v):
    return tuple(int(x) for x in re.findall(r"\d+", str(v or ""))[:4]) or (0,)


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


def fetch_json(url, timeout=12):
    if url.startswith("https://raw.githubusercontent.com/"):  # cache-bust the raw CDN
        url += ("&" if "?" in url else "?") + "t=%d" % int(time.time() * 1000)
    req = urllib.request.Request(url, headers=dict(UA, **{"Cache-Control": "no-cache", "Pragma": "no-cache"}))
    with urllib.request.urlopen(req, timeout=timeout, context=_ctx()) as r:
        return json.loads(r.read(2_000_000).decode("utf-8"))


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
        return "%d.%d.%d" % (ms >> 16, ms & 0xFFFF, ls >> 16)
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
        self.state.setdefault("ex_installs", {}); self.state.setdefault("wishlist", [])
        self.catalog = {a["id"]: dict(a) for a in CATALOG}
        self.cache = self._load(os.path.join(self.dir, "catalog_cache.json"), {})
        for aid, c in self.cache.get("apps", {}).items():
            if aid in self.catalog:
                self.catalog[aid]["latest"] = c.get("latest"); self.catalog[aid]["assets"] = c.get("assets", {})
        self.online = None; self.synced_at = self.cache.get("synced_at"); self.self_latest = None
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
                    lj = fetch_json(RAW % app["repo"], timeout=8)
                    ok += 1
                except Exception:
                    try:  # fall back to the GitHub API copy of latest.json
                        import base64
                        c = fetch_json("https://api.github.com/repos/Teobokki/%s/contents/latest.json" % app["repo"], timeout=8)
                        lj = json.loads(base64.b64decode(c["content"]).decode("utf-8")); ok += 1
                    except Exception:
                        return
                app["latest"] = lj
                ver = str(lj.get("version", app["version"]))
                cached = self.cache.get("apps", {}).get(aid, {})
                if cached.get("assets_ver") == ver and cached.get("assets"):
                    app["assets"] = cached["assets"]; return
                try:
                    rel = fetch_json(API % (app["repo"], ver))
                    app["assets"] = {a["name"]: {"size": a.get("size", 0), "sha256": (a.get("digest") or "").replace("sha256:", "") or None}
                                     for a in rel.get("assets", [])}
                    app["assets_ver"] = ver
                except Exception:
                    pass
            for aid in self.catalog:
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
                apps = {aid: {"latest": a.get("latest"), "assets": a.get("assets", {}), "assets_ver": a.get("assets_ver")} for aid, a in self.catalog.items()}
                try:
                    with open(os.path.join(self.dir, "catalog_cache.json"), "w", encoding="utf-8") as f:
                        json.dump({"apps": apps, "synced_at": self.synced_at}, f)
                except Exception:
                    pass
                self.cache = {"apps": apps, "synced_at": self.synced_at}
            self.scan()
            self.last_check_secs = time.time() - t_start
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
        if not url:
            return None
        name = urllib.request.unquote(url.rsplit("/", 1)[-1])
        meta = (a.get("assets") or {}).get(name, {})
        if (a.get("assets") and name not in a["assets"]):
            return None  # e.g. latest.json lists a zip the release doesn't carry
        return {"url": url, "name": name, "size": meta.get("size") or KNOWN_SIZES.get(name, 0), "sha256": meta.get("sha256"), "version": ver}

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
            # 1. Inno Setup install registered in Apps & features
            for e in entries:
                if _norm(e["DisplayName"]).startswith(_norm(app["name"])) or _norm(e["DisplayName"]).startswith(_norm(app["folder"])):
                    loc = e.get("InstallLocation", "").strip('"')
                    p = os.path.join(loc, exe) if loc else ""
                    if p and os.path.exists(p):
                        info = {"exe": p, "version": file_version(p) or e.get("DisplayVersion"), "source": "Setup install",
                                "uninstall": e.get("QuietUninstallString") or e.get("UninstallString")}
                        break
            # 2. default per-user install folder
            if not info and local:
                p = os.path.join(local, "Programs", app["folder"], exe)
                if os.path.exists(p):
                    un = os.path.join(local, "Programs", app["folder"], "unins000.exe")
                    info = {"exe": p, "version": file_version(p), "source": "Setup install",
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
                found[aid] = info
        self.installed = found
        return found

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
            r = subprocess.run([path, "/VERYSILENT", "/SUPPRESSMSGBOXES", "/NORESTART", "/SP-", "/CLOSEAPPLICATIONS"],
                               creationflags=CREATE_NO_WINDOW if WIN else 0)
            if r.returncode != 0:
                raise RuntimeError("Setup exit code %d" % r.returncode)
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
        p = subprocess.Popen([exe], cwd=os.path.dirname(exe), close_fds=True)
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
                    subprocess.run([exe, "/VERYSILENT", "/SUPPRESSMSGBOXES", "/NORESTART"], creationflags=CREATE_NO_WINDOW if WIN else 0)
                    time.sleep(1.5)
                elif inf.get("library"):
                    shutil.rmtree(inf["library"], ignore_errors=True)
                elif inf.get("portable"):
                    os.remove(inf["portable"])
            except Exception:
                pass
            self.scan(); self.notify("installed", aid)
        threading.Thread(target=run, daemon=True).start()

    # ---------- wishlist (saved in the state file) ----------
    def wishlist(self):
        return list(self.state.get("wishlist", []))

    def on_wishlist(self, aid):
        return aid in self.state.get("wishlist", [])

    def toggle_wishlist(self, aid, on=None):
        wl = self.state.setdefault("wishlist", [])
        on = (aid not in wl) if on is None else on
        if on and aid not in wl:
            wl.append(aid)
        elif not on and aid in wl:
            wl.remove(aid)
        self.save()
        return on

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
