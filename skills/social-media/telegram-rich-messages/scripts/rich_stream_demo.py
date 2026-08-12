#!/usr/bin/env python3
"""
Demo: Streaming Rich Message with sendRichMessageDraft
======================================================

Shows animated "thinking" frames like ShorBot does.
Run with: python3 scripts/rich_stream_demo.py <BOT_TOKEN> <CHAT_ID> [N]

This script demonstrates the CORRECT pattern:
- sendRichMessageDraft for streaming frames WITH <tg-thinking>
- sendRichMessage for final message WITHOUT <tg-thinking>

Key insight from ShorBot: <tg-thinking> works ONLY in sendRichMessageDraft frames,
not in the final sendRichMessage. Final message should be clean result.
"""

import asyncio
import sys
import time
import random
import aiohttp


async def send_rich_draft(bot_token: str, chat_id: int, html: str, draft_id: int) -> dict:
    """Send a single Rich Message draft frame (streaming)."""
    url = f"https://api.telegram.org/bot{bot_token}/sendRichMessageDraft"
    payload = {
        "chat_id": chat_id,
        "draft_id": draft_id,
        "rich_message": {"html": html},
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload) as resp:
            return await resp.json()


async def send_rich_final(bot_token: str, chat_id: int, html: str) -> dict:
    """Send the final Rich Message."""
    url = f"https://api.telegram.org/bot{bot_token}/sendRichMessage"
    payload = {
        "chat_id": chat_id,
        "rich_message": {"html": html},
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload) as resp:
            return await resp.json()


def esc(t: str) -> str:
    """HTML escape."""
    return str(t).replace("&", "&").replace("<", "<").replace(">", ">")


def make_frame(n: int, thinking: str, rows: str = "") -> str:
    """Build a streaming frame with thinking + table."""
    table = ""
    if rows:
        table = f"""
<table>
  <tr><th>No.</th><th>a</th><th>gcd(a,N)</th><th>period r</th><th>result</th></tr>
  {rows}
</table>"""
    return f"""
<h1>Factorization N = {n}</h1>
<tg-thinking>{esc(thinking)}</tg-thinking>
{table}
"""


async def stream_factorization(bot_token: str, chat_id: int, n: int = 91):
    """Simulate ShorBot-style factorization with animated thinking."""
    draft_id = int(time.time() * 1000)
    base_url = f"https://api.telegram.org/bot{bot_token}"
    draft_url = f"{base_url}/sendRichMessageDraft"
    final_url = f"{base_url}/sendRichMessage"

    def gcd(a: int, b: int) -> int:
        while b:
            a, b = b, a % b
        return a

    def find_period(a: int, n: int, max_r: int = 50) -> int | None:
        for r in range(1, min(max_r, n)):
            if pow(a, r, n) == 1:
                return r
        return None

    THINKING_POOL = [
        "Computing gcd(a, N)...",
        "Finding period r via classical simulation...",
        "Checking r parity...",
        "Computing x = a^(r/2) mod N...",
        "Checking candidates gcd(x±1, N)...",
        "Analyzing factor candidates...",
        "Trying next base a...",
        "Checking if gcd is nontrivial...",
    ]

    async with aiohttp.ClientSession() as session:
        attempts = []
        max_tries = 10

        # Initial frame
        await session.post(draft_url, json={
            "chat_id": chat_id,
            "draft_id": draft_id,
            "rich_message": {"html": f"""
<h1>Factorization N = {n}</h1>
<tg-thinking>Starting Shor's algorithm...</tg-thinking>
"""}
        })
        await asyncio.sleep(0.5)

        for i in range(max_tries):
            a = random.randint(2, n - 1)
            g = gcd(a, n)

            if g != 1:
                f1, f2 = g, n // g
                thinking = f"Attempt {i+1}: a = {a} -- gcd shortcut! {f1} × {f2}"
                row = f"<tr><td>1</td><td>{a}</td><td>{g}</td><td>shortcut</td><td><b>{f1} × {f2}</b></td></tr>"

                await session.post(draft_url, json={
                    "chat_id": chat_id,
                    "draft_id": draft_id,
                    "rich_message": {"html": f"""
<h1>Factorization N = {n}</h1>
<tg-thinking>{esc(thinking)}</tg-thinking>
<table>
  <tr><th>No.</th><th>a</th><th>gcd(a,N)</th><th>period r</th><th>result</th></tr>
  {row}
</table>
"""}
                })
                await asyncio.sleep(0.8)

                # Final result
                final = f"""
<h1>Factorization N = {n}</h1>
<table><tr><th>No.</th><th>a</th><th>gcd(a,N)</th><th>period r</th><th>result</th></tr>{row}</table>
<h2>Result</h2><p><b>{n} = {f1} × {f2}</b></p>
<details><summary>Why this won't break RSA tomorrow</summary>
<p>This is a <b>classical simulation</b> — no quantum speedup. Real Shor's algorithm needs thousands of logical qubits.</p>
<p>Module repo: <a href="https://github.com/i-execute/Modules">i-execute/Modules</a></p>
</details>"""
                await session.post(final_url, json={
                    "chat_id": chat_id,
                    "rich_message": {"html": final}
                })
                return

            # Find period
            r = find_period(a, n)

            if r and r % 2 == 0:
                x = pow(a, r // 2, n)
                if x != n - 1:
                    f1 = gcd(x - 1, n)
                    f2 = gcd(x + 1, n)
                    if f1 not in (1, n):
                        thinking = f"Attempt {i+1}: a = {a} -- SUCCESS! {f1} × {f2}"
                        row = f"<tr><td>1</td><td>{a}</td><td>1</td><td>{r}</td><td><b>{f1} × {f2}</b></td></tr>"

                        await session.post(draft_url, json={
                            "chat_id": chat_id,
                            "draft_id": draft_id,
                            "rich_message": {"html": f"""
<h1>Factorization N = {n}</h1>
<tg-thinking>{esc(thinking)}</tg-thinking>
<table>
  <tr><th>No.</th><th>a</th><th>gcd(a,N)</th><th>period r</th><th>result</th></tr>
  {row}
</table>
"""}
                        })
                        await asyncio.sleep(0.8)

                        final = f"""
<h1>Factorization N = {n}</h1>
<table><tr><th>No.</th><th>a</th><th>gcd(a,N)</th><th>period r</th><th>result</th></tr>{row}</table>
<h2>Result</h2><p><b>{n} = {f1} × {f2}</b></p>
<pre><code class="language-python">x = a^(r/2) mod N
factor1 = gcd(x-1, N)
factor2 = gcd(x+1, N)</code></pre>
<details><summary>Why this won't break RSA tomorrow</summary>
<p>This is a <b>classical simulation</b> — no quantum speedup. Real Shor's algorithm needs thousands of logical qubits.</p>
<p>Module repo: <a href="https://github.com/i-execute/Modules">i-execute/Modules</a></p>
</details>"""
                        await session.post(final_url, json={
                            "chat_id": chat_id,
                            "rich_message": {"html": final}
                        })
                        return

            # Failed attempt
            thinking = f"Attempt {i+1}: a = {a} -- {THINKING_POOL[i % len(THINKING_POOL)]}"
            row = f"<tr><td>{i+1}</td><td>{a}</td><td>1</td><td>{r or '?'}</td><td>period not suitable</td></tr>"

            await session.post(draft_url, json={
                "chat_id": chat_id,
                "draft_id": draft_id,
                "rich_message": {"html": make_frame(n, thinking, row)}
            })
            await asyncio.sleep(0.4)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 scripts/rich_stream_demo.py <BOT_TOKEN> <CHAT_ID> [N]")
        sys.exit(1)

    bot_token = sys.argv[1]
    chat_id = int(sys.argv[2])
    n = int(sys.argv[3]) if len(sys.argv) > 3 else 91

    asyncio.run(stream_factorization(bot_token, chat_id, n))