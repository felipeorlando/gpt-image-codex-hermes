# GPT Image Codex Hermes

Hermes-native adaptation of [`wuyoscar/gpt_image_2_skill`](https://github.com/wuyoscar/gpt_image_2_skill).

This repo exists for one specific reason: use **GPT Image 2** inside **Hermes Agent** through the native **OpenAI Codex / ChatGPT OAuth** flow instead of requiring `OPENAI_API_KEY`.

## What changed vs upstream

Upstream:
- expects `OPENAI_API_KEY`
- calls direct OpenAI image APIs
- supports generation and edit-style workflows

This adaptation:
- uses Hermes's native `openai-codex` image generation support
- reuses Hermes auth state
- does **not** require `OPENAI_API_KEY`
- currently focuses on **text-to-image generation**

## Status

Working now:
- Hermes-native auth via `openai-codex`
- CLI wrapper for generation
- Hermes skill folder for local install
- local validation on a Hermes environment

Not implemented yet:
- reference-image edits
- inpainting / masks
- multi-image compositing

## Hermes setup

Make sure Hermes already has Codex auth:

```bash
hermes auth list openai-codex
```

Recommended config:

```bash
hermes config set image_gen.provider openai-codex
hermes config set image_gen.model gpt-image-2-medium
hermes config set image_gen.openai-codex.model gpt-image-2-medium
```

## Install in Hermes

Option 1, install manually into the local Hermes skills directory:

```bash
git clone https://github.com/felipeorlando/gpt-image-codex-hermes.git
mkdir -p ~/.hermes/skills/creative
cp -R gpt-image-codex-hermes/skills/gpt-image-codex-hermes ~/.hermes/skills/creative/
```

Option 2, use the repo directly without copying the skill:

```bash
git clone https://github.com/felipeorlando/gpt-image-codex-hermes.git
cd gpt-image-codex-hermes
uv run skills/gpt-image-codex-hermes/scripts/generate.py -p "a cat astronaut on the moon"
```

## CLI usage

```bash
uv run skills/gpt-image-codex-hermes/scripts/generate.py -p "a cat astronaut on the moon"
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

## Hermes-native notes

The key implementation lives in:

- `src/gpt_image_cli/cli.py`

That file reads Hermes Codex auth by importing Hermes internals and sending the request through the ChatGPT/Codex Responses API `image_generation` tool path.

## Upstream credit

Original repo and prompt/gallery base:

- https://github.com/wuyoscar/gpt_image_2_skill

This repo is an adaptation, not an original gallery rewrite.

## License

This repo keeps the upstream CC BY 4.0 licensing model unless a subfile states otherwise.
