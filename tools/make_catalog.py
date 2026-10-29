"""Refresh catalog/catalog.json art hashes from assets/apps/<id>/ (and create it from ex_catalog.py the first time).

    python tools/make_catalog.py          # after editing catalog/catalog.json or adding/replacing art
Then commit + push catalog/catalog.json and assets/apps/<id>/ to main. No store rebuild is needed.
©2026 EX Inc./HYPERION DIGITAL ©2026"""
import hashlib, json, os, sys, time
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, ROOT)
import ex_remote as rm
OUT = os.path.join(ROOT, "catalog", "catalog.json")


def art_of(aid):
    d = os.path.join(ROOT, "assets", "apps", aid); out = {}
    for f in sorted(os.listdir(d)) if os.path.isdir(d) else []:
        if rm.RE_ART.match(f):
            b = open(os.path.join(d, f), "rb").read(); out[f] = {"size": len(b), "sha256": hashlib.sha256(b).hexdigest()}
    return out


if os.path.exists(OUT):
    doc = json.load(open(OUT, encoding="utf-8"))
else:
    from ex_catalog import CATALOG, KNOWN_SIZES, GAMES
    keys = ("id", "name", "repo", "genre", "tagline", "about", "features", "publisher", "developer", "release", "reg", "exe", "folder", "portable", "version")
    doc = {"schema": 1, "catalog_version": 1, "featured": ["fireout-shine"], "titles": [], "known_sizes": KNOWN_SIZES}
    for a in CATALOG:
        t = {"id": a["id"], "row": "GAMES" if a["category"] == GAMES else "APPS"}
        t.update({("description" if k == "about" else k): a[k] for k in keys if k in a and k != "id"})
        t["app_id"] = t["reg"][:-4].replace("}}", "}") if t.get("reg") else None
        t["latest_url"] = "https://raw.githubusercontent.com/Teobokki/%s/main/latest.json" % a["repo"]
        doc["titles"].append(t)
for t in doc["titles"]:
    t["art"] = art_of(t["id"])
doc["updated"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
meta, ok, skipped = rm.parse(doc)                     # same validation the store uses
for i, why in skipped:
    print("WARNING: entry %d would be SKIPPED by the store: %s" % (i, why))
os.makedirs(os.path.dirname(OUT), exist_ok=True)
json.dump(doc, open(OUT, "w", encoding="utf-8"), indent=1, ensure_ascii=False); open(OUT, "a").write("\n")
print("catalog.json: %d valid titles, %d skipped, art files %d" % (len(ok), len(skipped), sum(len(t["art"]) for t in ok)))
