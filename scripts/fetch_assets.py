#!/usr/bin/env python3
"""Fetch verified, reusable, properly licensed SHORTFORGE assets."""
from __future__ import annotations
import argparse
import hashlib
import json
import os
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PIN = "c70e098e4661beffab4e4a7912458285b73d1aaf"

ENVIRONMENTS = {
    "dogwalk": {
        "url": "https://mirror.blender.org/demo/splash/blender-4.5-splash.blend",
        "minimum_bytes": 300_000_000,
        "source": "Blender Studio official Blender demo files — DOGWALK (Blender 4.5)",
        "license": "CC-BY",
        "license_url": "https://creativecommons.org/licenses/by/4.0/",
        "source_page": "https://www.blender.org/download/demo-files/",
        "attribution": "Blender Studio — DOGWALK, licensed under CC BY 4.0",
        "notes": "Full prebuilt Blender scene. Keep the source attribution with redistributed renders and project files.",
    },
    "house_of_chores": {
        "url": "https://mirror.blender.org/demo/splash/blender-4.3-splash.blend",
        "minimum_bytes": 200_000_000,
        "source": "Blender Studio official Blender demo files — House of Chores (Blender 4.3)",
        "license": "CC-BY",
        "license_url": "https://creativecommons.org/licenses/by/4.0/",
        "source_page": "https://www.blender.org/download/demo-files/",
        "attribution": "Blender Studio — House of Chores, licensed under CC BY 4.0",
        "notes": "Full prebuilt Blender scene. Intended for an interior-set story. Use Blender 4.5 to open and convert when required.",
    },
}

AVATARS = {
    "male": {
        "url": f"https://raw.githubusercontent.com/glanderness/BeefTV/{PIN}/web/public/canvas/models/quaternius-standard-male.glb",
        "license_url": "https://creativecommons.org/publicdomain/zero/1.0/",
        "source_page": "https://quaternius.com/packs/universalbasecharacters.html",
        "attribution": "Quaternius — Universal Base Characters Standard, CC0 1.0",
        "source": f"Quaternius Universal Base Characters Standard, pinned community conversion at {PIN}",
    },
    "female": {
        "url": f"https://raw.githubusercontent.com/glanderness/BeefTV/{PIN}/web/public/canvas/models/quaternius-standard-female.glb",
        "license_url": "https://creativecommons.org/publicdomain/zero/1.0/",
        "source_page": "https://quaternius.com/packs/universalbasecharacters.html",
        "attribution": "Quaternius — Universal Base Characters Standard, CC0 1.0",
        "source": f"Quaternius Universal Base Characters Standard, pinned community conversion at {PIN}",
    },
}

def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()

def download(url: str, target: Path, minimum_bytes: int, magic: bytes, retries: int = 3) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists() and target.stat().st_size >= minimum_bytes and target.open("rb").read(len(magic)) == magic:
        return
    target.unlink(missing_ok=True)
    partial = target.with_suffix(target.suffix + ".part")
    last_error = None
    for attempt in range(1, retries + 1):
        try:
            request = urllib.request.Request(url, headers={"User-Agent": "SHORTFORGE-asset-fetcher/1.0"})
            with urllib.request.urlopen(request, timeout=90) as response, partial.open("wb") as out:
                status = getattr(response, "status", 200)
                if status != 200:
                    raise RuntimeError(f"HTTP {status} from {url}")
                while True:
                    chunk = response.read(1024 * 1024)
                    if not chunk:
                        break
                    out.write(chunk)
                    out.flush()
            size = partial.stat().st_size
            with partial.open("rb") as stream:
                prefix = stream.read(len(magic))
            if size < minimum_bytes:
                raise RuntimeError(f"Downloaded only {size:,} bytes; expected at least {minimum_bytes:,}")
            if prefix != magic:
                raise RuntimeError(f"Downloaded file has invalid signature: {prefix!r}")
            partial.replace(target)
            return
        except Exception as exc:
            last_error = exc
            partial.unlink(missing_ok=True)
            if attempt < retries:
                time.sleep(2 * attempt)
    raise RuntimeError(f"Unable to obtain licensed asset from {url}: {last_error}") from last_error

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", required=True)
    parser.add_argument("--cache-dir", default=str(ROOT / ".cache/shortforge-assets"))
    parser.add_argument("--output-manifest", required=True)
    args = parser.parse_args()
    project = json.loads(Path(args.project).read_text(encoding="utf-8"))
    cache = Path(args.cache_dir).resolve()
    output = Path(args.output_manifest).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)

    environment_id = project.get("environment", {}).get("id", "dogwalk")
    if environment_id not in ENVIRONMENTS:
        raise SystemExit(f"Unknown environment {environment_id!r}; available: {', '.join(ENVIRONMENTS)}")
    env_info = ENVIRONMENTS[environment_id]
    env_path = cache / "environments" / f"{environment_id}.blend"
    download(env_info["url"], env_path, env_info["minimum_bytes"], b"BLENDER")

    avatar_files = {}
    for gender, info in AVATARS.items():
        path = cache / "avatars" / f"quaternius-standard-{gender}.glb"
        download(info["url"], path, 500_000, b"glTF")
        avatar_files[gender] = {
            "path": str(path),
            "bytes": path.stat().st_size,
            "sha256": sha256(path),
            **info,
        }

    manifest = {
        "environment": {
            "id": environment_id,
            "path": str(env_path),
            "bytes": env_path.stat().st_size,
            "sha256": sha256(env_path),
            **env_info,
        },
        "avatars": avatar_files,
        "avatar_system": {
            "rig": "65-joint humanoid skeleton",
            "emotions": ["neutral", "happy", "sad", "angry", "surprised", "scared", "determined"],
            "poses": ["neutral", "wave", "point", "confident", "thinking", "celebrating", "running", "crouching"],
        },
        "cached_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    output.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(json.dumps({
        "environment": {k: manifest["environment"][k] for k in ("id", "bytes", "sha256", "license", "attribution")},
        "avatars": {name: {k: entry[k] for k in ("bytes", "sha256", "license_url")} for name, entry in avatar_files.items()},
    }, indent=2))

if __name__ == "__main__":
    main()
