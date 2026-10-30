# HYPERION DIGITAL EX 1.1.12

The store's sections now come from the catalog, and it has a new **EBOOKS** section.

- **Sections from `catalog.json`.** The rows on the Store page (GAMES, APPS & TOOLS, EBOOKS …) are read from the `rows` list in `catalog/catalog.json`. Each row sets its title, card style (`landscape` or `portrait`), verb and launch label. Future sections only need a catalog change, not a store rebuild. Catalogs without `rows` still show GAMES and APPS & TOOLS.
- **EBOOKS.** Books show their front cover as a card in book proportions. Their store page shows the front and back covers. **INSTALL** works the same as for any app, and an installed book shows **READ**.
- **Library filters.** Library has filter chips: **All · Games · Apps · Ebooks**. For books it shows reading time and when you last read them.
- Everything from 1.1.11 is unchanged: the remote catalog, live refresh, NEW badges, update detection, and per-user installs with no admin.

©2026 EX Inc./HYPERION DIGITAL ©2026
