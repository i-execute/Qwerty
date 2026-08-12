# Math & Formula Rendering in Telegram Rich Messages

**Tested:** Bot API 10.1 with Hermes Telegram adapter (`plugins/platforms/telegram/adapter.py`)

## What Works

### 1. Code Blocks with Language Tag (Best for LaTeX)
```html
<pre><code class="language-latex">
E = mc^2
\int_{-\infty}^{\infty} e^{-x^2} dx = \sqrt{\pi}
\sum_{n=1}^{\infty} \frac{1}{n^2} = \frac{\pi^2}{6}
e^{ix} = \cos(x) + i\sin(x)
</code></pre>
```
Renders with syntax highlighting (language "latex").

### 2. Inline Code with LaTeX
```html
<p>Quadratic: <code>x = \frac{-b \pm \sqrt{b^2-4ac}}{2a}</code></p>
<p>Euler: <code>e^{i\pi} + 1 = 0</code></p>
```
Renders as monospace with syntax highlighting.

### 3. Unicode Math Symbols (Native Rendering)
```html
<p>∫₀^∞ e⁻ˣ² dx = √π/2</p>
<p>∑ₙ₌₁^∞ 1/n² = π²/6</p>
<p>∀x ∈ ℝ: x² ≥ 0</p>
<p>∃!x: x² = 2 → x = √2</p>
```
Renders natively in Telegram clients (Desktop, Android, iOS).

### 4. HTML Sub/Superscript
```html
<p>x<sup>2</sup> + y<sup>2</sup> = r<sup>2</sup></p>
<p>H<sub>2</sub>O</p>
<p>x<sub>1</sub>, x<sub>2</sub> = (-b ± √(b²-4ac))/2a</p>
```
Works in rich messages.

### 5. Tables with Math
```html
<table>
  <tr><th>Formula</th><th>LaTeX</th><th>Unicode</th></tr>
  <tr><td>Quadratic</td><td><code>x = (-b ± √(b²-4ac))/2a</code></td><td>x = (-b ± √(b²-4ac))/2a</td></tr>
  <tr><td>Euler</td><td><code>e^{iπ} + 1 = 0</code></td><td>e<sup>iπ</sup> + 1 = 0</td></tr>
</table>
```

### 5. Code Blocks with Aligned Equations
```html
<pre><code class="language-latex">
\begin{aligned}
\nabla \times \mathbf{E} &= -\frac{\partial \mathbf{B}}{\partial t} \\
\nabla \cdot \mathbf{D} &= \rho \\
\nabla \times \mathbf{H} &= \mathbf{J} + \frac{\partial \mathbf{D}}{\partial t} \\
\nabla \cdot \mathbf{B} &= 0
\end{aligned}
</code></pre>
```

## What Does NOT Work

| Tag/Method | Error | Alternative |
|------------|-------|-------------|
| `<sup>` | `RICH_MESSAGE_BLOCK_UNSUPPORTED` | Use `<sup>` HTML tag OR unicode superscripts (¹²³⁴⁵⁶⁷⁸⁹⁰) |
| `<sub>` | `RICH_MESSAGE_BLOCK_UNSUPPORTED` | Use `<sub>` HTML tag OR unicode subscripts (₁₂₃₄₅₆₇₈₉₀) |
| `<tg-thinking>` in final message | `RICH_MESSAGE_BLOCK_UNSUPPORTED` | Use `<b>Thinking...</b>` or plain text; **only works in `sendRichMessageDraft`** |
| `<tg-spoiler>` | `RICH_MESSAGE_BLOCK_UNSUPPORTED` | Use `<details><summary>Spoiler</summary>Content</details>` |
| `<tg-emoji>` | `RICH_MESSAGE_BLOCK_UNSUPPORTED` | Use regular emoji or custom emoji via Telegram Premium |
| `$$...$$` or `\(...\)` in rich HTML | Not parsed | Use `<code>` blocks or Unicode |

## Streaming with Thinking Animation

**Only works in `sendRichMessageDraft` (streaming frames):**

```python
# Frame 1
<h1>Factorization N = 91</h1>
<tg-thinking>Starting Shor's algorithm...</tg-thinking>

# Frame 2
<h1>Factorization N = 91</h1>
<tg-thinking>Attempt 1: a = 847 -- Finding period r via classical simulation...</tg-thinking>
<table>...</table>

# Frame 3 (final via sendRichMessage - NO tg-thinking!)
<h1>Factorization N = 91</h1>
<table>...</table>
<h2>Result</h2>
<p><b>91 = 7 × 13</b></p>
```

The Hermes adapter (`plugins/platforms/telegram/adapter.py`) handles this automatically:
- `_try_send_rich_draft()` → sends frames WITH `<tg-thinking>`
- `_try_edit_rich()` → finalizes WITHOUT `<tg-thinking>`

## Helper Functions (in `references/rich_helpers.py`)

```python
from skills.social_media.telegram_rich_messages.references.rich_helpers import (
    rich_table, rich_code, rich_thinking, rich_details,
    format_factorization_rich, validate_rich_html
)

# Formula in code block
code = rich_code("x = (-b ± √(b²-4ac))/2a", "latex")

# Unicode math in text
html = f"<p>Euler: <code>e^{{iπ}} + 1 = 0</code></p>"

# Sub/superscript
html = "<p>x<sup>2</sup> + y<sup>2</sup> = r<sup>2</sup></p>"
html = "<p>H<sub>2</sub>O</p>"
```