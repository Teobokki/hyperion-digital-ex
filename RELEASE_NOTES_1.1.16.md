# HYPERION DIGITAL EX 1.1.16

Library now pins **CHIC EX** at the very top of every Library list (per row). Featured & Recommended stays CHIC EX as the main card.

- **Library pin.** `LIBRARY_PINNED_IDS` defaults to CHIC EX so it stays first even before a catalog refresh.
- **Catalog-driven pins.** `catalog.json` may set `library_pinned` (catalog_version 27); the store uses that when present, otherwise the built-in fallback.
- Everything from 1.1.15 (DNS mirror fallbacks, IPv4 prefer, TLS truststore) is unchanged.
- Per-user install, no admin.

©2026 EX Inc./HYPERION DIGITAL ©2026
