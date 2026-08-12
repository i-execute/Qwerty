# freeturn:// URI Spec

Source: `github.com/samosvalishe/free-turn-proxy/blob/master/docs/uri.md`
Android parser: `github.com/samosvalishe/turn-proxy-android/blob/main/app/src/main/java/com/freeturn/app/data/share/FreeturnLink.kt`

## Format

```
freeturn://<base64url(json)>
```

Payload is a JSON object encoded with `base64.urlsafe_b64encode` (no padding, equivalent to Go `base64.RawURLEncoding`). Versioned by `v` field — old parsers reject unknown versions, new fields don't break parsing.

## JSON Fields

| Key | CLI Flag | Type | Description |
|-----|---------|------|-------------|
| `v` | — | int | Version (currently `1`). Required. |
| `provider` | `-provider` | string | TURN-cred source (e.g. `vk`). Required, non-empty. |
| `peer` | `-peer` | string | Server address `ip:port`. Required, non-empty. |
| `transport` | `-transport` | string | `tcp` or `udp` (transport to TURN relay). |
| `mode` | `-mode` | string | Tunnel mode: `udp` or `tcp`. |
| `bond` | `-bond` | bool | Bonding TCP (`true`), only with `mode=tcp`. |
| `obf` | `-obf-profile` | string | Obfuscation profile (`rtpopus`, `rtpopus2`, `rtpopus3`). `none` omitted. |
| `key` | `-obf-key` | string | Obfuscation key (hex). Only with `obf` set. |
| `n` | `-n` | int | Number of TURN streams. |
| `spc` | `-streams-per-cred` | int | Streams per VK credential cache. |
| `cid` | `-client-id` | string | Client ID. Must be registered in `clients.json` allowlist by owner. |
| `listen` | `-listen` | string | Local `ip:port` for WireGuard/Xray (e.g. `127.0.0.1:51900`). |
| `dns` | `-dns-mode` | string | Client resolver: `plain`, `doh`, or `auto`. |
| `dnss` | `-dns-servers` | string | Custom DNS servers, comma-separated. |
| `mcap` | `-manual-captcha` | bool | Manual VK captcha (`true`). |
| `name` | — | string | Client name / comment. |
| `wg` | — | string | Full WireGuard config text (Android app imports atomically). |
| `mtu` | — | int | WireGuard MTU (default from `ClientConfig.DEFAULT_WG_MTU`). |

## Android Parser Requirements (FreeturnLink.kt)

The Android parser validates:
1. `v == 1` — rejects other versions
2. `provider` non-empty — rejects missing provider
3. `peer` non-empty — rejects missing peer

If `peer` is empty, the parse will fail with "missing peer". This is CORRECT behavior — it means the server is misconfigured. Never fall back to `127.0.0.1:9000`.

## What's NOT in the Link

- **`-link` (VK call URL)**: NEVER embedded. It's client-unique. Must be provided separately as `-link "https://vk.ru/call/join/..."` on CLI or in the Android share screen.

## Example (decoded)

```json
{
  "v": 1,
  "provider": "vk",
  "peer": "203.0.113.50:56000",
  "transport": "tcp",
  "mode": "udp",
  "obf": "rtpopus",
  "key": "d823fa...",
  "n": 15,
  "cid": "A1B2C3...",
  "listen": "127.0.0.1:51900",
  "dnss": "1.1.1.1",
  "name": "RU-Server",
  "wg": "[Interface]\nPrivateKey = ...\nAddress = 192.168.102.5/24\n..."
}
```

## Python Builder Pattern

```python
import json, base64

metadata = {
    "v": 1,
    "provider": "vk",
    "peer": f"{server_host}:{server_port}",
    "transport": "tcp",
    "mode": "udp",
    "obf": profile,
    "key": obf_key_hex,
    "n": 15,
    "cid": cid,
    "listen": "127.0.0.1:51900",
    "dnss": "1.1.1.1",
}
if name:
    metadata["name"] = name
if wg_conf:
    metadata["wg"] = wg_conf

raw = json.dumps(metadata, separators=(",", ":"), sort_keys=True).encode("utf-8")
b64 = base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")
link = f"freeturn://{b64}"
```

## clients.json Allowlist

The `cid` field must be registered in `/etc/wireguard/clients.json` before the Android client connects:

```json
{
  "A1B2C3-DEF": {"comment": "user-tag"}
}
```

`add_client.sh <cid> <comment>` handles this. `revoke_peer.sh` cleans up by matching `comment == tag`.

## WireGuard Config for Android

The WG config uses `Endpoint = 127.0.0.1:51900` (the freeturn local listener), NOT the external server. The freeturn client listens on localhost and tunnels traffic through the TURN proxy to the WireGuard server.

```
[Interface]
PrivateKey = <peer-private-key>
Address = 192.168.102.X/24
DNS = 1.1.1.1

[Peer]
PublicKey = <server-public-key>
PresharedKey = <psk>
Endpoint = 127.0.0.1:51900
AllowedIPs = 0.0.0.0/0
PersistentKeepalive = 25
```
