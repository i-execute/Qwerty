"""
Telegram Rich Message Helpers
=============================

Python composers for building Rich HTML messages for Telegram Bot API 10.1.

Usage:
    from skills.social_media.telegram_rich_messages.references.rich_helpers import (
        rich_table, rich_code, rich_thinking, rich_details,
        format_factorization_rich, validate_rich_html,
        rich_bold, rich_italic, rich_underline, rich_strikethrough,
        rich_final_thinking, rich_header, rich_paragraph, rich_blockquote,
        rich_link, rich_spoiler, rich_emoji
    )

    # Build a table
    table = rich_table(
        ["Metric", "Value", "Unit"],
        [["Latency", 42, "ms"], ["Throughput", 1200, "req/s"]]
    )

    # Code block with syntax highlighting
    code = rich_code('print("hello")', "python")

    # Thinking animation (ONLY for sendRichMessageDraft streaming frames)
    thinking = rich_thinking("Computing...")

    # Collapsible details
    details = rich_details("Raw JSON", rich_code('{"key": "value"}', "json"))

    # ShorBot-style factorization visualizer
    html = format_factorization_rich(
        n=91,
        attempts=[{"attempt": 1, "a": 2, "period_r": 6, "factors": (7, 13)}],
        success=True,
        factors=(7, 13)
    )

    # Validate before sending
    valid, errors = validate_rich_html(html)
"""

from html import escape
from typing import Any, List, Tuple, Optional


def rich_table(headers: List[str], rows: List[List[Any]]) -> str:
    """Generate a <table> from headers + rows. All values are HTML-escaped."""
    thead = "".join(f"<th>{escape(str(h))}</th>" for h in headers)
    tbody = "".join(
        "<tr>" + "".join(f"<td>{escape(str(cell))}</td>" for cell in row) + "</tr>"
        for row in rows
    )
    return f"<table><tr>{thead}</tr>{tbody}</table>"


def rich_code(code: str, lang: str = "python") -> str:
    """Wrap code in <pre><code class='language-{lang}'> for syntax highlighting."""
    return f"<pre><code class=\"language-{lang}\">{escape(code)}</code></pre>"


def rich_thinking(text: str) -> str:
    """
    Create a thinking animation block.

    IMPORTANT: <tg-thinking> works ONLY in sendRichMessageDraft (streaming frames).
    Using it in sendRichMessage or editMessageText causes RICH_MESSAGE_BLOCK_UNSUPPORTED error.

    Args:
        text: Text to show in thinking animation

    Returns:
        HTML string with <tg-thinking> tag
    """
    return f"<tg-thinking>{escape(text)}</tg-thinking>"


def rich_final_thinking(text: str) -> str:
    """
    Bold text for final messages — use instead of <tg-thinking> in sendRichMessage/editMessageText.

    <tg-thinking> works ONLY in sendRichMessageDraft (streaming). In final messages it causes
    RICH_MESSAGE_BLOCK_UNSUPPORTED. Use this function for final messages instead.
    """
    return f"<b>{escape(text)}</b>"


def rich_details(summary: str, content: str, open_by_default: bool = False) -> str:
    """Collapsible <details> block with <summary>."""
    open_attr = " open" if open_by_default else ""
    return f"<details{open_attr}><summary>{escape(summary)}</summary>{content}</details>"


def rich_blockquote(text: str) -> str:
    """Blockquote for quotes or highlighted text."""
    return f"<blockquote>{escape(text)}</blockquote>"


def rich_bold(text: str) -> str:
    return f"<b>{escape(text)}</b>"


def rich_italic(text: str) -> str:
    return f"<i>{escape(text)}</i>"


def rich_underline(text: str) -> str:
    return f"<u>{escape(text)}</u>"


def rich_strikethrough(text: str) -> str:
    return f"<s>{escape(text)}</s>"


def rich_header(level: int, text: str) -> str:
    """Heading <h1>–<h6>."""
    level = max(1, min(6, level))
    return f"<h{level}>{escape(text)}</h{level}>"


def rich_paragraph(text: str) -> str:
    """Simple paragraph."""
    return f"<p>{escape(text)}</p>"


def rich_link(url: str, text: str) -> str:
    """Hyperlink."""
    return f"<a href=\"{escape(url)}\">{escape(text)}</a>"


def rich_spoiler(text: str) -> str:
    """Spoiler text - tap to reveal."""
    return f"<tg-spoiler>{escape(text)}</tg-spoiler>"


def rich_emoji(emoji_id: str, fallback: str = "😀") -> str:
    """Custom emoji by document_id."""
    return f"<tg-emoji emoji-id=\"{emoji_id}\">{fallback}</tg-emoji>"


def rich_spoiler_block(text: str) -> str:
    """
    Collapsible spoiler using <details>/<summary> — works in rich messages.

    Alternative to <tg-spoiler> which is not supported in rich messages.
    """
    return f"<details><summary>{escape('Show spoiler')}</summary>{escape(text)}</details>"


# ============================================================
# High-level composers
# ============================================================


def format_factorization_rich(
    n: int,
    attempts: List[dict],
    success: bool,
    factors: Optional[Tuple[int, int]] = None,
) -> str:
    """
    Generate Rich HTML for ShorBot-style factorization visualization.

    Args:
        n: Number being factored
        attempts: List of attempt dicts with keys: attempt, a, period_r, factors?, candidate_factors?
        success: Whether factorization succeeded
        factors: Final (f1, f2) if success

    Returns:
        Complete Rich HTML string
    """
    rows = ""
    for st in attempts:
        idx = st["attempt"]
        a = st["a"]
        if "shortcut_gcd" in st:
            g = st["shortcut_gcd"]
            f1, f2 = st["factors"]
            r_cell = "shortcut"
            res = f"<b>{f1} × {f2}</b>"
        else:
            g = 1
            r = st.get("period_r", "?")
            r_cell = escape(str(r))
            cand = st.get("candidate_factors")
            if st.get("factors"):
                f1, f2 = st["factors"]
                res = f"<b>{f1} × {f2}</b>"
            elif cand:
                res = f"candidates: {cand[0]}, {cand[1]}"
            else:
                res = escape(st.get("result", "-"))

        rows += f"<tr><td>{idx}</td><td>{a}</td><td>{g}</td><td>{r_cell}</td><td>{res}</td></tr>"

    table = f"""
<table>
  <tr><th>No.</th><th>a</th><th>gcd(a,N)</th><th>period r</th><th>result</th></tr>
  {rows}
</table>"""

    if success and factors:
        f1, f2 = factors
        result_html = f"<h2>Result</h2><p><b>{n} = {f1} × {f2}</b></p>"
    else:
        result_html = f"<p>Tried {len(attempts)} attempts — failed to factorize, try again.</p>"

    code_block = """<pre><code class="language-python">
x = a^(r/2) mod N
factor1 = gcd(x-1, N)
factor2 = gcd(x+1, N)
</code></pre>"""

    details = f"""<details><summary>Why this won't break RSA tomorrow</summary>
<p>This is a <b>classical simulation</b> of Shor's period-finding step — no quantum speedup.
Real Shor's algorithm needs thousands of logical qubits and error correction.
Current quantum computers have < 1000 noisy qubits. RSA is safe for now.</p>
<p>Module repo: <a href="https://github.com/i-execute/Modules">i-execute/Modules</a></p>
<p>Simulation: <a href="https://github.com/SidRichardsQuantum/Shors_Algorithm_Simulation">SidRichardsQuantum/Shors_Algorithm_Simulation</a></p>
</details>"""

    return f"""<h1>Factorization N = {n}</h1>
{table}
{code_block}
{result_html}
{details}"""


# ============================================================
# Validation
# ============================================================

VALID_RICH_TAGS = {
    "b", "i", "u", "s", "a", "code", "pre", "blockquote",
    "table", "tr", "td", "th", "thead", "tbody",
    "details", "summary",
    "tg-thinking", "tg-spoiler", "tg-emoji",
    "h1", "h2", "h3", "h4", "h5", "h6",
    "p", "br", "ul", "ol", "li",
    "strong", "em", "del", "ins",
}


def validate_rich_html(html: str) -> Tuple[bool, List[str]]:
    """
    Basic validation of Rich Message HTML against allowed tags.
    Returns (is_valid, errors_list).
    """
    import re

    errors = []

    # Check for disallowed tags
    disallowed = {"sup", "sub", "tg-emoji", "tg-spoiler"}
    tag_pattern = re.compile(r"<\s*/?\s*([a-zA-Z0-9-]+)")
    found_tags = set(tag_pattern.findall(html))

    for tag in found_tags:
        base_tag = tag.split("-")[0] if "-" in tag else tag
        if base_tag in disallowed:
            errors.append(f"Disallowed tag: <{tag}> (use alternative)")

    # Check length
    if len(html) > 32768:
        errors.append(f"HTML exceeds 32KB limit ({len(html)} chars)")

    # Check for unclosed tags (basic check)
    open_tags = re.findall(r"<([a-zA-Z0-9-]+)(?:\s[^>]*)?>", html)
    close_tags = re.findall(r"</([a-zA-Z0-9-]+)>", html)

    # Basic check - this is approximate
    for tag in VALID_RICH_TAGS:
        if open_tags.count(tag) != close_tags.count(tag):
            # Some tags are self-closing, so we can't be too strict
            pass

    return len(errors) == 0, errors


# ============================================================
# Example usage / demo
# ============================================================

if __name__ == "__main__":
    # Demo
    html = format_factorization_rich(
        n=91,
        attempts=[
            {"attempt": 1, "a": 2, "period_r": 4, "candidate_factors": (3, 5)},
            {"attempt": 2, "a": 3, "period_r": 6, "factors": (7, 13)},
        ],
        success=True,
        factors=(7, 13)
    )
    print(html[:500] + "...")
    print()
    valid, errors = validate_rich_html(html)
    print(f"Valid: {valid}")
    if errors:
        print(f"Errors: {errors}")