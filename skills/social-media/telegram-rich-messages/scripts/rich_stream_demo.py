#!/usr/bin/env python3
"""
Demo: Streaming Rich Message with sendRichMessageDraft
======================================================

Shows animated "thinking" frames like ShorBot does.
Run with: python3 rich_stream_demo.py <BOT_TOKEN> <CHAT_ID>
"""

import asyncio
import sys
import aiohttp


async def send_rich_draft(bot_token: str, chat_id: int, html: str, draft_id: int) -> dict:
    """Send a single Rich Message draft frame."""
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


def make_frame(attempt: int, n: int, thinking: str, table_rows: str = "") -> str:
    """Build a Rich HTML frame for the stream."""
    table = ""
    if table_rows:
        table = f"""
<table>
  <tr><th>No.</th><th>a</th><th>gcd(a,N)</th><th>period r</th><th>result</th></tr>
  {table_rows}
</table>"""
    
    return f"""
<h1>Factorization N = {n}</h1>
{make_thinking(thinking)}
{table}
"""


def make_thinking(text: str) -> str:
    from html import escape
    return f"<tg-thinking>{escape(text)}</tg-thinking>"


async def demo_factorization_stream(bot_token: str, chat_id: int, n: int = 91):
    """Simulate ShorBot-style factorization streaming."""
    import random
    import math
    
    def gcd(a, b):
        while b:
            a, b = b, a % b
        return a
    
    draft_id = int(asyncio.get_event_loop().time() * 1000)
    attempts = []
    max_tries = 5
    
    # Initial frame
    await send_rich_draft(bot_token, chat_id, f"""
<h1>Factorization N = {n}</h1>
<tg-thinking>Starting Shor's algorithm, trying base a...</tg-thinking>
""", draft_id)
    await asyncio.sleep(0.4)
    
    for attempt_idx in range(max_tries):
        a = random.randint(2, n - 1)
        g = gcd(a, n)
        
        if g != 1:
            f1, f2 = g, n // g
            thinking = f"Found factor via gcd shortcut: {f1} × {f2}"
            rows = f"<tr><td>{attempt_idx + 1}</td><td>{a}</td><td>{g}</td><td>shortcut</td><td><b>{f1} × {f2}</b></td></tr>"
            await send_rich_draft(bot_token, chat_id, f"""
<h1>Factorization N = {n}</h1>
{make_thinking(thinking)}
<table>
  <tr><th>No.</th><th>a</th><th>gcd(a,N)</th><th>period r</th><th>result</th></tr>
  {rows}
</table>
""", draft_id)
            await asyncio.sleep(0.5)
            
            # Final result
            final_html = f"""
<h1>Factorization N = {n}</h1>
<table>
  <tr><th>No.</th><th>a</th><th>gcd(a,N)</th><th>period r</th><th>result</th></tr>
  {rows}
</table>
<pre><code class="language-python">
x = a^(r/2) mod N
factor1 = gcd(x-1, N)
factor2 = gcd(x+1, N)
</code></pre>
<h2>Result</h2>
<p><b>{n} = {f1} × {f2}</b></p>
<details><summary>Why this won't break RSA tomorrow</summary>
<p>This is a <b>classical simulation</b> — no quantum speedup. Real Shor's algorithm needs thousands of logical qubits.</p>
<p>Module repo: <a href="https://github.com/i-execute/Modules">i-execute/Modules</a></p>
</details>
"""
            await send_rich_final(bot_token, chat_id, final_html)
            return
        
        # Simulate period finding
        r = None
        for r_candidate in range(1, min(n, 20)):
            if pow(a, r_candidate, n) == 1:
                r = r_candidate
                break
        
        if r and r % 2 == 0:
            x = pow(a, r // 2, n)
            if x != n - 1:
                f1 = gcd(x - 1, n)
                f2 = gcd(x + 1, n)
                if f1 not in (1, n) and n % f1 == 0:
                    thinking = f"Success! a={a}, r={r}, x={x} → factors {f1} × {f2}"
                    rows = f"<tr><td>{attempt_idx + 1}</td><td>{a}</td><td>1</td><td>{r}</td><td><b>{f1} × {f2}</b></td></tr>"
                    await send_rich_draft(bot_token, chat_id, f"""
<h1>Factorization N = {n}</h1>
{make_thinking(thinking)}
<table>
  <tr><th>No.</th><th>a</th><th>gcd(a,N)</th><th>period r</th><th>result</th></tr>
  {rows}
</table>
""", draft_id)
                    await asyncio.sleep(0.5)
                    
                    final_html = f"""
<h1>Factorization N = {n}</h1>
<table>
  <tr><th>No.</th><th>a</th><th>gcd(a,N)</th><th>period r</th><th>result</th></tr>
  {rows}
</table>
<pre><code class="language-python">
x = a^(r/2) mod N
factor1 = gcd(x-1, N)
factor2 = gcd(x+1, N)
</code></pre>
<h2>Result</h2>
<p><b>{n} = {f1} × {f2}</b></p>
<details><summary>Why this won't break RSA tomorrow</summary>
<p>This is a <b>classical simulation</b> — no quantum speedup. Real Shor's algorithm needs thousands of logical qubits.</p>
<p>Module repo: <a href="https://github.com/i-execute/Modules">i-execute/Modules</a></p>
</details>
"""
                    await send_rich_final(bot_token, chat_id, final_html)
                    return
        
        # Failed attempt - show thinking frame
        thinking_pool = [
            "Computing gcd(a, N)...",
            "Finding period r via classical simulation...",
            "Checking r parity...",
            "Computing x = a^(r/2) mod N...",
            "Checking candidates gcd(x±1, N)...",
            "Trying next base a...",
            "Checking if gcd is nontrivial...",
        ]
        thinking = f"Attempt {attempt_idx + 1}: a = {a} -- {thinking_pool[attempt_idx % len(thinking_pool)]}"
        rows = f"<tr><td>{attempt_idx + 1}</td><td>{a}</td><td>1</td><td>{r or '?'}</td><td>period not suitable</td></tr>"
        
        # Build cumulative table
        attempts.append(rows)
        table_rows = "".join(attempts)
        
        await send_rich_draft(bot_token, chat_id, f"""
<h1>Factorization N = {n}</h1>
{make_thinking(thinking)}
<table>
  <tr><th>No.</th><th>a</th><th>gcd(a,N)</th><th>period r</th><th>result</th></tr>
  {table_rows}
</table>
""", draft_id)
        await asyncio.sleep(0.35)
    
    # All attempts failed
    final_html = f"""
<h1>Factorization N = {n}</h1>
<table>
  <tr><th>No.</th><th>a</th><th>gcd(a,N)</th><th>period r</th><th>result</th></tr>
  {"".join(attempts)}
</table>
<p>Tried {max_tries} attempts — failed to factorize, try again.</p>
<details><summary>Why this won't break RSA tomorrow</summary>
<p>This is a <b>classical simulation</b> — no quantum speedup. Real Shor's algorithm needs thousands of logical qubits.</p>
<p>Module repo: <a href="https://github.com/i-execute/Modules">i-execute/Modules</a></p>
</details>
"""
    await send_rich_final(bot_token, chat_id, final_html)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 rich_stream_demo.py <BOT_TOKEN> <CHAT_ID> [N]")
        sys.exit(1)
    
    bot_token = sys.argv[1]
    chat_id = int(sys.argv[2])
    n = int(sys.argv[3]) if len(sys.argv) > 3 else 91
    
    asyncio.run(demo_factorization_stream(bot_token, chat_id, n))