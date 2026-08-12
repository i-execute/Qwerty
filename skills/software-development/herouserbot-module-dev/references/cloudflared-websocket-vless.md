# Cloudflared WebSocket VLESS Pattern

## Scope

Use this pattern only when a Heroku XRay module must expose a WebSocket VLESS inbound through a Cloudflare Tunnel and also serve a harmless decoy page.

## Architecture

A plain static HTTP server cannot simultaneously serve the decoy page and forward WebSocket upgrades to Xray. Use a local reverse proxy service with two routes:

- `/` serves the decoy page.
- A randomized WebSocket path proxies WebSocket binary and text frames, ping/pong, and closure bidirectionally to the local Xray WS listener.

`cloudflared tunnel --url http://127.0.0.1:<proxy-port> --no-autoupdate` exposes that local proxy. The client link must use:

- `address`: generated `*.trycloudflare.com` hostname
- `port`: `443`
- `security`: `tls`
- `sni` and `host`: generated hostname
- `type`: `ws`
- `path`: the proxy and Xray path
- `encryption`: `none` unless both server and client are explicitly configured for a tested VLESS encryption suite

The Xray WS inbound remains on localhost. Its VLESS fallback can point to the proxy's local port for ordinary HTTP requests only if that does not create a loop. Do not make the proxy route WebSocket back to an Xray listener that itself falls back to the same proxy unless the VLESS handshake path is isolated correctly.

## Setup behavior

- Store cloudflared in the module-owned user directory, e.g. `~/.xray_on_userbot/<id>/cloudflared`.
- Download the architecture-specific official release, set mode `0755`, and run `cloudflared --version` before reporting success.
- Add Install/Reinstall Cloudflared controls to Setup and run the exact installed binary instead of relying on PATH.
- Parse only `https://<name>.trycloudflare.com` from the tunnel log before generating the VLESS link.

## Lifecycle

For each WebSocket user:

1. Allocate a loopback port for Xray and another one for the proxy.
2. Generate and persist a random path, proxy port, and tunnel hostname.
3. Start the local proxy and Xray in an order that avoids a reverse-proxy loop.
4. Start cloudflared and wait for its hostname.
5. Generate the VLESS link only after the hostname is available.
6. On stop, delete, module unload, and failed startup, terminate tunnel, proxy, and Xray process groups.
7. On reload, re-establish proxy and tunnel for every reattached WebSocket Xray user.

## Verification

Required checks before delivery:

1. Local E2E: a disposable Xray client reaches `https://www.gstatic.com/generate_204` through the local WS proxy and returns HTTP 204.
2. Tunnel health: the quick-tunnel process log contains the generated hostname and remains running.
3. External E2E: a disposable client connects through the generated `trycloudflare.com:443` WSS endpoint and returns HTTP 204.
4. Decoy check: `GET /` through the tunnel returns the animation page, while the WS path upgrades successfully.

Do not claim Cloudflare Tunnel support is working if only the local WS E2E passed. Quick Tunnels are temporary and their hostname changes whenever the process is recreated; named tunnels require user-owned Cloudflare credentials and a DNS route.

## Forum logging

For Heroku module audit logs, fetch the asset forum channel from `heroku.forums/channel_id`, create or reuse the topic via `utils.asset_forum_topic`, and use the requested topic icon. Send logs through `self.inline.bot.send_message` with `parse_mode="HTML"` and `message_thread_id=topic.id`; do not send audit logs through the user client. Log starts, stops, deletion, and limit enforcement. Persist `autostart=False` before stopping a user that exceeds its device limit, then record the configured limit and observed count.

## Xray detail

Xray's current WebSocket documentation marks WS as deprecated in favor of XHTTP. It is still usable where required, but the module should present it as `WebSocket`, not a misleading RAW/REALITY transport. RAW is the UI label for the existing `network: tcp` plus REALITY/Vision implementation.
