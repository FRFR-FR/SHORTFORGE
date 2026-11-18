#!/usr/bin/env python3
"""Fetch complete prebuilt Blender environments and textured CC0 humanoid assets."""
from __future__ import annotations
import argparse
import hashlib
import json
import subprocess
import time
import urllib.request
from pathlib import Path
from urllib.parse import quote

PIN = "82ca30efa7677af995bd2c6673788e1cb924b3c5"
QUATERNIUS_BASE = f"https://raw.githubusercontent.com/chrisakira/Open/{PIN}/assets/characters/quaternius/"

ENVIRONMENTS = {
    "dogwalk": {
        "url": "https://mirror.blender.org/demo/splash/blender-4.5-splash.blend",
        "minimum_bytes": 300_000_000,
        "source": "Blender Studio official demo files — DOGWALK (Blender 4.5)",
        "license": "CC-BY-SA (conservative splash-art interpretation)",
        "license_url": "https://creativecommons.org/licenses/by-sa/4.0/",
        "source_page": "https://www.blender.org/download/releases/4-5/",
        "attribution": "Blender Foundation / Blender Studio — DOGWALK splash artwork; share-alike terms apply.",
        "notes": "Prebuilt Blender splash environment. Derived artwork must follow the applicable share-alike terms.",
    },
    "house_of_chores": {
        "url": "https://mirror.blender.org/demo/splash/blender-4.3-splash.blend",
        "minimum_bytes": 200_000_000,
        "source": "Blender Studio official Blender demo files — House of Chores (Blender 4.3)",
        "license": "CC-BY (official Blender Demo Files listing; preserve creator credit)",
        "license_url": "https://www.blender.org/download/demo-files/",
        "source_page": "https://www.blender.org/download/demo-files/",
        "attribution": "Blender Studio — House of Chores (credit per official Blender Demo Files page).",
        "notes": "Complete prebuilt Blender interior scene, downloaded directly from the official Blender mirror.",
    },
}

AVATARS = {
    "male": {
        "model": "Superhero_Male_FullBody.gltf",
        "license": "CC0-1.0",
        "license_url": "https://creativecommons.org/publicdomain/zero/1.0/",
        "source_page": "https://quaternius.com/packs/universalbasecharacters.html",
        "attribution": "Quaternius — Universal Base Characters Standard, CC0 1.0.",
        "source": "Quaternius Universal Base Characters Standard; pinned source glTF and PBR textures.",
    },
    "female": {
        "model": "Superhero_Female_FullBody.gltf",
        "license": "CC0-1.0",
        "license_url": "https://creativecommons.org/publicdomain/zero/1.0/",
        "source_page": "https://quaternius.com/packs/universalbasecharacters.html",
        "attribution": "Quaternius — Universal Base Characters Standard, CC0 1.0.",
        "source": "Quaternius Universal Base Characters Standard; pinned source glTF and PBR textures.",
    },
}

def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()

def download(url: str, target: Path, minimum_bytes: int, magic: bytes = b"", retries: int = 3) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists() and target.stat().st_size >= minimum_bytes:
        if not magic or target.open("rb").read(len(magic)) == magic:
            return
    target.unlink(missing_ok=True)
    partial = target.with_suffix(target.suffix + ".part")
    last_error = None
    for attempt in range(1, retries + 1):
        try:
            request = urllib.request.Request(url, headers={"User-Agent": "SHORTFORGE-asset-fetcher/2.0"})
            with urllib.request.urlopen(request, timeout=120) as response, partial.open("wb") as out:
                status = getattr(response, "status", 200)
                if status != 200:
                    raise RuntimeError(f"HTTP {status} from {url}")
                while True:
                    chunk = response.read(1024 * 1024)
                    if not chunk:
                        break
                    out.write(chunk)
            # Some Blender mirrors now return a Zstandard-compressed payload.
            # Decode it before applying the .blend signature and minimum-size checks.
            with partial.open("rb") as stream:
                prefix = stream.read(4 if magic else 0)
            if magic and prefix == b"\x28\xb5\x2f\xfd":
                decoded = partial.with_name(partial.name + ".decoded")
                try:
                    with decoded.open("wb") as out:
                        subprocess.run(
                            ["zstd", "--quiet", "--decompress", "--stdout", str(partial)],
                            stdout=out,
                            stderr=subprocess.PIPE,
                            check=True,
                            text=False,
                        )
                except FileNotFoundError as exc:
                    raise RuntimeError(
                        "The downloaded asset is Zstandard-compressed, but the 'zstd' "
                        "decoder is not installed. Install the system package 'zstd'."
                    ) from exc
                except subprocess.CalledProcessError as exc:
                    detail = exc.stderr.decode("utf-8", errors="replace")[-1200:]
                    decoded.unlink(missing_ok=True)
                    raise RuntimeError(f"Unable to decompress Zstandard asset: {detail}") from exc
                decoded.replace(partial)

            size = partial.stat().st_size
            with partial.open("rb") as stream:
                prefix = stream.read(len(magic)) if magic else b""
            if size < minimum_bytes:
                raise RuntimeError(f"Downloaded only {size:,} bytes after decompression; expected at least {minimum_bytes:,}")
            if magic and prefix != magic:
                raise RuntimeError(f"Downloaded file has invalid signature after decompression: {prefix!r}")
            partial.replace(target)
            return
        except Exception as exc:
            last_error = exc
            partial.unlink(missing_ok=True)
            if attempt < retries:
                time.sleep(2 * attempt)
    raise RuntimeError(f"Unable to obtain asset from {url}: {last_error}") from last_error

def fetch_avatar(gender: str, info: dict, cache: Path) -> dict:
    folder = cache / "avatars" / f"quaternius-{gender}"
    model_path = folder / info["model"]
    model_url = QUATERNIUS_BASE + quote(info["model"])
    download(model_url, model_path, 20_000, b"{")
    gltf = json.loads(model_path.read_text(encoding="utf-8"))
    if gltf.get("asset", {}).get("version") != "2.0":
        raise RuntimeError(f"{model_path} is not a valid glTF 2.0 model")
    if len(gltf.get("skins", [{}])[0].get("joints", [])) < 60:
        raise RuntimeError(f"{model_path} did not contain the expected articulated humanoid rig")
    resources = [{"uri": buffer["uri"], "minimum_bytes": 100_000, "magic": b""} for buffer in gltf.get("buffers", [])]
    resources += [{"uri": image["uri"], "minimum_bytes": 1_000, "magic": b"\x89PNG\r\n\x1a\n"} for image in gltf.get("images", []) if image.get("uri")]
    files = []
    for resource in resources:
        name = Path(resource["uri"]).name
        path = folder / name
        url = QUATERNIUS_BASE + quote(name)
        download(url, path, resource["minimum_bytes"], resource["magic"])
        files.append({"file": name, "bytes": path.stat().st_size, "sha256": sha256(path), "url": url})
    return {
        "path": str(model_path),
        "bytes": model_path.stat().st_size,
        "sha256": sha256(model_path),
        "rig_joints": len(gltf["skins"][0]["joints"]),
        "mesh_names": [mesh.get("name", f"mesh-{i}") for i, mesh in enumerate(gltf.get("meshes", []))],
        "pbr_materials": [material.get("name", f"material-{i}") for i, material in enumerate(gltf.get("materials", []))],
        "resources": files,
        **info,
    }

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", required=True)
    parser.add_argument("--cache-dir", default=".cache/shortforge-assets")
    parser.add_argument("--output-manifest", required=True)
    args = parser.parse_args()
    project = json.loads(Path(args.project).read_text(encoding="utf-8"))
    cache = Path(args.cache_dir).resolve()
    output = Path(args.output_manifest).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)

    environment_id = project.get("environment", {}).get("id", "house_of_chores")
    if environment_id not in ENVIRONMENTS:
        raise SystemExit(f"Unknown environment {environment_id!r}; available: {', '.join(ENVIRONMENTS)}")
    env_info = ENVIRONMENTS[environment_id]
    env_path = cache / "environments" / f"{environment_id}.blend"
    download(env_info["url"], env_path, env_info["minimum_bytes"], b"BLENDER")

    avatar_files = {gender: fetch_avatar(gender, info, cache) for gender, info in AVATARS.items()}
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
            "mesh": "Quaternius Standard textured source mesh with PBR skin, hair, eye, normal and roughness maps",
            "emotions": ["neutral", "happy", "sad", "angry", "surprised", "scared", "determined"],
            "poses": ["neutral", "wave", "point", "confident", "thinking", "celebrating", "running", "crouching"],
        },
        "cached_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    output.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(json.dumps({
        "environment": {k: manifest["environment"][k] for k in ("id", "bytes", "sha256", "license", "attribution")},
        "avatars": {name: {k: entry[k] for k in ("bytes", "sha256", "rig_joints", "pbr_materials", "resources")} for name, entry in avatar_files.items()},
    }, indent=2))

if __name__ == "__main__":
    main()
