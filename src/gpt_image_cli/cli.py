#!/usr/bin/env python3
from __future__ import annotations

import argparse
import base64
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

_HERMES_SRC_CANDIDATES = [
    Path.home() / '.hermes' / 'hermes-agent',
    Path.home() / '.hermes' / 'profiles' / 'default' / 'hermes-agent',
]
for _candidate in _HERMES_SRC_CANDIDATES:
    if _candidate.exists():
        sys.path.insert(0, str(_candidate))
        break

from openai import OpenAI

_CODEX_BASE_URL = 'https://chatgpt.com/backend-api/codex'
_CODEX_CHAT_MODEL = 'gpt-5.4'
_API_MODEL = 'gpt-image-2'
_CODEX_INSTRUCTIONS = (
    'You are an assistant that must fulfill image generation requests by '
    'using the image_generation tool when provided.'
)

SIZE_SHORTCUTS: dict[str, str] = {
    '1k': '1024x1024',
    '2k': '2048x2048',
    '4k': '3840x2160',
    'portrait': '1024x1536',
    'landscape': '1536x1024',
    'square': '1024x1024',
    'wide': '2048x1152',
    'tall': '2160x3840',
}


def slugify(text: str, max_len: int = 30) -> str:
    s = re.sub(r'[^\w\s-]', '', text.lower()).strip()
    s = re.sub(r'[-\s]+', '-', s)[:max_len]
    return s or 'image'


def default_output_path(prompt: str, extension: str = 'png') -> Path:
    cwd = Path.cwd()
    target_dir = cwd / 'fig' if (cwd / 'fig').is_dir() else cwd
    stamp = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
    return target_dir / f'{stamp}-{slugify(prompt)}.{extension}'


def resolve_size(value: str) -> str:
    return SIZE_SHORTCUTS.get(value.lower(), value)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        prog='gpt-image-codex-hermes',
        description='Generate GPT Image 2 images through Hermes-native Codex auth.',
    )
    p.add_argument('-p', '--prompt', required=True, help='Text prompt.')
    p.add_argument('-f', '--file', help='Output path. Auto-generated if omitted.')
    p.add_argument(
        '--size',
        default='1024x1024',
        help='Literal size or shortcut: 1k, 2k, 4k, portrait, landscape, square, wide, tall.',
    )
    p.add_argument('--quality', default='medium', choices=['low', 'medium', 'high'])
    p.add_argument('-n', '--n', type=int, default=1, help='Number of images to save.')
    p.add_argument('-i', '--image', action='append', default=None, help='Not supported in this adaptation.')
    p.add_argument('-m', '--mask', default=None, help='Not supported in this adaptation.')
    return p.parse_args()


def build_client() -> OpenAI:
    from agent.auxiliary_client import _codex_cloudflare_headers, _read_codex_access_token

    token = _read_codex_access_token()
    if not token:
        raise RuntimeError(
            'No Codex/ChatGPT OAuth credentials found. Run `hermes auth` or `hermes login --provider openai-codex`.'
        )
    return OpenAI(
        api_key=token,
        base_url=_CODEX_BASE_URL,
        default_headers=_codex_cloudflare_headers(token),
    )


def collect_image_b64(client: OpenAI, *, prompt: str, size: str, quality: str) -> list[str]:
    images: list[str] = []
    with client.responses.stream(
        model=_CODEX_CHAT_MODEL,
        store=False,
        instructions=_CODEX_INSTRUCTIONS,
        input=[{
            'type': 'message',
            'role': 'user',
            'content': [{'type': 'input_text', 'text': prompt}],
        }],
        tools=[{
            'type': 'image_generation',
            'model': _API_MODEL,
            'size': size,
            'quality': quality,
            'output_format': 'png',
            'background': 'opaque',
            'partial_images': max(1, int(1)),
        }],
        tool_choice={
            'type': 'allowed_tools',
            'mode': 'required',
            'tools': [{'type': 'image_generation'}],
        },
    ) as stream:
        for event in stream:
            event_type = getattr(event, 'type', '')
            if event_type == 'response.output_item.done':
                item = getattr(event, 'item', None)
                if getattr(item, 'type', None) == 'image_generation_call':
                    result = getattr(item, 'result', None)
                    if isinstance(result, str) and result:
                        images.append(result)
            elif event_type == 'response.image_generation_call.partial_image':
                partial = getattr(event, 'partial_image_b64', None)
                if isinstance(partial, str) and partial:
                    images.append(partial)
        final = stream.get_final_response()

    for item in getattr(final, 'output', None) or []:
        if getattr(item, 'type', None) == 'image_generation_call':
            result = getattr(item, 'result', None)
            if isinstance(result, str) and result and result not in images:
                images.append(result)
    return images


def write_images(images: list[str], out_path: Path, n: int) -> list[Path]:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    selected = images[: max(1, n)]
    for i, b64 in enumerate(selected):
        raw = base64.b64decode(b64)
        if len(selected) == 1:
            target = out_path
        else:
            stem = out_path.with_suffix('')
            target = stem.parent / f'{stem.name}_{i}{out_path.suffix}'
        target.write_bytes(raw)
        written.append(target)
    return written


def main() -> int:
    args = parse_args()

    if args.image or args.mask:
        print(
            'error: this Hermes adaptation currently supports generation only; edits/inpainting still require direct OpenAI API usage.',
            file=sys.stderr,
        )
        return 2

    out_path = Path(args.file).expanduser().resolve() if args.file else default_output_path(args.prompt)

    try:
        client = build_client()
        images = collect_image_b64(
            client,
            prompt=args.prompt,
            size=resolve_size(args.size),
            quality=args.quality,
        )
    except Exception as exc:
        print(f'error: {exc}', file=sys.stderr)
        return 1

    if not images:
        print('error: no image data returned by Codex image_generation', file=sys.stderr)
        return 1

    for path in write_images(images, out_path, args.n):
        print(path)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
