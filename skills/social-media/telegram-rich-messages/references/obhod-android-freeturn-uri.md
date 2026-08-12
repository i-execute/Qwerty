# OBHOD Android freeturn:// URI Spec (Authoritative)

> Sources: `samosvalishe/free-turn-proxy/docs/uri.md` + `samosvalishe/turn-proxy-android/FreeturnLink.kt`
> Captured 2026-07-24 from session fixing Android link generation in OBHOD.

## Format

```
freeturn://<base64url(json)>
```

Payload is JSON, base64url encoded (no padding — Go `base64.RawURLEncoding`,
Python `base64.urlsafe_b64encode(...).rstrip("=")`). Versioned via `v` field.

## JSON Fields (complete)

| Key | CLI flag | Type | Android parser reads | Notes                                |
|-----|----------|------|----------------------|--------------------------------------|
| `v` | —        | int  | `optInt("v", -1)`    | Must be `1` — parser rejects others |
| `provider` | `-provider` | str | required (`optString`) | e.g. `"vk"` — empty rejected       |
| `peer` | `-peer`     | str | required (`optString`) | `ip:port` of VPS — empty rejected   |
| `transport` | `-transport` | str | `optString` | `tcp` \| `udp` (TURN relay transport) |
| `mode` | `-mode`       | str | `optString` | `udp` \| `tcp` (tunnel mode)          |
| `bond` | `-bond`       | bool | `optBoolean(_, false)` | Only with `mode=tcp`               |
| `obf` | `-obf-profile` | str | `optString` | `rtpopus` \| `rtpopus2` \| `rtpopus3`; omitted if `none` |
| `key` | `-obf-key`     | str | `optString` | Obfuscation key (hex), only with `obf` |
| `n` | `-n`             | int | `optInt(_, 0)` | Number of TURN streams             |
| `spc` | `-streams-per-cred` | int | `optInt(_, 0)` | Streams per VK cred cache        |
| `cid` | `-client-id`    | str | `optString` | Client ID — **must** be registered in `clients.json` allowlist |
| `listen` | `-listen`     | str | `optString` | Local `ip:port` for WG/Xray         |
| `dns` | `-dns-mode`     | str | `optString` | `plain` \| `doh` \| `auto`           |
| `dnss` | `-dns-servers` | str | `optString` | Custom DNS, comma-separated         |
| `mcap` | `-manual-captcha` | bool | `optBoolean(_, false)` | Manual VK captcha              |
| `name` | —              | str | `optString` | Client name/comment                  |
| `wg` | —                | str | `optString` | WireGuard config (embedded inline!)  |
| `mtu` | —               | int | `optInt(_, DEFAULT_WG_MTU)` | MTU — default if not set   |

**`-link` is NEVER in the payload** — it is unique per client and must be passed separately on the CLI / share screen as `-link "https://vk.ru/call/join/..."`.

## Critical Implementation Notes

### Android can import WG config from the link (`wg` field)

The Kotlin parser (`FreeturnLink.kt`) reads `wg` directly from the JSON payload
into `wgConf: String`. The Android app imports it atomically — no separate
WireGuard app import step needed. This was discovered late and the fix was to
build the WG conf in Python and embed it:

```python
metadata["wg"] = wg_conf  # Full [Interface]/[Peer] config as string
```

### `cid` must be registered in clients.json

The TURN server checks `clients.json` for the client ID. Without registration
the client cannot authenticate. Registration happens server-side via
`add_client.sh` (the bot calls it via sudo NOPASSWD):

```bash
/opt/vkturn/add_client.sh <client_id> <comment/tag>
```

### `peer` must be real external IP (never `127.0.0.1`)

Old code fell back to `127.0.0.1:9000` when `_detect_server_host()` failed.
Android parser requires non-empty `peer` — if it's localhost the client
connects to itself and fails silently. Fix: emit empty `peer` (parser rejects)
rather than localhost, so the failure is observable and debuggable.

### Example decoded payload

```json
{
  "v": 1, "provider": "vk", "peer": "203.0.113.50:56000",
  "transport": "tcp", "mode": "udp",
  "obf": "rtpopus", "key": "deadbeefcafe",
  "n": 15, "cid": "ABC-123-DEF", "name": "test-peer",
  "listen": "127.0.0.1:51900", "dnss": "1.1.1.1",
  "wg": "[Interface]\nPrivateKey = ...\nAddress = 192.168.102.5/24\nDNS = 1.1.1.1\n\n[Peer]\nPublicKey = ...\nPresharedKey = ...\nEndpoint = 127.0.0.1:51900\nAllowedIPs = 0.0.0.0/0\nPersistentKeepalive = 25\n"
}
```

## Build code (Python — `build_link_android`)

```python
def build_link_android(cid, obf_key_hex, server_host, server_port, profile, wg_conf, name=""):
    peer = f"{server_host}:{server_port}" if server_host and server_port else ""
    metadata = {
        "v": 1, "provider": "vk", "peer": peer,
        "transport": "tcp", "mode": "udp",
        "obf": profile, "key": obf_key_hex,
        "n": 15, "cid": cid, "listen": ANDROID_LOCAL_LISTEN,
        "dnss": "1.1.1.1",
    }
    if name:
        metadata["name"] = name
    if wg_conf:
        metadata["wg"] = wg_conf
    raw = json.dumps(metadata, separators=(",", ":"), sort_keys=True).encode("utf-8")
    b64 = base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")
    return f"freeturn://{b64}"
```

## WireGuard config for Android (`build_android_wg_conf`)

```python
# Endpoint is localhost:listen — freeturn CLI tunnels to the TURN proxy
ANDROID_LOCAL_LISTEN = "127.0.0.1:51900"

def build_android_wg_conf(peer):
    return (
        "[Interface]\n"
        f"PrivateKey = {peer['PRIV']}\n"
        f"Address = {peer['IP']}/24\n"
        "DNS = 1.1.1.1\n\n"
        "[Peer]\n"
        f"PublicKey = {peer['PUB']}\n"
        f"PresharedKey = {peer.get('PSK', '')}\n"
        f"Endpoint = {ANDROID_LOCAL_LISTEN}\n"
        "AllowedIPs = 0.0.0.0/0\n"
        "PersistentKeepalive = 25\n"
    )
```

## Related Android file (`add_client.sh`)

```bash
CLIENTS_DB="/etc/wireguard/clients.json"
# Registers: {cid: {"comment": tag}}
# revoke_peer.sh cleans up by matching comment == tag
```

## Pitfalls

- **DO NOT** use `base64.b64encode` (standard base64) — Android's `Base64.getUrlDecoder()` expects URL-safe base64.
- **Empty `peer`** when server IP detection fails — better visible failure than silent `127.0.0.1:9000` self-connection.
- **`cid` NEVER auto-registered** in the old code — Android clients would fail authentication silently. Must call `add_client.sh`.
