# HYPERION DIGITAL EX 1.1.15

Fixes "Could not check the store (URLError: … getaddrinfo failed / Errno 11001)" when Windows DNS cannot resolve a GitHub raw host, even though github.com still opens in the browser.

- **Mirror fallbacks.** Catalog refresh, each title's `latest.json`, and cover art try several hosts in order: `raw.githubusercontent.com` → `cdn.jsdelivr.net/gh/Teobokki/...` → `raw.githack.com` / `rawcdn.githack.com` → GitHub Contents API.
- **IPv4 first.** When dual-stack DNS flakes, lookups prefer IPv4 (set `HDX_ALLOW_IPV6=1` to keep the old behaviour).
- **Short retries across mirrors.** One failed host no longer fails the whole store check.
- **Clearer status.** The Updates page shows which host served the catalog (`Store catalog: live cdn.jsdelivr.net main@…`). DNS failures say so instead of a raw `URLError`.
- **TLS unchanged.** Still uses `truststore` + certifi / Windows certificates from 1.1.13. Verification is never switched off.
- Per-user install, no admin. Everything from 1.1.14 is unchanged.

Until the store can refresh, you can install **MIYOYAZU DASH** from https://github.com/Teobokki/miyoyazu-dash/releases/tag/v1.0.1

©2026 EX Inc./HYPERION DIGITAL ©2026
