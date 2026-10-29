# HYPERION DIGITAL EX 1.1.10

Game updates and changes are detected again, for every title.

- latest.json is read live at main's current commit, so it is never a cached copy. GitHub's raw CDN kept main/latest.json for 5 minutes and ignored the old cache-buster.
- Release downloads no longer depend on the GitHub API, which allows 60 calls an hour. Asset lists from an older release (for example THE ANULMENT 1.0.0.2) can no longer block the new Setup.
- Installed versions are read from each title's own uninstall key (HKCU ...\Uninstall\<AppId>_is1 DisplayVersion) and from its exe FileVersion. All four version parts are compared, so 1.0.0.4 > 1.0.0.
- The store checks on startup, when its window gets focus, with CHECK FOR UPDATES, and every 10 minutes. It re-reads installed versions every 15 s, so a game that updated itself shows up at once.
- New UPDATES page: every game or app with an update, installed vs latest version, UPDATE / UPDATE ALL. A title that could not be checked is flagged, never shown as "up to date".
- Product page shows LATEST VERSION and INSTALLED; Library shows ⬆ UPDATE.
- UPDATE runs the game's per-user Setup detached, with a clean environment and RunAsInvoker: no admin, no UAC.
- Only one store window runs at a time (opening it again brings the running window forward).

©2026 EX Inc./HYPERION DIGITAL ©2026
