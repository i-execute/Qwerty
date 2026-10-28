# Downloader external-path validation

Use when repairing a Telegram userbot module that wraps yt-dlp or uploads previews.

## Verify the supplied media URL

Run the installed/current yt-dlp against the exact URL in metadata-only mode before delivery. Confirm non-empty ID, title, duration, and available formats. This grounds the repair in the real extractor path rather than an inferred code change.

Do not unconditionally set yt-dlp `impersonate`: first ensure a compatible impersonation target is installed and listed. An unavailable target makes yt-dlp fail before extraction.

## x0.at preview uploads

Use multipart form upload to `https://x0.at/` with a trailing slash. The bare `https://x0.at` endpoint can return HTTP 405. Treat success as an HTTP 200/201 response whose first non-empty response line begins with `https://x0.at/`; then make a lightweight GET/range probe of the returned URL.

## Delivery

Run `py_compile`, validate all referenced localization keys against every locale dictionary, and exercise the x0 upload helper directly with a small harmless fixture. When asked for a file without commentary, send only the verified artifact.