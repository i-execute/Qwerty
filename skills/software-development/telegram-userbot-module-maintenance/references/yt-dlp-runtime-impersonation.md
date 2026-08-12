# yt-dlp runtime impersonation probe

Use when a URL succeeds in an external yt-dlp CLI but fails from a loaded userbot module.

## Reproduce in the actual runtime

```bash
PY=/path/to/userbot/venv/bin/python
$PY - <<'PY'
import sys, yt_dlp
print(yt_dlp.version.__version__)
print(yt_dlp.__file__)
print(sys.executable)
opts = {"quiet": True, "no_warnings": True, "skip_download": True}
with yt_dlp.YoutubeDL(opts) as ydl:
    print(ydl.extract_info("URL", download=False)["id"])
PY
```

## Browser-protected endpoint recipe

1. Ensure yt-dlp is current.
2. Install a version yt-dlp supports, not blindly the latest curl_cffi:

```bash
python -m pip install -U yt-dlp 'curl_cffi>=0.10,<0.16'
```

3. Discover an available target:

```bash
python -m yt_dlp --list-impersonate-targets
```

4. For the Python API, construct the target object with all fields from the listing. Example:

```python
from yt_dlp.networking.impersonate import ImpersonateTarget

opts = {
    "quiet": True,
    "no_warnings": True,
    "socket_timeout": 30,
    "skip_download": True,
    "impersonate": ImpersonateTarget(
        client="chrome", version="136", os="macos", os_version="15"
    ),
}
```

The CLI accepts `--impersonate chrome-136`; directly passing that string in `YoutubeDL(opts)` may fail because the Python API expects `ImpersonateTarget`.

## Validation

Run the module's metadata options under the live venv and require a real ID/title/duration. Repeat with the download options (or a controlled small-format download) before delivery.
