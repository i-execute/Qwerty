#!/usr/bin/env python3
"""
Telegram Bot API 10.1/10.2 Rich Messages - Streaming Demo
=========================================================

Demonstrates sendRichMessageDraft for animated AI responses.

Requires:
    pip install aiohttp

Usage:
    python streaming_demo.py --token YOUR_BOT_TOKEN --chat 123456789
"""

import asyncio
import argparse
import json
import time
from typing import List, Dict
import aiohttp


# ============================================================
# Rich Message Builders (inline)
# ============================================================

def plain(text: str) -> Dict:
    return {"type": "plain", "text": text}

def bold(*content) -> Dict:
    return {"type": "bold", "text": list(content)}

def italic(*content) -> Dict:
    return {"type": "italic", "text": list(content)}

def code(text: str) -> Dict:
    return {"type": "code", "text": text}

def url(text: str, url: str) -> Dict:
    return {"type": "url", "text": [plain(text)], "url": url}

def math_inline(latex: str) -> Dict:
    return {"type": "math", "text": latex}

def paragraph(*content) -> Dict:
    return {"type": "paragraph", "content": list(content)}

def heading(level: int, *content) -> Dict:
    level = max(1, min(6, level))
    return {"type": "section_heading", "level": level, "content": list(content)}

def divider() -> Dict:
    return {"type": "divider"}

def preformatted(text: str, lang: str = "") -> Dict:
    return {"type": "preformatted", "content": [plain(text)], "language": lang}

def math_block(latex: str) -> Dict:
    return {"type": "math", "content": latex}

def table_cell(content, header=False, align="left") -> Dict:
    if isinstance(content, str):
        content = [plain(content)]
    return {"type": "table_cell", "content": content, "header": header, "align": align}

def table_row(*cells) -> Dict:
    return {"type": "table_row", "cells": list(cells)}

def table(rows, headers=None, caption="", bordered=True, striped=True) -> Dict:
    table_rows = []
    if headers:
        table_rows.append(table_row(*[table_cell(h, header=True, align="center") for h in headers]))
    for row in rows:
        table_rows.append(table_row(*[table_cell(c, align="left" if isinstance(c, str) else "center") for c in row]))
    result = {"type": "table", "rows": table_rows, "bordered": bordered, "striped": striped}
    if caption:
        result["caption"] = {"type": "caption", "content": [plain(caption)]}
    return result

def details(summary: str, *blocks, open=False) -> Dict:
    return {"type": "details", "summary": [plain(summary)], "content": list(blocks), "open": open}

def thinking(text: str = "Thinking...") -> Dict:
    return {"type": "thinking", "text": text}

def build_message(*blocks, media=None) -> Dict:
    msg = {"blocks": list(blocks)}
    if media:
        msg["media"] = media
    return msg


# ============================================================
# Demo Scenarios
# ============================================================

def demo_factorization_frames() -> List[Dict]:
    """ShorBot-style factorization streaming frames."""
    frames = []

    # Frame 1: Start
    frames.append(build_message(
        thinking("Initializing quantum simulation..."),
        heading(1, plain("Factorizing N = 91"))
    ))
    await_sleep(0.5)

    # Frame 2: Attempt 1
    frames.append(build_message(
        thinking("Attempt 1: a=2, finding period..."),
        heading(1, plain("Factorizing N = 91")),
        table(
            [["1", "2", "1", "6", "candidates: 3, 5"]],
            headers=["No.", "a", "gcd(a,N)", "period r", "result"],
            caption="Attempt 1: a=2, r=6 (candidates: 3, 5)"
        )
    ))
    await_sleep(0.5)

    # Frame 3: Attempt 2 - SUCCESS
    frames.append(build_message(
        thinking("Attempt 2: a=3, success!"),
        heading(1, plain("Factorizing N = 91")),
        table(
            [["1", "2", "1", "6", "candidates: 3, 5"], ["2", "3", "1", "6", "7 × 13"]],
            headers=["No.", "a", "gcd(a,N)", "period r", "result"],
            caption="Attempt 2: a=3, r=6 → FACTORS FOUND!"
        ),
        paragraph(bold(plain("Result: ")), plain("91 = "), bold(plain("7 × 13")))
    ))
    await_sleep(0.5)

    # Frame 4: Final (no thinking!)
    frames.append(build_message(
        heading(1, plain("Factorizing N = 91")),
        table(
            [["1", "2", "1", "6", "candidates: 3, 5"], ["2", "3", "1", "6", "7 × 13"]],
            headers=["No.", "a", "gcd(a,N)", "period r", "result"],
            caption="Complete: 91 = 7 × 13"
        ),
        paragraph(bold(plain("Result: ")), plain("91 = "), bold(plain("7 × 13"))),
        preformatted("x = a^(r/2) mod N\nfactor1 = gcd(x-1, N)\nfactor2 = gcd(x+1, N)", "python"),
        details(
            "Why this won't break RSA tomorrow",
            paragraph(plain("This is a classical simulation of Shor's period-finding step — no quantum speedup.")),
            paragraph(plain("Real Shor's algorithm needs thousands of logical qubits and error correction.")),
            paragraph(plain("Current quantum computers have < 1000 noisy qubits. RSA is safe for now."))
        )
    ))

    return frames


def demo_ai_response_frames(query: str) -> List[Dict]:
    """AI assistant streaming response."""
    frames = []

    # Frame 1: Thinking
    frames.append(build_message(
        thinking("Analyzing your question..."),
        heading(2, plain("AI Assistant"))
    ))
    await_sleep(0.3)

    # Frame 2: Partial answer
    frames.append(build_message(
        thinking("Generating response..."),
        heading(2, plain("AI Assistant")),
        paragraph(plain("You asked: "), bold(plain(query)))
    ))
    await_sleep(0.3)

    # Frame 3: Add code example
    frames.append(build_message(
        thinking("Generating response..."),
        heading(2, plain("AI Assistant")),
        paragraph(plain("You asked: "), bold(plain(query))),
        paragraph(plain("Here's a Python example:")),
        preformatted("def fibonacci(n):\n    a, b = 0, 1\n    for _ in range(n):\n        yield a\n        a, b = b, a + b\n\nprint(list(fibonacci(10)))", "python")
    ))
    await_sleep(0.3)

    # Frame 4: Add table
    frames.append(build_message(
        thinking("Formatting output..."),
        heading(2, plain("AI Assistant")),
        paragraph(plain("You asked: "), bold(plain(query))),
        paragraph(plain("Here's a Python example:")),
        preformatted("def fibonacci(n):\n    a, b = 0, 1\n    for _ in range(n):\n        yield a\n        a, b = b, a + b\n\nprint(list(fibonacci(10)))", "python"),
        paragraph(plain("First 10 Fibonacci numbers:")),
        table(
            [[str(i), str(fib(i))] for i in range(10)],
            headers=["n", "F(n)"],
            caption="Fibonacci Sequence"
        )
    ))
    await_sleep(0.3)

    # Frame 5: Complete (no thinking!)
    frames.append(build_message(
        heading(2, plain("AI Assistant")),
        paragraph(plain("You asked: "), bold(plain(query))),
        paragraph(plain("Here's a Python example:")),
        preformatted("def fibonacci(n):\n    a, b = 0, 1\n    for _ in range(n):\n        yield a\n        a, b = b, a + b\n\nprint(list(fibonacci(10)))", "python"),
        paragraph(plain("First 10 Fibonacci numbers:")),
        table(
            [[str(i), str(fib(i))] for i in range(10)],
            headers=["n", "F(n)"],
            caption="Fibonacci Sequence"
        ),
        details(
            "Math Note",
            paragraph(plain("The Fibonacci sequence is defined by F(n) = F(n-1) + F(n-2) with F(0)=0, F(1)=1.")),
            math_block("F(n) = \\frac{\\phi^n - (-\\phi)^{-n}}{\\sqrt{5}} \\quad \\text{where } \\phi = \\frac{1+\\sqrt{5}}{2}")
        ),
        paragraph(plain("— Generated via Telegram Rich Messages streaming"))
    ))

    return frames


def demo_business_report() -> Dict:
    """Complete business report (single message)."""
    return build_message(
        heading(1, bold(plain("Q3 2026 Financial Report"))),
        divider(),
        paragraph(
            plain("Revenue grew "),
            bold(plain("23%")),
            plain(" YoY to "),
            italic(plain("$4.2M"))
        ),
        table(
            [["$3.4M", "$4.2M", "+23%"], ["$1.2M", "$1.5M", "+25%"]],
            headers=["Q2", "Q3", "Change"],
            caption="Quarterly Revenue Comparison"
        ),
        table(
            [["Product A", "$2.1M", "+18%"], ["Product B", "$1.3M", "+32%"], ["Services", "$0.8M", "+20%"]],
            headers=["Segment", "Revenue", "Growth"],
            caption="Revenue by Segment"
        ),
        details(
            "Methodology & Assumptions",
            paragraph(plain("Data sourced from internal analytics platform (updated 2026-07-15).")),
            paragraph(plain("All figures in USD, unaudited. Growth rates calculated YoY.")),
            paragraph(plain("Projections based on current trajectory, subject to market conditions.")),
            open=False
        ),
        math_block("\\text{YoY Growth} = \\frac{R_{Q3,2026} - R_{Q3,2025}}{R_{Q3,2025}} \\times 100\\%"),
        footer(plain("Confidential — Internal Use Only — Generated by Hermes Agent"))
    )


def fib(n: int) -> int:
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a


async def await_sleep(seconds: float):
    await asyncio.sleep(seconds)


# ============================================================
# API Functions
# ============================================================

async def send_draft_frame(session: aiohttp.ClientSession, bot_token: str, chat_id: int, draft_id: int, frame: Dict):
    """Send a single draft frame."""
    url = f"https://api.telegram.org/bot{bot_token}/sendRichMessageDraft"
    payload = {
        "chat_id": chat_id,
        "draft_id": draft_id,
        "rich_message": frame
    }
    async with session.post(url, json=payload) as resp:
        result = await resp.json()
        if not result.get("ok"):
            print(f"⚠️ Draft frame failed: {result}")
        return result


async def send_final_message(session: aiohttp.ClientSession, bot_token: str, chat_id: int, message: Dict):
    """Send final rich message."""
    url = f"https://api.telegram.org/bot{bot_token}/sendRichMessage"
    payload = {
        "chat_id": chat_id,
        "rich_message": message
    }
    async with session.post(url, json=payload) as resp:
        result = await resp.json()
        if not result.get("ok"):
            print(f"❌ Final message failed: {result}")
        return result


async def stream_frames(bot_token: str, chat_id: int, frames: List[Dict], frame_delay: float = 0.5):
    """Stream a sequence of draft frames, then send final."""
    draft_id = int(time.time() * 1000)
    print(f"🚀 Starting stream (draft_id={draft_id}) with {len(frames)} frames")

    async with aiohttp.ClientSession() as session:
        for i, frame in enumerate(frames):
            print(f"  Frame {i+1}/{len(frames)}...", end=" ", flush=True)
            await send_draft_frame(session, bot_token, chat_id, draft_id, frame)
            print("✓")
            if i < len(frames) - 1:
                await asyncio.sleep(frame_delay)

        # Send final message (last frame without thinking)
        print("  Sending final message...", end=" ", flush=True)
        final_frame = frames[-1]
        # Remove thinking blocks from final
        final_blocks = [b for b in final_frame.get("blocks", []) if b.get("type") != "thinking"]
        final_message = {"blocks": final_blocks}
        await send_final_message(session, bot_token, chat_id, final_message)
        print("✓")

    print("✅ Stream complete!")


async def send_single_message(bot_token: str, chat_id: int, message: Dict):
    """Send a single rich message."""
    async with aiohttp.ClientSession() as session:
        await send_final_message(session, bot_token, chat_id, message)
        print("✅ Single message sent!")


# ============================================================
# Main
# ============================================================

async def main():
    parser = argparse.ArgumentParser(description="Telegram Rich Messages Streaming Demo")
    parser.add_argument("--token", required=True, help="Bot token")
    parser.add_argument("--chat", type=int, required=True, help="Chat ID")
    parser.add_argument("--demo", choices=["factorization", "ai", "report", "all"], default="all",
                        help="Which demo to run")
    parser.add_argument("--delay", type=float, default=0.5, help="Frame delay (seconds)")

    args = parser.parse_args()

    print(f"🎬 Telegram Rich Messages Streaming Demo")
    print(f"   Bot: {args.token[:10]}...")
    print(f"   Chat: {args.chat}")
    print(f"   Demo: {args.demo}")
    print()

    if args.demo in ("factorization", "all"):
        print("=" * 50)
        print("DEMO 1: ShorBot Factorization")
        print("=" * 50)
        frames = demo_factorization_frames()
        await stream_frames(args.token, args.chat, frames, args.delay)
        print()

    if args.demo in ("ai", "all"):
        print("=" * 50)
        print("DEMO 2: AI Assistant Response")
        print("=" * 50)
        frames = demo_ai_response_frames("How do I compute Fibonacci numbers efficiently?")
        await stream_frames(args.token, args.chat, frames, args.delay)
        print()

    if args.demo in ("report", "all"):
        print("=" * 50)
        print("DEMO 3: Business Report (Single Message)")
        print("=" * 50)
        msg = demo_business_report()
        await send_single_message(args.token, args.chat, msg)
        print()


if __name__ == "__main__":
    asyncio.run(main())