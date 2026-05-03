#!/usr/bin/env python3
from __future__ import annotations

import argparse
import filecmp
import shutil
from pathlib import Path

ROOT_FILES = [
    '.claude-plugin/marketplace.json',
    '.claude-plugin/plugin.json',
    '.github/ISSUE_TEMPLATE/bug_report.yml',
    '.github/ISSUE_TEMPLATE/config.yml',
    '.github/ISSUE_TEMPLATE/gallery_entry.yml',
    '.github/PULL_REQUEST_TEMPLATE.md',
    '.gitignore',
    'CHANGELOG.md',
    'CODE_OF_CONDUCT.md',
    'CONTRIBUTING.md',
    'LICENSE',
    'README.md',
    'README.zh.md',
    'SECURITY.md',
    'SUPPORT.md',
    'pyproject.toml',
    'src/gpt_image_cli/__init__.py',
    'src/gpt_image_cli/cli.py',
]

DIR_MAPPINGS = [
    ('docs', 'docs'),
    ('skills/gpt-image', 'skills/gpt-image-codex-hermes'),
]

EXCLUDED_DEST_FILES = {
    'README.md',
    'README.zh.md',
    'pyproject.toml',
    'src/gpt_image_cli/cli.py',
    'skills/gpt-image-codex-hermes/SKILL.md',
    'skills/gpt-image-codex-hermes/scripts/generate.py',
    '.github/workflows/sync-upstream.yml',
}

SPECIAL_FILE_MAP = {
    'README.md': 'README.upstream.md',
    'README.zh.md': 'README.upstream.zh.md',
}


def same_file(src: Path, dst: Path) -> bool:
    return dst.exists() and filecmp.cmp(src, dst, shallow=False)


def copy_file(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)


def should_skip_dest(path: Path, repo_root: Path) -> bool:
    rel = path.relative_to(repo_root).as_posix()
    return rel in EXCLUDED_DEST_FILES


def sync_root_files(source_root: Path, repo_root: Path) -> None:
    for rel in ROOT_FILES:
        src = source_root / rel
        if not src.exists():
            continue
        dest_rel = SPECIAL_FILE_MAP.get(rel, rel)
        dst = repo_root / dest_rel
        if should_skip_dest(dst, repo_root):
            continue
        if not same_file(src, dst):
            copy_file(src, dst)


def sync_directory(source_dir: Path, dest_dir: Path, repo_root: Path) -> None:
    if not source_dir.exists():
        return
    dest_dir.mkdir(parents=True, exist_ok=True)

    source_files: set[str] = set()
    for src in source_dir.rglob('*'):
        if src.is_dir():
            continue
        rel = src.relative_to(source_dir).as_posix()
        source_files.add(rel)
        dst = dest_dir / rel
        if should_skip_dest(dst, repo_root):
            continue
        if not same_file(src, dst):
            copy_file(src, dst)

    for dst in sorted(dest_dir.rglob('*'), reverse=True):
        if dst.is_dir():
            continue
        rel = dst.relative_to(dest_dir).as_posix()
        if rel not in source_files and not should_skip_dest(dst, repo_root):
            dst.unlink()

    for directory in sorted(dest_dir.rglob('*'), reverse=True):
        if directory.is_dir() and not any(directory.iterdir()):
            directory.rmdir()


def main() -> int:
    parser = argparse.ArgumentParser(description='Sync selected upstream files into the Hermes adaptation repo without overwriting custom files.')
    parser.add_argument('--source', required=True, help='Path to an upstream checkout.')
    parser.add_argument('--repo-root', default='.', help='Path to the local Hermes adaptation repository.')
    args = parser.parse_args()

    source_root = Path(args.source).resolve()
    repo_root = Path(args.repo_root).resolve()

    sync_root_files(source_root, repo_root)
    for src_rel, dst_rel in DIR_MAPPINGS:
        sync_directory(source_root / src_rel, repo_root / dst_rel, repo_root)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
