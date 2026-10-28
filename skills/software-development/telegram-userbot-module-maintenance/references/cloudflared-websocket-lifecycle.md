# Cloudflared Quick Tunnel + generated WebSocket relay lifecycle

## Observed failure signature

A previously sent `*.trycloudflare.com` address displays Cloudflare **Error 1033** after the relay or userbot restarts.

## Cause

`cloudflared tunnel --url http://127.0.0.1:<port>` creates a **Quick Tunnel**. Its hostname is bound to that particular running cloudflared process. When it exits, Cloudflare unregisters the hostname; the next run receives a different name. The old hostname is expected to produce 1033 and cannot be made durable by configuration in the local module.

## Correct lifecycle

1. Start and health-check the local HTTP/WebSocket helper first.
2. Before launching cloudflared, truncate the user's `cloudflared.log` so hostname parsing cannot select an old URL.
3. Start `cloudflared tunnel --url http://127.0.0.1:<site_port> --no-autoupdate`.
4. Parse the first fresh `https://<name>.trycloudflare.com` line only after the new process is alive.
5. Store the hostname and regenerate/send the VLESS link after every restart. Do not show the former URL as current.
6. When a fixed public hostname is required, use an authenticated **named Tunnel** plus a Cloudflare DNS route; Quick Tunnels cannot satisfy that requirement.

## Relay landing page pitfall

Babel transpiles a remote `type="text/babel"` file, but an exported global `App` may still not mount. The wrapper must explicitly call:

```js
ReactDOM.createRoot(document.getElementById("root"))
  .render(React.createElement(window.App));
```

Keep a simple HTML fallback visible if scripts or the raw JSX asset fail.

## Minimal verification

- Compile module and generated helper with the userbot interpreter.
- GET helper `/` and `/gate.jsx` locally: both must return `200`.
- Run a local WebSocket echo backend, connect through the helper, send a text probe, and assert the echoed response.
- Start cloudflared and check its log for `Registered tunnel connection` and a newly issued URL. Confirm that the live URL—not a former one—returns the helper landing page.
