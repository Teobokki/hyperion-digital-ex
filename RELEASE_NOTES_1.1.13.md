# HYPERION DIGITAL EX 1.1.13

Fixes "Could not check the store (… CERTIFICATE_VERIFY_FAILED … unable to get issuer cert)" on PCs where antivirus, a firewall or a network proxy scans HTTPS traffic.

- **Uses the Windows certificate store.** All store connections now check certificates against the Windows trust store. That covers the catalog, update checks, downloads, cover art and the GitHub API. The root certificates that HTTPS-scanning software installs live in that store, so they are trusted the way your browser trusts them.
- **Fallback.** If that check fails, the store tries again using the built-in Mozilla CA bundle together with every Windows ROOT/CA certificate.
- **Certificates are always checked.** Verification is never switched off.
- **Clearer message.** If the connection is still refused, the store tells you the likely cause instead of showing an OpenSSL error code.
- Per-user install, no admin. Everything from 1.1.12 is unchanged.

©2026 EX Inc./HYPERION DIGITAL ©2026
