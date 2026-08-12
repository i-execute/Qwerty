---
name: telegram-userbot-module-maintenance
description: Repair and validate Python Telegram userbot modules that use inline UI, external APIs, and persistent state.
version: 1.0.0
author: Hermes Agent
created_by: agent
---

# Telegram Userbot Module Maintenance

## Use when

A user supplies or asks to repair a Python module for a Telegram userbot framework (for example Hikka/Telethon style modules) with inline callbacks, localized `strings`, database state, or external HTTP API integration.

## Core workflow

1. **Inspect before editing.** Compile the source and enumerate every `self.strings["..."]` lookup against both `strings` and `strings_ru`.
2. **Create a tight regression harness first.** Prefer AST extraction for pure helpers and static checks for localization keys, config constants, and handler call signatures. Run it red before the implementation.
3. **Preserve framework contracts.** Keep callback signatures, `InlineCall` behavior, storage APIs, and command decorators compatible with the supplied module framework.
4. **Normalize user-entered external identifiers.** Accept the form users naturally paste (for GitHub repositories, `https://github.com/owner/repository`) and store the canonical form needed by the API (`owner/repository`). Reject ambiguous or malformed input with a localized UI error.
5. **Make HTTP failures actionable.** API wrappers should return structured success plus a compact, safe diagnostic containing HTTP status and a bounded response body. Do not expose tokens or raw authorization headers.
6. **Specify the target explicitly.** For GitHub Contents API writes, pass the intended file path and branch explicitly; use the file SHA returned from the read request, and handle an empty/missing JSON database as `{}` only when that is the desired schema.
7. **Instrument parsers with bounded diagnostics.** For long-running inline actions, edit the existing `InlineCall` no more often than about once per 1.5 seconds. Show batches/API calls, scanned items, unique accepted IDs, skipped/no-sender count, current rate, elapsed time, last cursor/message ID, and ETA only when a server-provided total makes it meaningful. Return a contextual error containing those counters on failure. Do not add bulk collection behavior beyond the user's supplied scope.
8. **Treat failed mutations as failed.** After every `patch`/write, verify that the target file actually changed before reporting progress. If a patch fails validation, re-read the exact region, apply a narrower replacement, and explicitly keep working rather than claiming a completed fix.
9. **Validate before delivery.** Run `py_compile`, AST/string-key validation, and targeted tests. Copy the final module to a stable deliverable path and report real verification output.
10. **Launch helpers with the userbot interpreter.** When the module writes then runs a Python helper (HTTP server, WebSocket relay, etc.), use `[sys.executable, script_path]`, not a bare `python`/`python3`. The bot may run inside a venv whose dependencies differ from the system interpreter. Compile the generated helper with that same interpreter before delivery.
11. **Separate WebSocket relay logic from its cover page.** Keep a deployable JSX fallback/landing page in a versioned repository and reference its `raw.githubusercontent.com` URL. Serve it through a local route (for example `/gate.jsx`) behind a minimal React/Babel wrapper. Include a small local JS fallback so a remote UI-asset outage does not prevent the WebSocket relay from functioning.
12. **WebSocket client counts must account for relay topology.** If public clients terminate at an aiohttp mask-site relay and Xray sees only `127.0.0.1`, inspect the **mask-site listener port**, not Xray's backend port. Parse `ss -Htn state established sport = :<site_port>`, count distinct non-loopback peer sockets, and exclude the single localhost relay→Xray hop. Retain public-IP deduplication for direct TCP/Reality users. Persist `site_port`, pass it into both the status UI and device-limit monitor, and test parsing with fixture output containing public peers, duplicate peers, and a localhost backend connection.
13. **Cover assets and fallback page are independent deployables.** Store the static connection/loading page in its own versioned HTML file and fetch it in the generated helper; keep the React/JSX cover in a separate file. The static page must render correctly with no CDN scripts (it is the fallback), use a restrained monochrome dark palette when requested, and never include obsolete decorative elements. Version raw URLs with a query suffix when clients/helpers may cache them.
14. **Lottie/audio interaction contract.** Put Lottie JSON and audio in stable repository paths with names matching the current cover identity; remove obsolete asset references rather than merely leaving them unused. Render a deliberately sized Lottie container rather than inheriting full-page dimensions. Browsers block unsolicited audio: attempt playback on the first page `pointerdown`/`keydown`; a dedicated sound control must toggle it, and once the user explicitly turns it off, later page clicks must not re-enable it. Do not promise autoplay before a user gesture.
15. **Status labels with constrained renderers.** When a Telegram renderer only supports one token in a highlighted/status field, make the entire `user_started`/`user_stopped` value a single word in every locale and keep the same exact constrained words in any code-language/log header markup.
13. **VLESS fallbacks and encryption are mutually constrained by Xray.** Xray rejects `settings.decryption` together with VLESS `fallbacks`. A WebSocket cover site that requires a fallback must use legacy VLESS `encryption=none` with outer Cloudflare TLS; ML-KEM-768 VLESS encryption belongs on new TCP/XHTTP users without fallback/`xtls-rprx-vision`. Validate each generated transport separately with the exact Xray binary using `xray run -test -config`.
14. **Ephemeral WebSocket tunnel lifecycle.** A Quick Tunnel hostname is process-scoped. On restart, stop stale helper/tunnel processes, rebuild the helper before regenerating Xray so its fallback port matches, clear the tunnel log before startup, parse only the fresh hostname, persist it after successful registration, and send a deterministic `link_for_<user>.txt` to the configured log topic. Delete the temporary file after upload.
15. **Cover-asset versioning.** Keep JSX, Lottie JSON, and optional audio under stable repository paths; use raw URLs in generated helpers and verify each URL returns HTTP 200. A JSX source must explicitly mount `window.App` after Babel loads it; autoplay audio must be opt-in behind a user gesture.
12. **Render external JSX explicitly.** A `<script type="text/babel" src="/gate.jsx">` transpiles source but does not reliably mount a global `App`; after loading it, explicitly run `ReactDOM.createRoot(document.getElementById("root")).render(React.createElement(window.App))`. Use a non-JSX static fallback page for browser/CDN failures.
13. **Treat Quick Tunnels as ephemeral.** Every `cloudflared tunnel --url ...` Quick Tunnel gets a new `trycloudflare.com` hostname on process restart; old hosts correctly return Cloudflare 1033. Truncate the per-user tunnel log before startup, parse only the fresh hostname, persist it only after successful connection registration, and never claim URL stability. For a stable hostname, the user must configure a named Cloudflare Tunnel and DNS separately.
14. **Verify helper readiness and relay behavior, not just compilation.** Before exposing a tunnel, wait for the generated helper to listen on loopback. Test its `/` and JSX routes, then run a local WebSocket echo backend through the generated relay. Give both WebSocket sides a heartbeat and close clients cleanly if the backend is unavailable.
15. **VLESS encryption semantics.** VLESS `encryption=none` is protocol-correct for legacy configurations; transport confidentiality comes from TLS (for Cloudflare WebSocket) or Reality (TCP/XHTTP). Preserve legacy records via `.get(..., "none")` so existing users are untouched.
16. **ML-KEM-768 VLESS encryption for new users.** On Xray builds that expose `xray vlessenc`, generate the paired values rather than inventing an encryption string: select the post-quantum ML-KEM-768 pair from its output. Put `decryption` only in inbound `settings`; put its matching `encryption` only in the generated VLESS URI. Xray rejects an `encryption` key under `settings.clients[]`. ML-KEM VLESS encryption must not be mixed with `xtls-rprx-vision`: omit Vision for newly generated encrypted TCP/Reality links, while retaining it for legacy users. Test the full generated JSON with the exact installed binary: `xray run -test -config <path>`.

See `references/generated-websocket-helper.md` and `references/cloudflared-websocket-lifecycle.md` for implementation and verification patterns.

## GitHub Contents API checklist

- Canonical repository identifier: `owner/repository`.
- Contents URL shape: `/repos/{owner}/{repo}/contents/{path}`.
- Read the intended ref explicitly, e.g. `?ref=main`.
- Update body contains `message`, Base64 `content`, `branch`, and existing-file `sha` when supplied.
- Successful writes return HTTP 200 or 201.
- A concurrent update can return conflict/validation failure: show the bounded API diagnostic and retry only after a fresh read if the user requested automatic conflict retry.
- Never log or render the API token.

## Localization invariant

Every literal key accessed as `self.strings["key"]` must exist in every supported locale dictionary. Add a static AST test to catch omissions; missing keys cause runtime `unknown strings` failures in callbacks that are otherwise valid.

## yt-dlp / browser-protected media sources

When a userbot module wraps yt-dlp, test the exact URL with the **same Python interpreter and venv as the running userbot**, not only with a system CLI or a separate `uvx` environment. Different runtime dependencies and network handlers can produce materially different results.

1. Print the runtime `yt_dlp.version.__version__`, `yt_dlp.__file__`, and `sys.executable`.
2. Reproduce metadata extraction with the module's actual `YoutubeDL` options.
3. For sites that reject the default Python HTTP transport (for example a 410/anti-bot response), use yt-dlp browser impersonation through `curl_cffi`.
4. Pin a yt-dlp-compatible dependency range in the module installer: `curl_cffi>=0.10,<0.16`. Do not assume the newest curl_cffi release is compatible with the installed yt-dlp.
5. In yt-dlp's **Python API**, pass a typed `ImpersonateTarget`, not the string form accepted by the CLI. Select an entry exposed by `CurlCFFIRH.supported_targets` and include all fields required by that target (client, version, OS, OS version).
6. Apply the same transport/impersonation options to both metadata extraction and every actual download path.
7. Make dependency installation fail loudly (`subprocess.run(..., check=True)`) and expose the installed dependency state in the module's diagnostic command.
8. If a regional media URL is unstable, normalize it to a canonical host for the download path, but keep a bounded original/canonical retry list for extraction.

See `references/yt-dlp-runtime-impersonation.md` for the compact reproduction and verification sequence.

## Delivery standard

Do not claim a module is fixed until a real file has been written and checked. When a patch fails, say the file is unchanged and continue with a narrower edit; never describe an unapplied patch as a completed fix.
