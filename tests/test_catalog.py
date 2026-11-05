"""HYPERION DIGITAL EX 1.1.12 - remote catalog tests (python -m unittest tests/test_catalog.py -v)"""
import copy, hashlib, json, os, sys, tempfile, unittest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
TMP = tempfile.mkdtemp(prefix="hdx_c_"); os.environ["LOCALAPPDATA"] = TMP; os.environ["HOME"] = TMP
import ex_connect as xc, ex_remote as rm
ROOT = os.path.join(os.path.dirname(__file__), "..")
DOC = json.load(open(os.path.join(ROOT, "catalog", "catalog.json"), encoding="utf-8"))
PNG = b"\x89PNG fake art bytes"


class T(unittest.TestCase):
    def test_live_file_is_valid_and_complete(self):
        meta, titles, skipped = rm.parse(DOC)
        self.assertEqual(skipped, [])
        self.assertEqual({t["id"] for t in titles}, {t["id"] for t in DOC["titles"]})
        for t in titles:
            self.assertTrue(t["reg"] and t["art"] and "icon.png" in t["art"], t["id"])

    def test_rows_are_data_driven(self):
        """1.1.12: sections come from catalog "rows"; EBOOKS is a portrait row; unknown rows are skipped"""
        meta, titles, skipped = rm.parse(DOC)
        self.assertEqual([r["id"] for r in meta["rows"]], ["GAMES", "APPS", "EBOOKS"])
        eb = meta["rows"][2]; self.assertEqual((eb["card"], eb["label"], eb["launch"], eb["front"]), ("portrait", "Ebooks", "READ", "book_front.jpg"))
        book = next(t for t in titles if t["id"] == "learn-japanese-easy")
        self.assertEqual((book["row"], book["category"]), ("EBOOKS", "Ebooks"))
        for n in ("book_front.jpg", "book_back.jpg", "icon.png", "capsule.jpg"):
            self.assertIn(n, book["art"])
        d = copy.deepcopy(DOC); d.pop("rows")                       # a catalog without rows: GAMES/APPS defaults, ebook skipped
        meta2, titles2, skipped2 = rm.parse(d)
        self.assertEqual([r["id"] for r in meta2["rows"]], ["GAMES", "APPS"]); self.assertEqual(len(skipped2), 1)
        d = copy.deepcopy(DOC); d["rows"].append({"id": "bad row", "card": "x"}); d["rows"].append({"id": "COMICS", "title": "COMICS", "card": "portrait"})
        meta3, _, _ = rm.parse(d); self.assertEqual([r["id"] for r in meta3["rows"]], ["GAMES", "APPS", "EBOOKS", "COMICS"])
        self.assertEqual(rm.parse_rows({"rows": [{"id": "EBOOKS", "card": "portrait"}]})[0]["id"], "GAMES")   # defaults always kept

    def test_bad_entries_are_skipped_not_fatal(self):
        d = copy.deepcopy(DOC); good = d["titles"][0]
        bad = [dict(good, id="../evil"), dict(good, id="x-exe", exe="..\\\\cmd.exe"), dict(good, id="x-url", latest_url="https://evil.example/latest.json"),
               dict(good, id="x-row", row="TOYS"), "not a dict", dict(good, id="x-art", art={"../../a.png": {"size": 3}})]
        d["titles"] += bad
        meta, titles, skipped = rm.parse(d)
        self.assertEqual(len(titles), len(DOC["titles"]) + 1)          # x-art kept, only its bad art file dropped
        self.assertEqual(len(skipped), 5)
        self.assertEqual(next(t for t in titles if t["id"] == "x-art")["art"], {})

    def test_future_schema_fields_tolerated(self):
        d = copy.deepcopy(DOC); d["schema"] = 2; d["something_new"] = {"a": 1}; d["titles"][0]["trailer"] = "x"
        meta, titles, _ = rm.parse(d); self.assertEqual(meta["schema"], 2); self.assertEqual(len(titles), len(DOC["titles"]))

    def test_only_teobokki_downloads(self):
        self.assertTrue(rm.allowed_url("https://github.com/Teobokki/the-anulment/releases/download/v1/x.exe"))
        self.assertTrue(rm.allowed_url("https://cdn.jsdelivr.net/gh/Teobokki/hyperion-digital-ex@main/catalog/catalog.json"))
        self.assertTrue(rm.allowed_url("https://raw.githack.com/Teobokki/hyperion-digital-ex/main/latest.json"))
        for u in ("https://github.com/someone/x/releases/download/v1/x.exe", "http://github.com/Teobokki/x", "https://github.com/Teobokki/../x",
                  "https://cdn.jsdelivr.net/gh/someone/x@main/x.json"):
            self.assertFalse(rm.allowed_url(u), u)

    def test_raw_urls_order(self):
        urls = rm.raw_urls("Teobokki", "hyperion-digital-ex", "main", "catalog/catalog.json")
        self.assertEqual([u.split("/")[2] for u in urls],
                         ["raw.githubusercontent.com", "cdn.jsdelivr.net", "raw.githack.com", "rawcdn.githack.com"])

    def test_sync_new_title_changed_listing_and_offline_fallback(self):
        svc = xc.ExConnect()
        d = copy.deepcopy(DOC); d["catalog_version"] = 99
        d["titles"][4]["tagline"] = "TEST tagline change"
        new = dict(copy.deepcopy(d["titles"][0]), id="ex-new-test", name="EX NEW TEST", art={"icon.png": {"size": len(PNG), "sha256": hashlib.sha256(PNG).hexdigest()}})
        d["titles"].append(new)
        xc.main_sha = lambda repo, timeout=8: "a" * 40
        xc.fetch_json = lambda url, timeout=12: copy.deepcopy(d)
        got = []
        xc.fetch_bytes = lambda url, limit, timeout=20: (got.append(url), PNG)[1]
        added, changed = svc.sync_catalog()
        self.assertIn("ex-new-test", added); self.assertIn("learn-japanese-easy", added); self.assertIn(d["titles"][4]["id"], changed)
        self.assertTrue(svc.is_new("ex-new-test")); self.assertFalse(svc.is_new("fireout-shine"))
        self.assertTrue(got and got[0].startswith("https://raw.githubusercontent.com/Teobokki/hyperion-digital-ex/" + "a" * 40 + "/assets/apps/ex-new-test/"))
        self.assertTrue(svc.art_path("ex-new-test", "icon.png"))
        self.assertEqual(svc.sync_catalog(), ([], []))                       # nothing new the second time
        # offline: a new service starts from the cached catalog, and a failed fetch keeps it
        xc.main_sha = lambda repo, timeout=8: (_ for _ in ()).throw(OSError("offline"))
        xc.fetch_repo_json = lambda *a, **k: (_ for _ in ()).throw(OSError("offline"))
        s2 = xc.ExConnect(); self.assertIn("ex-new-test", s2.catalog); self.assertEqual(s2.cat_source, "cached")
        with self.assertRaises(OSError):
            s2.sync_catalog()
        self.assertIn("ex-new-test", s2.catalog)


    def test_fetch_repo_json_falls_back_when_raw_dns_fails(self):
        """1.1.15: Errno 11001 on raw.githubusercontent.com must not fail the catalog; jsDelivr (or another mirror) serves it."""
        real = xc.fetch_json
        def boom(url, timeout=12):
            if "raw.githubusercontent.com" in url:
                raise OSError("[Errno 11001] getaddrinfo failed")
            return real(url, timeout)
        xc.fetch_json = boom
        try:
            doc, src = xc.fetch_repo_json(rm.REPO, rm.PATH, ref="main", timeout=12)
            self.assertEqual(doc.get("catalog_version"), DOC.get("catalog_version"))
            self.assertNotIn("raw.githubusercontent.com", src)
            self.assertTrue(any(h in src for h in ("cdn.jsdelivr.net", "raw.githack.com", "rawcdn.githack.com", "api.github.com")), src)
        finally:
            xc.fetch_json = real


if __name__ == "__main__":
    unittest.main()
