#!/usr/bin/env python3
"""Ingest calendar JSON files from the calendar-bharat GitHub repo.

This script tries to `git clone` the repo into a temporary directory and copy
all `.json` files into the project's `data/calendar-events` folder. If `git`
is not available or cloning fails, it falls back to downloading raw files via
GitHub's raw URLs using `urllib`.

Usage:
    python src/data_collection/ingest_calendar.py

The script creates `data/calendar-events` if it doesn't exist and preserves
filenames. If multiple files share the same name, path components are
prefixed to avoid collisions.
"""
import os
import shutil
import subprocess
import tempfile
import urllib.request
from pathlib import Path

GIT_REPO = "https://github.com/jayantur13/calendar-bharat.git"
RAW_BASE = "https://raw.githubusercontent.com/jayantur13/calendar-bharat/main"


def clone_repo(tmp_dir: str) -> bool:
    try:
        subprocess.run(["git", "clone", "--depth", "1", GIT_REPO, tmp_dir], check=True)
        return True
    except Exception:
        return False


def copy_jsons_from_dir(src_dir: str, dest_dir: str) -> int:
    saved = 0
    for root, _, files in os.walk(src_dir):
        for f in files:
            if f.lower().endswith('.json'):
                rel_dir = os.path.relpath(root, src_dir)
                if rel_dir == '.':
                    out_name = f
                else:
                    # prefix path parts to avoid collisions
                    safe_prefix = rel_dir.replace(os.sep, "-")
                    out_name = f"{safe_prefix}-{f}"
                src_path = os.path.join(root, f)
                dest_path = os.path.join(dest_dir, out_name)
                shutil.copyfile(src_path, dest_path)
                saved += 1
    return saved


def list_json_files_via_api() -> list:
    # Use the GitHub tree API to list files. If it fails, return empty list.
    import json
    try:
        api_url = "https://api.github.com/repos/jayantur13/calendar-bharat/git/trees/main?recursive=1"
        with urllib.request.urlopen(api_url) as resp:
            data = json.load(resp)
        paths = [item['path'] for item in data.get('tree', []) if item['path'].lower().endswith('.json')]
        return paths
    except Exception:
        return []


def download_raw(path: str, dest_path: str) -> bool:
    url = f"{RAW_BASE}/{path}"
    try:
        with urllib.request.urlopen(url) as resp, open(dest_path, 'wb') as out:
            out.write(resp.read())
        return True
    except Exception:
        return False


def download_jsons_via_raw(paths: list, dest_dir: str) -> int:
    saved = 0
    for path in paths:
        fname = os.path.basename(path)
        prefix = os.path.dirname(path).replace('/', '-')
        out_name = f"{prefix}-{fname}" if prefix else fname
        dest_path = os.path.join(dest_dir, out_name)
        if download_raw(path, dest_path):
            saved += 1
    return saved


def ensure_dest_dir() -> str:
    dest = os.path.join(os.getcwd(), 'data', 'calendar-events')
    os.makedirs(dest, exist_ok=True)
    return dest


def main():
    dest = ensure_dest_dir()
    tmp_dir = tempfile.mkdtemp(prefix='calendar-bharat-')
    try:
        cloned = clone_repo(tmp_dir)
        if cloned:
            print(f"Cloned repo into {tmp_dir}, collecting JSON files...")
            count = copy_jsons_from_dir(tmp_dir, dest)
            print(f"Copied {count} JSON files to {dest}")
            return

        # Fallback to GitHub API + raw downloads
        print("Git clone failed; falling back to GitHub API/raw downloads...")
        paths = list_json_files_via_api()
        if not paths:
            print("No JSON files found via API or API failed.")
            return
        count = download_jsons_via_raw(paths, dest)
        print(f"Downloaded {count} JSON files to {dest}")

    finally:
        try:
            shutil.rmtree(tmp_dir)
        except Exception:
            pass


if __name__ == '__main__':
    main()
