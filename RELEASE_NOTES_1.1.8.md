# HYPERION DIGITAL EX 1.1.8: update fixes

- **Fixed: "UPDATE TO 1.0.5.1" never went away for ファイアアウト・シャイン (FIREOUT SHINE).**
  - The store read only the first three parts of a game's version, so an installed 1.0.5.1 showed as "1.0.5". The update button stayed up even after the update had installed.
  - EX CONNECT now reads all four parts (1.0.5.1, 1.0.5.2, ...) for Setup installs, library installs and portable copies. Versions compare correctly, so 1.0.5 is the same as 1.0.5.0, and 1.0.5.1 is newer than 1.0.5.
- **Fixed: "Failed to remove temporary directory ...\_MEI..." warning.**
  - Games, Setups and the store's own update restart now start with a clean environment, without the PyInstaller variables from the store process.
  - A relaunched app now unpacks fresh instead of reusing the old temporary folder.
- Setups started by EX CONNECT run from %TEMP% and close a running copy of the game before replacing files.

Per-user install, no admin. Already on 1.1.7? Click **Update now** when HYPERION DIGITAL EX offers 1.1.8.

©2026 EX Inc./HYPERION DIGITAL ©2026
