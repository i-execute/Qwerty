"""Tests for the native Rich Message blocks converter (Bot API 10.2)."""

import pytest

from plugins.platforms.telegram.rich_blocks import (
    RichBlocksError,
    has_native_markers,
    markdown_to_blocks,
    parse_inline,
    strip_thinking_blocks,
)


def test_empty_raises():
    with pytest.raises(RichBlocksError):
        markdown_to_blocks("")
    with pytest.raises(RichBlocksError):
        markdown_to_blocks("   \n  ")


def test_headings():
    blocks = markdown_to_blocks("## Title\n### Sub\n")
    assert blocks[0] == {"type": "heading", "text": ["Title"], "size": 2}
    assert blocks[1] == {"type": "heading", "text": ["Sub"], "size": 3}


def test_inline_bold_italic_code():
    blocks = markdown_to_blocks("**bold** and *italic* and `code`")
    text = blocks[0]["text"]
    assert text[0] == {"type": "bold", "text": ["bold"]}
    assert any(x == {"type": "italic", "text": ["italic"]} for x in text)
    assert any(x == {"type": "code", "text": ["code"]} for x in text)


def test_inline_misc():
    line = "~~s~~ ||sp|| ==m== [l](https://t.me) $x^2$ ^up^ ~dn~"
    text = parse_inline(line)
    assert any(x.get("type") == "strikethrough" for x in text if isinstance(x, dict))
    assert any(x.get("type") == "spoiler" for x in text if isinstance(x, dict))
    assert any(x.get("type") == "marked" for x in text if isinstance(x, dict))
    assert any(x.get("type") == "url" for x in text if isinstance(x, dict))
    assert any(x.get("type") == "mathematical_expression" for x in text if isinstance(x, dict))
    assert any(x.get("type") == "superscript" for x in text if isinstance(x, dict))
    assert any(x.get("type") == "subscript" for x in text if isinstance(x, dict))


def test_table_striped_bordered_with_align():
    blocks = markdown_to_blocks(
        "| A | B | C |\n"
        "|---|:---:|---:|\n"
        "| 1 | 2 | 3 |\n"
    )
    table = blocks[0]
    assert table["type"] == "table"
    assert table["is_bordered"] is True
    assert table["is_striped"] is True
    assert table["cells"][0][0]["is_header"] is True
    assert table["cells"][1][0]["align"] == "left"
    assert table["cells"][1][1]["align"] == "center"
    assert table["cells"][1][2]["align"] == "right"


def test_checkboxes_and_ordered_list():
    blocks = markdown_to_blocks("- [x] done\n- [ ] todo\n")
    lst = blocks[0]
    assert lst["type"] == "list"
    assert lst["items"][0]["has_checkbox"] is True
    assert lst["items"][0]["is_checked"] is True
    assert lst["items"][1]["is_checked"] is False

    blocks = markdown_to_blocks("1. first\n2. second\n")
    lst = blocks[0]
    assert lst["items"][0]["value"] == 1
    assert lst["items"][1]["value"] == 2


def test_blockquote_and_pullquote():
    blocks = markdown_to_blocks("> quoted line\n> second line\n")
    assert blocks[0]["type"] == "blockquote"
    assert blocks[0]["blocks"][0]["type"] == "paragraph"

    blocks = markdown_to_blocks(":::pullquote Someone\nCentered quote\n:::\n")
    pq = blocks[0]
    assert pq["type"] == "pullquote"
    assert pq["text"] == ["Centered quote"]
    assert pq["credit"] == ["Someone"]


def test_details_open_and_footer():
    blocks = markdown_to_blocks(
        ":::details Secrets open\nhidden content\n:::\n:::footer\nMade with love\n:::\n"
    )
    d = blocks[0]
    assert d["type"] == "details"
    assert d["summary"] == ["Secrets"]
    assert d["is_open"] is True
    assert d["blocks"][0]["text"] == ["hidden content"]
    assert blocks[1]["type"] == "footer"


def test_slideshow_and_collage():
    blocks = markdown_to_blocks(
        ":::slideshow Our shots\n"
        "![](https://example.com/1.png)\n"
        "![](https://example.com/2.png)\n"
        ":::\n"
    )
    ss = blocks[0]
    assert ss["type"] == "slideshow"
    assert len(ss["blocks"]) == 2
    assert ss["blocks"][0]["type"] == "photo"
    assert ss["blocks"][0]["photo"]["media"] == "https://example.com/1.png"
    assert ss["caption"]["text"] == ["Our shots"]

    blocks = markdown_to_blocks(":::collage\n![](https://example.com/a.jpg)\n:::\n")
    assert blocks[0]["type"] == "collage"
    assert blocks[0]["blocks"][0]["photo"]["media"] == "https://example.com/a.jpg"


def test_math_blocks():
    blocks = markdown_to_blocks("$$E = mc^2$$\n")
    assert blocks[0] == {"type": "mathematical_expression", "expression": "E = mc^2"}

    blocks = markdown_to_blocks("$$\n\\int_0^1 x^2 dx\n$$\n")
    assert blocks[0]["type"] == "mathematical_expression"
    assert "int" in blocks[0]["expression"]


def test_pre_block_with_language():
    blocks = markdown_to_blocks("```python\nprint('hi')\n```\n")
    assert blocks[0]["type"] == "pre"
    assert blocks[0]["language"] == "python"
    assert blocks[0]["text"] == ["print('hi')"]


def test_divider_anchor_map_media():
    blocks = markdown_to_blocks("---\n")
    assert blocks[0] == {"type": "divider"}

    blocks = markdown_to_blocks(":::anchor top\n")
    assert blocks[0] == {"type": "anchor", "name": "top"}

    blocks = markdown_to_blocks(":::map 55.7558 37.6173 12 400 300\n")
    m = blocks[0]
    assert m["type"] == "map"
    assert m["location"] == {"latitude": 55.7558, "longitude": 37.6173}
    assert m["zoom"] == 12

    blocks = markdown_to_blocks(":::video https://example.com/v.mp4|Cool video\n")
    assert blocks[0]["type"] == "video"
    assert blocks[0]["video"]["media"] == "https://example.com/v.mp4"
    assert blocks[0]["caption"]["text"] == ["Cool video"]


def test_thinking_stripped_in_final():
    blocks = markdown_to_blocks(
        "## Report\n:::thinking\nworking...\n:::\ndone\n"
    )
    assert any(b["type"] == "thinking" for b in blocks)
    final = strip_thinking_blocks(blocks)
    assert not any(b["type"] == "thinking" for b in final)
    assert final[0]["type"] == "heading"


def test_has_native_markers():
    assert not has_native_markers("просто текст без маркеров")
    assert has_native_markers("| a | b |")
    assert has_native_markers(":::slideshow x")
    assert has_native_markers("- [ ] task")
    assert has_native_markers("> quote")
    assert has_native_markers("$$math$$")
