---
name: gpt-image-codex-hermes
description: Use when you want GPT Image 2 generation through Hermes native OpenAI Codex auth instead of OPENAI_API_KEY. This adapts the upstream gpt_image_2_skill workflow for Hermes by using ChatGPT/Codex OAuth and the image_generation tool path.
version: 0.1.0
author: Felipe Orlando / adapted from wuyoscar
license: CC-BY-4.0
metadata:
  hermes:
    tags: [image-generation, gpt-image-2, openai-codex, hermes, creative]
    related_skills: [hermes-agent]
---

# gpt-image-codex-hermes

## Overview

Hermes-native adaptation of the upstream `wuyoscar/gpt_image_2_skill` project.

The upstream project assumes direct OpenAI API access via `OPENAI_API_KEY`. This adaptation replaces that with Hermes's existing `openai-codex` auth flow, so image generation runs through ChatGPT/Codex OAuth and does not require a separate OpenAI API key.

## When to Use

- You want `gpt-image-2` in Hermes without `OPENAI_API_KEY`
- You already authenticated Hermes with Codex/ChatGPT
- You want a local CLI wrapper plus a reusable Hermes skill
- You want to generate polished images from prompts using Hermes-native auth

Do not use this when:
- You need direct OpenAI `images.edit` / mask editing today
- You need reference-image editing or inpainting
- You explicitly want API-key based billing through OpenAI

## Setup

Confirm Hermes has Codex auth:

```bash
hermes auth list openai-codex
```

Recommended Hermes config:

```bash
hermes config set image_gen.provider openai-codex
hermes config set image_gen.model gpt-image-2-medium
hermes config set image_gen.openai-codex.model gpt-image-2-medium
```

## One-line Usage

```bash
uv run ~/.hermes/skills/creative/gpt-image-codex-hermes/scripts/generate.py -p "PROMPT"
```

If you cloned this repo locally instead of installing the skill into Hermes:

```bash
uv run skills/gpt-image-codex-hermes/scripts/generate.py -p "PROMPT"
```

Examples:

```bash
uv run skills/gpt-image-codex-hermes/scripts/generate.py \
  -p "cinematic cyberpunk street in Tokyo rain, dense neon signage" \
  --size landscape --quality medium

uv run skills/gpt-image-codex-hermes/scripts/generate.py \
  -p 'tea poster with exact Chinese text "山川茶事" and elegant editorial layout' \
  --size portrait --quality high -f ./poster.png
```

## Current Scope

Supported now:
- text-to-image generation
- Hermes Codex auth reuse
- local CLI execution
- Hermes skill installation

Not supported yet:
- edits endpoint
- multi-reference compositing
- mask-based inpainting

## Upstream Reference Files

This repo preserves the upstream gallery/reference material under `skills/gpt-image-codex-hermes/references/` so prompt examples are still useful even though the auth/runtime path changed.

## Common Pitfalls

1. No Codex auth configured in Hermes.
2. Expecting this adaptation to support edits already.
3. Running the script on a machine without a local Hermes checkout or installed Hermes source.
4. Confusing Hermes tool config with this CLI wrapper. Both can coexist.

## Verification Checklist

- [ ] `hermes auth list openai-codex` shows an available credential
- [ ] `image_gen.provider` is set to `openai-codex` in Hermes config
- [ ] The script generates a PNG without `OPENAI_API_KEY`
- [ ] The generated file path prints to stdout
