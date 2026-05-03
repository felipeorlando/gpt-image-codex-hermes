#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from pathlib import Path

INTRO = '''> **Hermes adaptation notice**
>
> This repository is the Hermes-native adaptation of [`wuyoscar/gpt_image_2_skill`](https://github.com/wuyoscar/gpt_image_2_skill) for [`felipeorlando/gpt-image-codex-hermes`](https://github.com/felipeorlando/gpt-image-codex-hermes).
>
> - Uses **Hermes Agent** with native **OpenAI Codex / ChatGPT OAuth** instead of `OPENAI_API_KEY`
> - Primary local skill path is `skills/gpt-image-codex-hermes`
> - Primary CLI entry point is `gpt-image-codex-hermes`
> - **Current Hermes implementation is generation-only**
> - Sections and showcase items covering edits / inpainting are preserved below as **upstream reference** and are **not yet implemented in this Hermes adaptation**

'''

INSTALL_SECTION = '''## 📥 Install

<details>
<summary><strong>Hermes Agent</strong></summary>

Make sure Hermes already has Codex auth available:

```bash
hermes auth list openai-codex
hermes config set image_gen.provider openai-codex
hermes config set image_gen.model gpt-image-2-medium
hermes config set image_gen.openai-codex.model gpt-image-2-medium
```

Install the local skill folder into Hermes:

```bash
git clone https://github.com/felipeorlando/gpt-image-codex-hermes.git
cd gpt-image-codex-hermes

mkdir -p ~/.hermes/skills/creative
cp -R skills/gpt-image-codex-hermes ~/.hermes/skills/creative/
```

You can also symlink instead of copying:

```bash
ln -s "$PWD/skills/gpt-image-codex-hermes" ~/.hermes/skills/creative/gpt-image-codex-hermes
```

Restart Hermes after installation so the skill is reloaded.

</details>

<details>
<summary><strong>Manual agent-skill install</strong></summary>

Set `AGENT_SKILLS_DIR` to the skills directory used by your runtime, then symlink this repo's Hermes-adapted skill folder into it.

```bash
git clone https://github.com/felipeorlando/gpt-image-codex-hermes.git
cd gpt-image-codex-hermes

# Choose the skill directory for your runtime.
# Examples:
#   Hermes Agent: ~/.hermes/skills/creative
#   Other runtimes: use that runtime's documented skills directory.
export AGENT_SKILLS_DIR="/path/to/your/agent/skills"

mkdir -p "$AGENT_SKILLS_DIR"
ln -s "$PWD/skills/gpt-image-codex-hermes" "$AGENT_SKILLS_DIR/gpt-image-codex-hermes"
```

</details>

<details>
<summary><strong>CLI</strong></summary>

```bash
uvx --from git+https://github.com/felipeorlando/gpt-image-codex-hermes gpt-image-codex-hermes -p "a cat astronaut"

# or install to PATH
uv tool install git+https://github.com/felipeorlando/gpt-image-codex-hermes
gpt-image-codex-hermes -p "a cat astronaut"
```

Repo-local script entry point also works:

```bash
uv run skills/gpt-image-codex-hermes/scripts/generate.py -p "a cat astronaut"
```

</details>

<details>
<summary><strong>Update</strong></summary>

```bash
cd gpt-image-codex-hermes && git pull

# if installed as a uv tool
uv tool upgrade gpt-image-codex-hermes
```

This fork also ships a GitHub Action that can open PRs with upstream gallery/reference sync updates without overwriting Hermes-specific files.

</details>

Uses **Hermes Codex / ChatGPT OAuth auth state**. No `OPENAI_API_KEY` is required for the supported generation workflow.

---

## ⚡ Quick Usage & Prompting Fundamentals'''

EDIT_USAGE_NOTE = '''### Text + reference image → image (edit)

> **Upstream reference — not yet supported in this Hermes adaptation.**
>
> The original upstream project supports edit-style workflows through direct OpenAI image edit endpoints. This Hermes adaptation currently rejects `-i/--image` and `-m/--mask` and only supports text-to-image generation. The examples below are preserved so you can track upstream behavior and future parity targets.
'''

EDIT_GALLERY_NOTE = '''<h2 align="center">✨ Edit Endpoint Showcase</h2>

> **Upstream reference only.** These examples showcase the original upstream edit workflow. The current Hermes adaptation does **not** implement reference-image edits, mask-based inpainting, or multi-image compositing yet.
'''


def render(content: str) -> str:
    content = content.replace(
        '<h1 align="center">GPT Image 2 Prompt Gallery + Agentic Skill + CLI</h1>',
        '<h1 align="center">GPT Image Codex Hermes · GPT Image 2 Prompt Gallery + Hermes Skill + CLI</h1>',
        1,
    )
    content = content.replace(
        '<p align="center"><em>OpenAI GPT Image 2 prompt gallery, image prompt library, agentic skill, and CLI — curated, copy-paste prompts and runnable examples for skill-capable agents.</em></p>',
        '<p align="center"><em>Hermes-native GPT Image 2 prompt gallery, image prompt library, skill, and CLI — adapted from upstream for OpenAI Codex / ChatGPT OAuth inside Hermes Agent.</em></p>',
        1,
    )
    content = content.replace(
        'https://github.com/wuyoscar/gpt_image_2_skill/blob/main/LICENSE',
        'https://github.com/felipeorlando/gpt-image-codex-hermes/blob/main/LICENSE',
    )
    content = content.replace(
        'https://github.com/wuyoscar/gpt_image_2_skill/pulls',
        'https://github.com/felipeorlando/gpt-image-codex-hermes/pulls',
    )
    content = content.replace(
        '<td><strong>Agentic Skill + CLI</strong> — Claude Code / Codex, OpenClaw, Hermes Agent and other skill-capable agent runtimes</td>',
        '<td><strong>Hermes Skill + CLI + upstream-compatible gallery</strong> — optimized for Hermes Agent, while preserving the upstream prompt/reference corpus and showcase</td>',
    )
    content = content.replace(
        'Use this repo as a **GPT Image 2 prompt gallery**, **image prompt library**, **example of generation showcase**, **Codex / Claude Code agent skill**, and **gpt-image-2 CLI**. It includes reusable AI image prompts for research paper figures, posters, UI mockups, game HUDs, anime / manga, photography, typography, maps, tattoo design, and reference-image editing workflows.',
        'Use this repo as a **GPT Image 2 prompt gallery**, **image prompt library**, **Hermes Agent skill**, and **generation CLI**. It preserves the upstream showcase and reusable prompts for research paper figures, posters, UI mockups, game HUDs, anime / manga, photography, typography, maps, tattoo design, and edit-oriented reference workflows, while clearly marking which upstream capabilities are not yet implemented in Hermes.',
    )
    content = re.sub(
        r'## 📥 Install\n.*?\n---\n\n## ⚡ Quick Usage & Prompting Fundamentals',
        INSTALL_SECTION,
        content,
        count=1,
        flags=re.S,
    )
    content = content.replace(
        '---\n\n## ✨ At a glance\n',
        f'---\n\n{INTRO}## ✨ At a glance\n',
        1,
    )
    content = content.replace(
        'After install, every gallery entry below can be copy-pasted as `gpt-image -p "…"` or requested from any skill-capable agent runtime in natural language, e.g. *"generate the Boston Spring poster from the skill gallery"*.',
        'After install, every gallery entry below can be copy-pasted as `gpt-image-codex-hermes -p "…"` for generation or requested from Hermes Agent in natural language, e.g. *"generate the Boston Spring poster from the skill gallery"*.',
    )
    content = content.replace(
        'gpt-image -p "a photorealistic convenience store at 10pm" --size 1k --quality high -f store.png',
        'gpt-image-codex-hermes -p "a photorealistic convenience store at 10pm" --size 1k --quality high -f store.png',
    )
    content = content.replace(
        'Under the hood: `POST /v1/images/generations` with `model=gpt-image-2`.',
        'Under the hood in this adaptation: Hermes reuses your local `openai-codex` / ChatGPT OAuth session and routes generation through the Codex Responses API `image_generation` tool path using `gpt-image-2`.',
    )
    content = content.replace('### Text + reference image → image (edit)', EDIT_USAGE_NOTE, 1)
    content = content.replace(
        '| `-i, --image` | path (repeatable) | — | edits | Presence routes through `/v1/images/edits`. |',
        '| `-i, --image` | path (repeatable) | — | edits | Upstream reference only. The current Hermes adaptation rejects this flag. |',
    )
    content = content.replace(
        '| `-m, --mask` | path (PNG, alpha) | — | edits | Opaque = preserved, transparent = regenerated. Requires `-i`. |',
        '| `-m, --mask` | path (PNG, alpha) | — | edits | Upstream reference only. The current Hermes adaptation rejects this flag. |',
    )
    content = content.replace(
        '| `--input-fidelity` | `low` · `high` | — | edits | Supported on `gpt-image-1`/`1.5`. `gpt-image-2` rejects this parameter, so the CLI drops it locally. |',
        '| `--input-fidelity` | `low` · `high` | — | edits | Upstream reference only. Supported on `gpt-image-1`/`1.5`; not part of the current Hermes generation-only adaptation. |',
    )
    content = content.replace(
        'Every entry below ships **just the prompt plus a metadata line** (`"size"` · `"quality"` · source). Assemble the CLI / SDK call the same way every time — worked once here so per-entry code blocks can stay out of your way. Example for a `"portrait"` · `"high"` entry:',
        'Every entry below ships **just the prompt plus a metadata line** (`"size"` · `"quality"` · source). Assemble the Hermes CLI / SDK call the same way every time — worked once here so per-entry code blocks can stay out of your way. Example for a `"portrait"` · `"high"` entry:',
    )
    content = content.replace(
        'gpt-image -p "<PROMPT FROM ENTRY>" --size portrait --quality high -f out.png',
        'gpt-image-codex-hermes -p "<PROMPT FROM ENTRY>" --size portrait --quality high -f out.png',
    )
    content = content.replace(
        'For reference-based edits, add `-i ref.png` (repeatable) and optionally `-m mask.png` on the CLI, or call `client.images.edit(...)` with `image=[open(p, "rb") for p in refs]`. Everything else stays identical to the generate path.',
        'For this Hermes adaptation today, stay on the generate path shown above. Reference-based edits remain an upstream capability and future-parity target rather than a supported local feature.',
    )
    content = content.replace(
        'Exit codes: `0` success · `1` API/refusal error (full response body echoed to stderr) · `2` bad args or missing `OPENAI_API_KEY`.',
        'Exit codes in this Hermes adaptation: `0` success · `1` request/runtime/auth error · `2` bad args or use of unsupported edit/inpaint flags.',
    )
    content = content.replace('skills/gpt-image/references/', 'skills/gpt-image-codex-hermes/references/')
    content = content.replace('skills/gpt-image/references', 'skills/gpt-image-codex-hermes/references')
    content = content.replace('skills/gpt-image/scripts/generate.py', 'skills/gpt-image-codex-hermes/scripts/generate.py')
    content = content.replace('<h2 align="center">✨ Edit Endpoint Showcase</h2>', EDIT_GALLERY_NOTE, 1)
    return content


def main() -> int:
    parser = argparse.ArgumentParser(description='Render the local Hermes README from an upstream README source.')
    parser.add_argument('--source', default='README.upstream.md')
    parser.add_argument('--output', default='README.md')
    args = parser.parse_args()

    source = Path(args.source)
    output = Path(args.output)
    content = source.read_text(encoding='utf-8')
    output.write_text(render(content), encoding='utf-8')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
