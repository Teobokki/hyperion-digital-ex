"""HYPERION DIGITAL EX 1.1.10 - update detection tests (run on Linux: python -m unittest tests/test_updates.py -v).
The registry and exe version reads are mocked; latest.json is read LIVE from every title's GitHub repo."""
import os, sys, tempfile, unittest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
TMP = tempfile.mkdtemp(prefix="hdx_t_"); os.environ["LOCALAPPDATA"] = TMP; os.environ["HOME"] = TMP
import ex_connect as xc
from ex_catalog import CATALOG

# what we pretend is installed: (registry DisplayVersion, exe FileVersion)
FAKE = {"the-anulment": ("1.0.0", "1.0.0"), "fireout-shine": ("1.0.5.1", "1.0.5.1"), "ex-sports-sfc27": ("1.0.0", None),
        "dream-vine": ("1.3.2", "1.3.2"), "piknott-celestika": ("1.0.1", "1.0.1"), "hyperia": ("1.1.23", "1.1.23"),
        "ex-creator-studio": ("1.2.0", "1.2.0"), "ex-network": ("1.2.1", "1.2.1"), "ex-sudo-terminal": ("1.1.1", None),
        "fireout-revolution": ("1.0.3", "1.0.3")}
BY_REG = {a["reg"]: a for a in CATALOG}


def install_fake():
    vers = {}
    for a in CATALOG:
        d = os.path.join(TMP, "Programs", a["folder"]); os.makedirs(d, exist_ok=True)
        p = os.path.join(d, a["exe"]); open(p, "wb").close()
        vers[p] = FAKE[a["id"]][1]
    xc.file_version = lambda p: vers.get(p)
    xc.reg_entry = lambda key: (lambda a: a and {"key": key, "DisplayName": a["name"], "DisplayVersion": FAKE[a["id"]][0],
                                                   "InstallLocation": os.path.join(TMP, "Programs", a["folder"]) + os.sep})(BY_REG.get(key))
    xc.uninstall_entries = lambda: []
    return vers


class T(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.vers = install_fake()
        cls.svc = xc.ExConnect()
        cls.svc.refresh(block=True)

    def test_vtuple_four_parts(self):
        self.assertGreater(xc.vtuple("1.0.0.4"), xc.vtuple("1.0.0"))
        self.assertGreater(xc.vtuple("1.0.5.2"), xc.vtuple("1.0.5.1"))
        self.assertGreater(xc.vtuple("1.1.10"), xc.vtuple("1.1.9"))
        self.assertEqual(xc.vtuple("1.0.5"), xc.vtuple("1.0.5.0"))
        self.assertEqual(xc.newest("1.0.0", "1.0.0.4"), "1.0.0.4")

    def test_every_title_is_checked_live(self):
        self.assertEqual(self.svc.check_errors, {})
        for a in CATALOG:
            self.assertIn(a["id"], self.svc.checked_at, a["id"])

    def test_installed_version_comes_from_registry_and_exe(self):
        s = self.svc
        self.assertEqual(s.installed["the-anulment"]["version"], "1.0.0")
        self.assertEqual(s.installed["ex-sports-sfc27"]["version"], "1.0.0")     # no exe version: DisplayVersion
        self.assertEqual(s.installed["ex-sudo-terminal"]["version"], "1.1.1")

    def test_updates_detected(self):
        s = self.svc; ups = s.updates()
        for aid in CATALOG:
            aid = aid["id"]
            should = xc.vtuple(s.latest_version(aid)) > xc.vtuple(s.installed[aid]["version"])
            self.assertEqual(aid in ups, should, aid)
            self.assertEqual(s.status(aid), "update" if should else "play", aid)
        self.assertIn("the-anulment", ups)          # 1.0.0 -> 1.0.0.4

    def test_update_asset_is_the_new_setup(self):
        s = self.svc
        for aid in s.updates():
            k, a = s.install_choice(aid)
            self.assertEqual(k, "installer", aid)
            self.assertIn(s.latest_version(aid), a["url"], aid)

    def test_stale_old_release_assets_do_not_block_update(self):
        s = self.svc; app = s.catalog["the-anulment"]
        saved = (app.get("assets"), app.get("assets_ver"))
        app["assets"] = {"THE-ANULMENT-Setup-1.0.0.2.exe": {"size": 1}}; app["assets_ver"] = "1.0.0.2"   # what the user's cache held
        try:
            k, a = s.install_choice("the-anulment")
            self.assertIsNotNone(a); self.assertTrue(a["name"].endswith(s.latest_version("the-anulment") + ".exe"))
        finally:
            app["assets"], app["assets_ver"] = saved

    def test_outside_update_is_noticed(self):
        s = self.svc; s.rescan_changed()
        FAKE["the-anulment"] = ("1.0.0.4", "1.0.0.4")               # the game updated itself
        p = os.path.join(TMP, "Programs", "THE ANULMENT", "THE ANULMENT.exe"); self.vers[p] = "1.0.0.4"
        self.assertTrue(s.rescan_changed())
        self.assertEqual(s.installed["the-anulment"]["version"], "1.0.0.4")
        self.assertNotIn("the-anulment", s.updates())
        self.assertFalse(s.rescan_changed())
        FAKE["the-anulment"] = ("1.0.0", "1.0.0"); self.vers[p] = "1.0.0"; s.rescan_changed()     # back for the other tests

    def test_failed_check_is_not_up_to_date(self):
        old = xc.fetch_latest
        xc.fetch_latest = lambda repo, timeout=8: (_ for _ in ()).throw(OSError("offline"))
        try:
            svc = xc.ExConnect(); svc.refresh(block=True)
            self.assertEqual(set(svc.check_errors), {a["id"] for a in CATALOG})
            self.assertFalse(svc.online)
        finally:
            xc.fetch_latest = old


if __name__ == "__main__":
    install_fake(); svc = xc.ExConnect(); svc.refresh(block=True)
    print("%-20s %-12s %-12s %-10s %s" % ("TITLE", "INSTALLED", "LATEST", "RESULT", "SOURCE"))
    for a in CATALOG:
        i = svc.installed.get(a["id"]) or {}
        print("%-20s %-12s %-12s %-10s %s" % (a["id"], i.get("version"), svc.latest_version(a["id"]),
                                            "UPDATE" if a["id"] in svc.updates() else "up to date", svc.sources.get(a["id"], svc.check_errors.get(a["id"]))))
