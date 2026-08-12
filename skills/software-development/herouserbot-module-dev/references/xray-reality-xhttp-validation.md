# Xray REALITY + XHTTP validation

Use this when maintaining Hero userbot modules that generate per-user Xray configs and VLESS links.

## Required proof before delivering a claimed working XHTTP fix

A generated JSON config parsing or a successful TCP connect is insufficient. Run an isolated end-to-end loop:

1. Start the generated server config on a temporary local port.
2. Derive the REALITY public key from the server private key using the same Xray binary.
3. Start a temporary SOCKS client using the generated UUID, port, XHTTP path, public key, SNI and short ID.
4. Fetch a known endpoint through SOCKS, e.g. `https://www.gstatic.com/generate_204`.
5. Require curl exit 0 and HTTP 204 before calling the transport working.

This validates the full chain: REALITY handshake, XHTTP exchange, VLESS auth and outbound traffic.

## Target compatibility finding

On Xray 26.7.28, direct REALITY + XHTTP testing showed target-dependent behavior:

| target | result |
|---|---|
| `www.microsoft.com:443` | REALITY handshake completes, then XHTTP fails with EOF/reset |
| `www.cloudflare.com:443` | E2E proxy request succeeds, HTTP 204 |
| `www.apple.com:443` | E2E proxy request succeeds, HTTP 204 |

For this module family, use `www.cloudflare.com:443` as the default SNI/target for newly created TCP+Vision and XHTTP users. Preserve user-customized targets. For old XHTTP users that still have the untouched `www.microsoft.com` defaults, migrate both SNI and target before regenerating and starting their config.

## XHTTP link/config rules

- Keep server and link `path` identical.
- Do not insert server-only XHTTP settings into a VLESS URI (`scMaxBufferedPosts`, `scMaxEachPostBytes`, `scStreamUpServerSecs`).
- Do not force `mode` or `extra` unless the client support and matching full server/client behavior were verified.
- For default direct REALITY XHTTP, start from the upstream minimal shape: `xhttpSettings` with `path` only.
- `TCP+Vision` requires `flow: xtls-rprx-vision` on both VLESS server client entry and VLESS URI.

## Delivery expectation

When the user asks for a repaired module, deliver an actual `.py` artifact only after syntax validation and the transport E2E result. Do not characterize a file as working based only on static config inspection.