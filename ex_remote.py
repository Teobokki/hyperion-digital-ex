"""HYPERION DIGITAL EX - remote store catalog (1.1.11).

The list of titles, their texts, install/registry names and art live in catalog/catalog.json + assets/apps/<id>/ on main
of Teobokki/hyperion-digital-ex. The store reads them at main's current commit SHA (never a cached CDN copy), validates
every entry, downloads new or changed art into %LOCALAPPDATA%\\HYPERION DIGITAL EX\\catalog\\, and keeps the last good
copy for offline use. The built-in ex_catalog.py is only the first-run / offline fallback.
©2026 EX Inc./HYPERION DIGITAL ©2026"""
import hashlib, json, os, re

OWNER = "Teobokki"
REPO = "hyperion-digital-ex"
PATH = "catalog/catalog.json"
SCHEMA = 1                                    # newer schemas are read too: unknown fields are ignored
ROWS = {"GAMES": "Games", "APPS": "Apps & Tools", "Games": "Games", "Apps & Tools": "Apps & Tools"}
RE_ID = re.compile(r"^[a-z0-9][a-z0-9-]{1,48}$")
RE_REPO = re.compile(r"^[A-Za-z0-9._-]{1,80}$")
RE_FILE = re.compile(r"^[^\\/:*?\"<>|]{1,80}$")
RE_ART = re.compile(r"^[a-z0-9_]{1,40}\.(png|jpg|jpeg)$")
RE_REG = re.compile(r"^\{[A-Za-z0-9-]{8,60}\}{1,2}_is1$")
RE_VER = re.compile(r"^\d+(\.\d+){0,3}$")
RE_SHA = re.compile(r"^[0-9a-f]{64}$")
ALLOWED = ("https://github.com/%s/" % OWNER, "https://raw.githubusercontent.com/%s/" % OWNER)


def allowed_url(u):
    """only downloads from github.com/Teobokki (and its raw files)"""
    return isinstance(u, str) and u.startswith(ALLOWED) and ".." not in u and len(u) < 400


def _s(t, k, n=4000, req=False):
    v = t.get(k)
    if v is None and not req:
        return None
    if not isinstance(v, str) or not v.strip() or len(v) > n:
        raise ValueError(k)
    return v


def validate_title(t):
    """one catalog entry -> clean dict for the store, or raises ValueError (the entry is then skipped)"""
    if not isinstance(t, dict):
        raise ValueError("not an object")
    out = {}
    out["id"] = _s(t, "id", 50, True)
    if not RE_ID.match(out["id"]):
        raise ValueError("id")
    out["name"] = _s(t, "name", 80, True)
    row = t.get("row", t.get("category"))
    if row not in ROWS:
        raise ValueError("row")
    out["category"] = ROWS[row]
    out["repo"] = _s(t, "repo", 80, True)
    if not RE_REPO.match(out["repo"]):
        raise ValueError("repo")
    for k in ("exe", "folder"):
        out[k] = _s(t, k, 80, True)
        if not RE_FILE.match(out[k]):
            raise ValueError(k)
    if not out["exe"].lower().endswith(".exe"):
        raise ValueError("exe")
    port = t.get("portable", [])
    if not isinstance(port, list) or not all(isinstance(p, str) and RE_FILE.match(p) and p.lower().endswith(".exe") for p in port):
        raise ValueError("portable")
    out["portable"] = list(port)[:6]
    reg = t.get("reg") or t.get("registry_key")
    if reg is not None and not (isinstance(reg, str) and RE_REG.match(reg)):
        raise ValueError("reg")
    out["reg"] = reg
    out["app_id"] = t.get("app_id") if isinstance(t.get("app_id"), str) else None
    ver = str(t.get("version", "0"))
    out["version"] = ver if RE_VER.match(ver) else "0"
    lu = t.get("latest_url") or "https://raw.githubusercontent.com/%s/%s/main/latest.json" % (OWNER, out["repo"])
    m = re.match(r"^https://raw\.githubusercontent\.com/%s/([A-Za-z0-9._-]+)/main/([A-Za-z0-9._/-]+\.json)$" % OWNER, lu)
    if not m or ".." in lu:
        raise ValueError("latest_url")
    out["latest_url"] = lu; out["latest_repo"], out["latest_path"] = m.group(1), m.group(2)
    for k, n in (("genre", 200), ("tagline", 600), ("about", 6000), ("publisher", 120), ("developer", 120), ("release", 40)):
        v = t.get(k if k != "about" else ("description" if "description" in t else "about"))
        if v is not None:
            if not isinstance(v, str) or len(v) > n:
                raise ValueError(k)
            out[k] = v
    out.setdefault("genre", out["category"]); out.setdefault("tagline", ""); out.setdefault("about", out["tagline"])
    f = t.get("features", [])
    out["features"] = [x for x in f if isinstance(x, str) and len(x) < 400][:20] if isinstance(f, list) else []
    art = t.get("art", {})
    if not isinstance(art, dict):
        raise ValueError("art")
    clean = {}
    for name, meta in art.items():
        if not (isinstance(name, str) and RE_ART.match(name) and isinstance(meta, dict)):
            continue
        size = meta.get("size"); sha = meta.get("sha256")
        if not isinstance(size, int) or not (0 < size <= 15_000_000) or (sha is not None and not (isinstance(sha, str) and RE_SHA.match(sha))):
            continue
        clean[name] = {"size": size, "sha256": sha}
    out["art"] = clean
    return out


def parse(doc):
    """catalog.json -> (meta, [titles], [(index, reason) skipped]); raises only if the document itself is unusable"""
    if not isinstance(doc, dict) or not isinstance(doc.get("titles"), list):
        raise ValueError("catalog.json has no titles list")
    schema = doc.get("schema", 1)
    if not isinstance(schema, int) or schema < 1:
        raise ValueError("bad schema")
    titles, skipped, seen = [], [], set()
    for i, t in enumerate(doc["titles"][:200]):
        try:
            c = validate_title(t)
            if c["id"] in seen:
                raise ValueError("duplicate id")
            seen.add(c["id"]); titles.append(c)
        except Exception as e:
            skipped.append((i, "%s: %s" % (type(e).__name__, e)))
    if not titles:
        raise ValueError("catalog.json has no valid titles")
    feat = [x for x in doc.get("featured", []) if isinstance(x, str) and x in seen] if isinstance(doc.get("featured"), list) else []
    ks = doc.get("known_sizes", {})
    ks = {k: v for k, v in ks.items() if isinstance(k, str) and isinstance(v, int)} if isinstance(ks, dict) else {}
    meta = {"schema": schema, "catalog_version": doc.get("catalog_version"), "featured": feat or [titles[0]["id"]], "known_sizes": ks}
    return meta, titles, skipped


def cache_dir(base):
    d = os.path.join(base, "catalog"); os.makedirs(os.path.join(d, "art"), exist_ok=True)
    return d


def art_ok(path, meta):
    try:
        if os.path.getsize(path) != meta["size"]:
            return False
        if meta.get("sha256"):
            with open(path, "rb") as f:
                return hashlib.sha256(f.read()).hexdigest() == meta["sha256"]
        return True
    except OSError:
        return False


def sync_art(base, titles, sha, fetch_bytes, bundled=None):
    """download new / changed art for every title into the cache (art already identical in the store's own bundle is
    not downloaded); returns ({id: [changed files]}, [errors])"""
    changed, errs = {}, []
    root = os.path.join(cache_dir(base), "art")
    for t in titles:
        d = os.path.join(root, t["id"])
        for name, meta in t["art"].items():
            p = os.path.join(d, name)
            if art_ok(p, meta):
                continue
            if bundled and art_ok(os.path.join(bundled, t["id"], name), meta):
                if os.path.exists(p):          # the cached copy is outdated and the bundled one is current
                    os.remove(p); changed.setdefault(t["id"], []).append(name)
                continue
            url = "https://raw.githubusercontent.com/%s/%s/%s/assets/apps/%s/%s" % (OWNER, REPO, sha, t["id"], name)
            try:
                data = fetch_bytes(url, meta["size"] + 1)
                if len(data) != meta["size"] or (meta.get("sha256") and hashlib.sha256(data).hexdigest() != meta["sha256"]):
                    raise ValueError("size/sha256 mismatch")
                os.makedirs(d, exist_ok=True)
                with open(p + ".tmp", "wb") as f:
                    f.write(data)
                os.replace(p + ".tmp", p)
                changed.setdefault(t["id"], []).append(name)
            except Exception as e:
                errs.append("%s/%s: %s" % (t["id"], name, e))
    return changed, errs


def fingerprint(t):
    """what the UI shows for a title (texts, names, art hashes) - used to tell 'changed' titles apart"""
    keep = {k: v for k, v in t.items() if k not in ("latest", "assets", "assets_ver")}
    return hashlib.sha1(json.dumps(keep, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
