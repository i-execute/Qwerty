# Generated WebSocket helper: interpreter and cover-page pattern

## Problem signature

A generated relay crashes immediately with `ModuleNotFoundError` for a dependency such as `aiohttp`, even though the dependency is available to the userbot. The usual cause is spawning a bare `python3`, which resolves to a different interpreter than the userbot runtime.

## Implementation

1. Import `sys` in the module.
2. Launch the generated helper with:

```python
subprocess.Popen([sys.executable, script_path], cwd=user_dir, ...)
```

3. Validate the helper with the same interpreter:

```bash
"$USERBOT_PYTHON" -m py_compile generated_helper.py
```

4. For a WebSocket helper that also needs a minimal public page, keep the React JSX in a repository and reference the raw URL. The helper can expose `/gate.jsx`, fetch and return that source with `application/javascript`, and use a local fallback assignment to `window.App` if the fetch fails.
5. Serve `/` as a small HTML wrapper that loads React, ReactDOM, Babel, and `/gate.jsx`; keep the WebSocket route separate.

## Verification checklist

- `ast.parse()` succeeds for the module.
- The generated helper compiles with the userbot's `sys.executable`.
- The raw JSX URL returns HTTP 200 and JavaScript source.
- The helper has a local fallback when the remote JSX request fails.
- The WebSocket route still connects to the intended loopback backend and closes cleanly if it is unavailable.

## Safety

Do not put bot credentials, proxy credentials, or other secrets in the JSX or public HTML. Treat the cover page as public.
