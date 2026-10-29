# HYPERION DIGITAL EX 1.1.11

The store catalog is now remote. New and changed games and apps arrive through the store's checks, with no store rebuild.

- Titles, descriptions, install and registry names and art come from `catalog/catalog.json` + `assets/apps/<id>/` on main. They are read at main's current commit, so the copy is never stale.
- The catalog is fetched on startup, on window focus, every 10 minutes, on CHECK FOR UPDATES and on the new **CHECK FOR STORE UPDATES** button. The Store and Library refresh live; no restart is needed.
- New or changed art is downloaded only when its size/sha256 changes, and it is cached in `%LOCALAPPDATA%\HYPERION DIGITAL EX\catalog\`.
- Every entry is validated. A bad entry is skipped, never a crash, and unknown future fields are ignored (`schema`).
- Downloads are allowed only from github.com/Teobokki.
- When offline, the store uses the last saved catalog. The built-in list is only used on the very first run.
- New titles get a **NEW** badge. Results read "Store updated: 1 new title …" or "Store is up to date".
- Kept from 1.1.10: update detection, the UPDATES page, a single store window, and per-user installs with no admin.

©2026 EX Inc./HYPERION DIGITAL ©2026
