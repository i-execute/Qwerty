"""
Telegram Rich Message helpers — drop-in utilities for composing Rich HTML.

Save as: skills/social-media/telegram-rich-messages/references/rich_helpers.py
"""

from html import escape
from typing import Any


def rich_table(headers: list[str], rows: list[list[Any]]) -> str:
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
    """Thinking animation block — shows animated spinner in Telegram."""
    return f"<tg-thinking>{escape(text)}</tg-thinking>"


def rich_details(summary: str, content: str, open_by_default: bool = False) -> str:
    """Collapsible <details> block with <summary>."""
    open_attr = " open" if open_by_default else ""
    return f"<details{open_attr}><summary>{escape(summary)}</summary>{content}</details>"


def rich_blockquote(text: str) -> str:
    """Blockquote for quotes or highlighted text."""
    return f"<blockquote>{escape(text)}</blockquote>"


def rich_header(level: int, text: str) -> str:
    """Heading <h1>–<h6>."""
    level = max(1, min(6, level))
    return f"<h{level}>{escape(text)}</h{level}>"


def rich_paragraph(text: str) -> str:
    """Simple paragraph."""
    return f"<p>{escape(text)}</p>"


def rich_bold(text: str) -> str:
    return f"<b>{escape(text)}</b>"


def rich_italic(text: str) -> str:
    return f"<i>{escape(text)}</i>"


def rich_underline(text: str) -> str:
    return f"<u>{escape(text)}</u>"


def rich_strikethrough(text: str) -> str:
    return f"<s>{escape(text)}</s>"