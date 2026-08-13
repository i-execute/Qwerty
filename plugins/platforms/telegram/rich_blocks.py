"""Native Rich Message blocks builder (Bot API 10.2).

Converts the agent's extended Markdown dialect ("RichMarkdown") into the
structured ``InputRichBlock`` / ``RichText`` object lists consumed by
``sendRichMessage(rich_message={"blocks": [...]})``.

Field names and shapes follow the official Bot API documentation exactly:

- InputRichMessage: exactly ONE of html / markdown / blocks (+ optional media)
- table:  ``cells`` (array of arrays of RichBlockTableCell), is_bordered, is_striped
- pullquote: ``text`` (RichText) + optional ``credit``
- blockquote: ``blocks`` + optional ``credit``
- slideshow/collage: ``blocks`` + optional ``caption``
- list items: ``blocks`` + has_checkbox / is_checked / value / type
- heading: ``text`` + ``size`` (1-6, 1 largest)
- thinking: allowed ONLY in sendRichMessageDraft frames

Dialect (extended markdown):

  Blocks:
    # … ######           -> heading (size = number of #)
    > line               -> blockquote (consecutive lines merged)
    ```lang              -> pre (language)
    ---                  -> divider
    - item / 1. item     -> list / ordered list (value from number)
    - [ ] / - [x]        -> checkbox list items
    | a | b |            -> table (header row + |---| separators, :-- align)
    $$latex$$            -> mathematical_expression block
    :::slideshow caption -> slideshow of photo/video blocks until :::
    :::collage caption   -> collage of photo/video blocks until :::
    :::pullquote credit  -> pullquote (first content line is the quote text)
    :::details Summary [open] -> collapsible details until :::
    :::footer text…      -> footer until :::
    :::thinking text…    -> thinking block (drafts only)
    :::anchor name       -> anchor (single line)
    :::map lat lon zoom w h -> map (single line)
    :::photo src|caption / :::video src|caption / :::animation src|caption
    :::audio src|caption / :::voice src|caption   -> media blocks (single line)
    ![](src)             -> standalone photo block (also inside slideshow/collage)

  Inline:
    **bold** __bold__ *italic* _italic_ ~~strike~~ ||spoiler|| ==marked==
    `code` $latex$ [text](url) ^sup^ ~sub~

Anything not matching the above stays plain text. If the whole message has no
native markers, callers should keep the legacy markdown payload path.
"""

from __future__ import annotations

import re
from typing import Any, List, Optional

__all__ = [
    "RichBlocksError",
    "markdown_to_blocks",
    "has_native_markers",
    "parse_inline",
    "strip_thinking_blocks",
]

# Regexes for inline markup, ordered by priority.
_RE_CODE = re.compile(r"`([^`\n]+)`")
_RE_BOLD = re.compile(r"\*\*(.+?)\*\*|__(.+?)__", re.S)
_RE_ITALIC = re.compile(r"(?<!\*)\*([^*\n]+)\*(?!\*)|(?<!_)_([^_\n]+)_(?!_)")
_RE_STRIKE = re.compile(r"~~(.+?)~~", re.S)
_RE_SPOILER = re.compile(r"\|\|(.+?)\|\|", re.S)
_RE_MARKED = re.compile(r"==(.+?)==", re.S)
_RE_URL = re.compile(r"\[([^\]\n]+)\]\(([^)\s]+)\)")
_RE_MATH = re.compile(r"\$([^$\n]+)\$")
_RE_SUP = re.compile(r"\^([^^\n]+)\^")
_RE_SUB = re.compile(r"~([^~\n]+)~")
_RE_MENTION = re.compile(r"(?<![\w@])@([A-Za-z][A-Za-z0-9_]{3,30})(?![\w])")
_RE_CUSTOM_EMOJI = re.compile(r"!\[([^\]]*)\]\(tg://emoji\?id=([0-9]+)\)")

# Block-level markers.
_RE_HEADING = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
_RE_HR = re.compile(r"^\s*(?:---|\*\*\*|___)\s*$")
_RE_FENCE = re.compile(r"^```(\S*)\s*$")
_RE_UNORDERED = re.compile(r"^(\s*)[-*+]\s+(.*)$")
_RE_ORDERED = re.compile(r"^(\s*)([0-9]+)[.)]\s+(.*)$")
_RE_CHECKBOX = re.compile(r"^(\s*)[-*+]\s+\[( |x|X)\]\s+(.*)$")
_RE_TABLE_ROW = re.compile(r"^\s*\|.*\|\s*$")
_RE_TABLE_SEP = re.compile(r"^\s*\|[\s:|-]+\|\s*$")
_RE_DIRECTIVE = re.compile(r"^:::\s*([A-Za-z_]+)\s*(.*)$")
_RE_CLOSE = re.compile(r"^\s*:::\s*$")
_RE_QUOTE = re.compile(r"^>\s?(.*)$")
_RE_MATH_BLOCK_OPEN = re.compile(r"^\$\$\s*$")
_RE_MATH_BLOCK_ONELINE = re.compile(r"^\$\$(.+?)\$\$\s*$")
_RE_IMAGE = re.compile(r"^!\[([^\]]*)\]\(([^)]+)\)\s*$")


class RichBlocksError(ValueError):
    """Raised when content cannot be converted to native blocks."""


def _plain(text: str) -> str:
    return text


def _parse_inline_rec(text: str, depth: int = 0) -> List[Any]:
    """Parse a single line of inline markup into RichText pieces."""
    if depth > 12:
        return [text]

    def split_first(pattern: re.Pattern) -> Optional[tuple]:
        m = pattern.search(text)
        if not m:
            return None
        return m

    # Custom emoji links (must come before url/image handling).
    m = _RE_CUSTOM_EMOJI.search(text)
    if m:
        alt, emoji_id = m.group(1), m.group(2)
        out: List[Any] = []
        if m.start() > 0:
            out.extend(parse_inline(text[: m.start()]))
        out.append(
            {
                "type": "custom_emoji",
                "custom_emoji_id": emoji_id,
                "alternative_text": alt or "😀",
            }
        )
        if m.end() < len(text):
            out.extend(parse_inline(text[m.end() :]))
        return out

    m = _RE_CODE.search(text)
    if m:
        out = []
        if m.start() > 0:
            out.extend(parse_inline(text[: m.start()]))
        out.append({"type": "code", "text": [m.group(1)]})
        if m.end() < len(text):
            out.extend(parse_inline(text[m.end() :]))
        return out

    m = _RE_BOLD.search(text)
    if m:
        inner = m.group(1) if m.group(1) is not None else m.group(2)
        out = []
        if m.start() > 0:
            out.extend(parse_inline(text[: m.start()]))
        out.append({"type": "bold", "text": parse_inline(inner)})
        if m.end() < len(text):
            out.extend(parse_inline(text[m.end() :]))
        return out

    m = _RE_ITALIC.search(text)
    if m:
        inner = m.group(1) if m.group(1) is not None else m.group(2)
        out = []
        if m.start() > 0:
            out.extend(parse_inline(text[: m.start()]))
        out.append({"type": "italic", "text": parse_inline(inner)})
        if m.end() < len(text):
            out.extend(parse_inline(text[m.end() :]))
        return out

    m = _RE_STRIKE.search(text)
    if m:
        out = []
        if m.start() > 0:
            out.extend(parse_inline(text[: m.start()]))
        out.append({"type": "strikethrough", "text": parse_inline(m.group(1))})
        if m.end() < len(text):
            out.extend(parse_inline(text[m.end() :]))
        return out

    m = _RE_SPOILER.search(text)
    if m:
        out = []
        if m.start() > 0:
            out.extend(parse_inline(text[: m.start()]))
        out.append({"type": "spoiler", "text": parse_inline(m.group(1))})
        if m.end() < len(text):
            out.extend(parse_inline(text[m.end() :]))
        return out

    m = _RE_MARKED.search(text)
    if m:
        out = []
        if m.start() > 0:
            out.extend(parse_inline(text[: m.start()]))
        out.append({"type": "marked", "text": parse_inline(m.group(1))})
        if m.end() < len(text):
            out.extend(parse_inline(text[m.end() :]))
        return out

    m = _RE_URL.search(text)
    if m:
        out = []
        if m.start() > 0:
            out.extend(parse_inline(text[: m.start()]))
        out.append({"type": "url", "text": parse_inline(m.group(1)), "url": m.group(2)})
        if m.end() < len(text):
            out.extend(parse_inline(text[m.end() :]))
        return out

    m = _RE_MATH.search(text)
    if m:
        out = []
        if m.start() > 0:
            out.extend(parse_inline(text[: m.start()]))
        out.append({"type": "mathematical_expression", "expression": m.group(1)})
        if m.end() < len(text):
            out.extend(parse_inline(text[m.end() :]))
        return out

    m = _RE_SUP.search(text)
    if m:
        out = []
        if m.start() > 0:
            out.extend(parse_inline(text[: m.start()]))
        out.append({"type": "superscript", "text": parse_inline(m.group(1))})
        if m.end() < len(text):
            out.extend(parse_inline(text[m.end() :]))
        return out

    m = _RE_SUB.search(text)
    if m:
        out = []
        if m.start() > 0:
            out.extend(parse_inline(text[: m.start()]))
        out.append({"type": "subscript", "text": parse_inline(m.group(1))})
        if m.end() < len(text):
            out.extend(parse_inline(text[m.end() :]))
        return out

    m = _RE_MENTION.search(text)
    if m:
        out = []
        if m.start() > 0:
            out.extend(parse_inline(text[: m.start()]))
        out.append(
            {"type": "mention", "text": ["@" + m.group(1)], "username": m.group(1)}
        )
        if m.end() < len(text):
            out.extend(parse_inline(text[m.end() :]))
        return out

    return [text]


def parse_inline(text: str) -> List[Any]:
    """Parse inline markup in a single line into RichText pieces (str or dict)."""
    if not text:
        return []
    return _parse_inline_rec(text)


def _split_table_row(line: str) -> List[str]:
    inner = line.strip()
    if inner.startswith("|"):
        inner = inner[1:]
    if inner.endswith("|"):
        inner = inner[:-1]
    return [c.strip() for c in inner.split("|")]


def _parse_align(sep_cells: List[str]) -> List[str]:
    aligns = []
    for cell in sep_cells:
        cell = cell.strip()
        has_left = cell.startswith(":")
        has_right = cell.endswith(":")
        if has_left and has_right:
            aligns.append("center")
        elif has_right:
            aligns.append("right")
        elif has_left:
            aligns.append("left")
        else:
            aligns.append("left")
    return aligns


def _table_block(lines: List[str]) -> dict:
    cells: List[List[dict]] = []
    aligns: List[str] = []
    for idx, line in enumerate(lines):
        raw_cells = _split_table_row(line)
        if idx == 1 and _RE_TABLE_SEP.match(line):
            aligns = _parse_align(raw_cells)
            continue
        row = []
        for ci, cell in enumerate(raw_cells):
            entry: dict = {
                "text": parse_inline(cell),
                "is_header": idx == 0,
            }
            if idx != 1 and ci < len(aligns):
                entry["align"] = aligns[ci]
            row.append(entry)
        if row:
            cells.append(row)
    return {"type": "table", "cells": cells, "is_bordered": True, "is_striped": True}


def _media_block(kind: str, src: str, caption: Optional[str]) -> dict:
    media_field = {
        "photo": "photo",
        "video": "video",
        "animation": "animation",
        "audio": "audio",
        "voice": "voice_note",
    }[kind]
    block: dict = {"type": media_field, media_field: {"media": src}}
    if caption:
        block["caption"] = {"text": parse_inline(caption)}
    return block


def _parse_blocks(lines: List[str]) -> List[dict]:
    """Parse a list of source lines into a list of InputRichBlock dicts."""
    blocks: List[dict] = []
    i = 0
    n = len(lines)
    while i < n:
        line = lines[i]

        # Blank line.
        if not line.strip():
            i += 1
            continue

        # Math block.
        if _RE_MATH_BLOCK_OPEN.match(line):
            expr_lines = []
            i += 1
            while i < n and not _RE_MATH_BLOCK_OPEN.match(lines[i]):
                expr_lines.append(lines[i])
                i += 1
            if i < n:
                i += 1  # closing $$
            blocks.append(
                {
                    "type": "mathematical_expression",
                    "expression": "\n".join(expr_lines).strip(),
                }
            )
            continue

        # One-line math block: $$...$$ on a single line.
        m = _RE_MATH_BLOCK_ONELINE.match(line)
        if m:
            blocks.append(
                {"type": "mathematical_expression", "expression": m.group(1).strip()}
            )
            i += 1
            continue

        # Code fence.
        m = _RE_FENCE.match(line)
        if m:
            lang = m.group(1)
            code_lines = []
            i += 1
            while i < n and not _RE_FENCE.match(lines[i]):
                code_lines.append(lines[i])
                i += 1
            if i < n:
                i += 1  # closing fence
            block: dict = {
                "type": "pre",
                "text": ["\n".join(code_lines)],
            }
            if lang:
                block["language"] = lang
            blocks.append(block)
            continue

        # Directive openers / single-line directives.
        m = _RE_DIRECTIVE.match(line)
        if m:
            kind = m.group(1).lower()
            arg = m.group(2).strip()
            if kind == "anchor":
                blocks.append({"type": "anchor", "name": arg.split()[0] if arg else ""})
                i += 1
                continue
            if kind == "map":
                parts = arg.split()
                if len(parts) >= 2:
                    lat = float(parts[0])
                    lon = float(parts[1])
                    zoom = int(parts[2]) if len(parts) > 2 else 15
                    width = int(parts[3]) if len(parts) > 3 else 300
                    height = int(parts[4]) if len(parts) > 4 else 200
                    blocks.append(
                        {
                            "type": "map",
                            "location": {"latitude": lat, "longitude": lon},
                            "zoom": zoom,
                            "width": width,
                            "height": height,
                        }
                    )
                i += 1
                continue
            if kind in {"photo", "video", "animation", "audio", "voice"}:
                src, _, cap = arg.partition("|")
                blocks.append(_media_block(kind, src.strip(), cap.strip() or None))
                i += 1
                continue
            if kind == "thinking":
                blocks.append({"type": "thinking", "text": parse_inline(arg or "…")})
                i += 1
                continue
            # Multi-line directive blocks.
            body: List[str] = []
            i += 1
            while i < n and not _RE_CLOSE.match(lines[i]):
                body.append(lines[i])
                i += 1
            if i < n:
                i += 1  # closing :::
            inner_blocks = _parse_blocks(body)
            if kind == "slideshow":
                slides = [b for b in inner_blocks if b.get("type") in {"photo", "video", "animation"}]
                if not slides:
                    # Fall back: images written as ![](src) inside get parsed as paragraphs;
                    # re-scan body lines for image lines.
                    slides = []
                    for b_line in body:
                        im = _RE_IMAGE.match(b_line.strip())
                        if im:
                            slides.append(_media_block("photo", im.group(2), im.group(1) or None))
                block = {"type": "slideshow", "blocks": slides}
                if arg:
                    block["caption"] = {"text": parse_inline(arg)}
                blocks.append(block)
                continue
            if kind == "collage":
                items = [b for b in inner_blocks if b.get("type") in {"photo", "video", "animation"}]
                if not items:
                    items = []
                    for b_line in body:
                        im = _RE_IMAGE.match(b_line.strip())
                        if im:
                            items.append(_media_block("photo", im.group(2), im.group(1) or None))
                block = {"type": "collage", "blocks": items}
                if arg:
                    block["caption"] = {"text": parse_inline(arg)}
                blocks.append(block)
                continue
            if kind == "pullquote":
                quote_text = body[0].strip() if body else ""
                block = {
                    "type": "pullquote",
                    "text": parse_inline(quote_text),
                }
                if arg:
                    block["credit"] = parse_inline(arg)
                blocks.append(block)
                continue
            if kind == "details":
                summary = arg
                is_open = False
                if summary.endswith(" open"):
                    is_open = True
                    summary = summary[: -len(" open")].rstrip()
                blocks.append(
                    {
                        "type": "details",
                        "summary": parse_inline(summary),
                        "blocks": inner_blocks,
                        "is_open": is_open,
                    }
                )
                continue
            if kind == "footer":
                blocks.append(
                    {"type": "footer", "text": parse_inline(" ".join(body))}
                )
                continue
            if kind == "quote":
                block = {"type": "blockquote", "blocks": inner_blocks}
                if arg:
                    block["credit"] = parse_inline(arg)
                blocks.append(block)
                continue
            # Unknown directive: treat contents as plain paragraphs.
            blocks.extend(inner_blocks)
            continue

        # Horizontal rule.
        if _RE_HR.match(line):
            blocks.append({"type": "divider"})
            i += 1
            continue

        # Heading.
        m = _RE_HEADING.match(line)
        if m:
            blocks.append(
                {
                    "type": "heading",
                    "text": parse_inline(m.group(2)),
                    "size": len(m.group(1)),
                }
            )
            i += 1
            continue

        # Blockquote group.
        m = _RE_QUOTE.match(line)
        if m:
            quote_lines = []
            while i < n and _RE_QUOTE.match(lines[i]):
                quote_lines.append(_RE_QUOTE.match(lines[i]).group(1))
                i += 1
            blocks.append(
                {"type": "blockquote", "blocks": _parse_blocks(quote_lines)}
            )
            continue

        # Table group: header row + separator + rows.
        if _RE_TABLE_ROW.match(line):
            table_lines = []
            while i < n and _RE_TABLE_ROW.match(lines[i]):
                table_lines.append(lines[i])
                i += 1
            blocks.append(_table_block(table_lines))
            continue

        # List group (supports one nesting level via indentation).
        item_match = _RE_CHECKBOX.match(line) or _RE_UNORDERED.match(line) or _RE_ORDERED.match(line)
        if item_match and (line.lstrip().startswith(("-", "*", "+")) or _RE_ORDERED.match(line)):
            items: List[dict] = []
            ordered = False
            while i < n:
                cb = _RE_CHECKBOX.match(lines[i])
                ul = _RE_UNORDERED.match(lines[i])
                ol = _RE_ORDERED.match(lines[i])
                if cb:
                    has_checkbox = True
                    checked = cb.group(2).lower() == "x"
                    text = cb.group(3)
                    indent = len(cb.group(1))
                elif ul:
                    has_checkbox = False
                    checked = False
                    text = ul.group(2)
                    indent = len(ul.group(1))
                elif ol:
                    ordered = True
                    has_checkbox = False
                    checked = False
                    text = ol.group(3)
                    indent = len(ol.group(1))
                else:
                    break
                # Gather continuation lines belonging to this item.
                item_lines = [text]
                j = i + 1
                while j < n and lines[j].strip() and not (
                    _RE_CHECKBOX.match(lines[j])
                    or _RE_UNORDERED.match(lines[j])
                    or _RE_ORDERED.match(lines[j])
                    or _RE_HEADING.match(lines[j])
                    or _RE_HR.match(lines[j])
                    or _RE_DIRECTIVE.match(lines[j])
                ):
                    item_lines.append(lines[j].strip())
                    j += 1
                item: dict = {"blocks": _parse_blocks(item_lines)}
                if has_checkbox:
                    item["has_checkbox"] = True
                    item["is_checked"] = checked
                if ordered and ol:
                    item["value"] = int(ol.group(2))
                    item["type"] = "1"
                items.append(item)
                i = j
                # Nested items become part of the previous item's blocks.
                _ = indent  # reserved for deeper nesting; items keep flat order
            blocks.append({"type": "list", "items": items})
            continue

        # Image line.
        m = _RE_IMAGE.match(line.strip())
        if m:
            blocks.append(_media_block("photo", m.group(2), m.group(1) or None))
            i += 1
            continue

        # Plain paragraph: gather consecutive plain lines.
        para_lines = [line.strip()]
        i += 1
        while i < n and lines[i].strip():
            stripped = lines[i].strip()
            if (
                _RE_HEADING.match(stripped)
                or _RE_HR.match(stripped)
                or _RE_QUOTE.match(stripped)
                or _RE_TABLE_ROW.match(stripped)
                or _RE_FENCE.match(stripped)
                or _RE_DIRECTIVE.match(stripped)
                or _RE_MATH_BLOCK_OPEN.match(stripped)
                or _RE_CHECKBOX.match(stripped)
                or _RE_UNORDERED.match(stripped)
                or _RE_ORDERED.match(stripped)
                or _RE_IMAGE.match(stripped)
            ):
                break
            para_lines.append(stripped)
            i += 1
        blocks.append({"type": "paragraph", "text": parse_inline("\n".join(para_lines))})
    return blocks


def markdown_to_blocks(text: str) -> List[dict]:
    """Convert RichMarkdown text into a list of InputRichBlock dicts.

    Raises RichBlocksError on empty content.
    """
    if not text or not text.strip():
        raise RichBlocksError("empty content")
    lines = text.split("\n")
    blocks = _parse_blocks(lines)
    if not blocks:
        raise RichBlocksError("no blocks produced")
    return blocks


_NATIVE_MARKER = re.compile(
    r"(^|\n)\s*:::[A-Za-z_]|^\$\$|^```|^\s*\|.*\|\s*$|^\s*[-*+]\s+\[[ xX]\]|^\s*>\s"
    , re.M,
)


def has_native_markers(text: str) -> bool:
    """True when the content uses RichMarkdown constructs that require the
    native blocks path (directives, tables, code fences, math blocks,
    checkboxes, blockquotes)."""
    return bool(_NATIVE_MARKER.search(text or ""))


def strip_thinking_blocks(blocks: List[dict]) -> List[dict]:
    """Remove thinking blocks (only allowed in drafts)."""

    def _walk(bl: dict) -> Optional[dict]:
        if bl.get("type") == "thinking":
            return None
        for key, value in list(bl.items()):
            if isinstance(value, list):
                if key in {"text", "summary"}:
                    continue  # RichText lists, not blocks
                bl[key] = [x for x in (_walk(b) if isinstance(b, dict) else b for b in value) if x is not None]
            elif isinstance(value, dict) and value.get("type") in {
                "paragraph", "heading", "blockquote", "details", "slideshow",
                "collage", "table", "list", "footer", "pre",
            }:
                bl[key] = _walk(value)
        return bl

    return [b for b in (_walk(x) for x in blocks) if b is not None]
