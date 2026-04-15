"""
asset_library.py — Stil asset search server
Exposes 4 tools: list_assets, inspect_asset, tag_asset, find_asset.
Run standalone: python asset_library.py
"""

import json
import os
from dotenv import load_dotenv
import anthropic
from mcp.server.fastmcp import FastMCP

load_dotenv()

ASSETS_DIR = "assets"
TAGS_CACHE = os.path.join(ASSETS_DIR, "tags.json")
MODEL = "claude-haiku-4-5"

mcp = FastMCP("FF Creative Assets")
client = anthropic.Anthropic()


def _load_tags() -> dict:
    if os.path.exists(TAGS_CACHE):
        with open(TAGS_CACHE, "r") as f:
            return json.load(f)
    return {}


def _save_tags(tags: dict):
    os.makedirs(ASSETS_DIR, exist_ok=True)
    with open(TAGS_CACHE, "w") as f:
        json.dump(tags, f, indent=2)


def _fake_metadata(filename: str) -> dict:
    """Generate plausible metadata from filename."""
    name = filename.lower()
    contrast = "high" if any(w in name for w in ["dark", "contrast", "bw", "dramatic", "moody"]) else "medium"
    brightness = "bright" if any(w in name for w in ["bright", "golden", "warm", "white"]) else "dark" if any(w in name for w in ["dark", "moody", "bw"]) else "medium"
    tone = "warm" if any(w in name for w in ["warm", "golden"]) else "cool" if any(w in name for w in ["cool", "blue"]) else "neutral"
    return {
        "filename": filename,
        "dimensions": "3000x2000",
        "file_size_mb": round(2.1 + hash(filename) % 50 / 10, 1),
        "format": filename.split(".")[-1].upper(),
        "contrast": contrast,
        "brightness": brightness,
        "tone": tone,
        "has_people": "portrait" in name,
        "suitable_for": _guess_use_case(name)
    }


def _guess_use_case(name: str) -> list:
    uses = []
    if any(w in name for w in ["bg", "background", "abstract"]):
        uses.append("background")
    if "portrait" in name:
        uses.append("portrait")
    if any(w in name for w in ["flat_lay", "desk", "product"]):
        uses.append("product")
    if any(w in name for w in ["social", "instagram"]):
        uses.append("social_media")
    if not uses:
        uses.append("general")
    return uses


@mcp.tool()
def list_assets() -> dict:
    """List all creative assets available in the assets folder."""
    os.makedirs(ASSETS_DIR, exist_ok=True)
    files = [
        f for f in os.listdir(ASSETS_DIR)
        if f.lower().endswith((".jpg", ".jpeg", ".png", ".webp"))
    ]
    return {
        "status": "ok",
        "count": len(files),
        "assets": files
    }


@mcp.tool()
def inspect_asset(filename: str) -> dict:
    """Get metadata and properties of a specific asset."""
    filepath = os.path.join(ASSETS_DIR, filename)
    if not os.path.exists(filepath):
        return {"status": "error", "message": f"{filename} not found in assets/"}
    return {"status": "ok", **_fake_metadata(filename)}


@mcp.tool()
def tag_asset(filename: str) -> dict:
    """Generate and cache descriptive tags for an asset using AI."""
    tags_cache = _load_tags()
    if filename in tags_cache:
        return {"status": "ok", "filename": filename, "tags": tags_cache[filename], "cached": True}

    filepath = os.path.join(ASSETS_DIR, filename)
    if not os.path.exists(filepath):
        return {"status": "error", "message": f"{filename} not found"}

    prompt = f"""Generate exactly 5 short descriptive tags for a photo named: {filename}
Return ONLY a JSON array of 5 strings, no other text. Example: ["warm", "portrait", "natural light", "soft", "outdoor"]
Tags should describe: mood, lighting, subject, use case, and visual style."""

    response = client.messages.create(
        model=MODEL,
        max_tokens=100,
        messages=[{"role": "user", "content": prompt}]
    )

    try:
        raw = response.content[0].text.strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        tags = json.loads(raw.strip())
    except Exception:
        tags = filename.replace(".jpg", "").replace("_", " ").split()[:5]

    tags_cache[filename] = tags
    _save_tags(tags_cache)
    return {"status": "ok", "filename": filename, "tags": tags, "cached": False}


@mcp.tool()
def find_asset(prompt: str) -> dict:
    """Find the best matching asset for a creative brief using keyword matching."""
    tags_cache = _load_tags()
    assets = list_assets().get("assets", [])

    if not assets:
        return {"status": "error", "message": "No assets found in assets/ folder"}

    prompt_words = set(prompt.lower().replace(",", " ").split())
    scores = []

    for filename in assets:
        score = 0
        name_words = set(filename.lower().replace("_", " ").replace(".", " ").split())
        score += len(prompt_words & name_words) * 2

        if filename in tags_cache:
            tag_words = set(" ".join(tags_cache[filename]).lower().split())
            score += len(prompt_words & tag_words)

        meta = _fake_metadata(filename)
        if "contrast" in prompt.lower() and meta["contrast"] == "high":
            score += 3
        if "bright" in prompt.lower() and meta["brightness"] == "bright":
            score += 2
        if "dark" in prompt.lower() and meta["brightness"] == "dark":
            score += 2
        if "warm" in prompt.lower() and meta["tone"] == "warm":
            score += 2
        if "background" in prompt.lower() and "background" in meta.get("suitable_for", []):
            score += 3

        scores.append((filename, score, tags_cache.get(filename, [])))

    scores.sort(key=lambda x: x[1], reverse=True)
    top = scores[:3]

    return {
        "status": "ok",
        "prompt": prompt,
        "results": [
            {
                "rank": i + 1,
                "filename": fname,
                "score": score,
                "tags": tags,
                "rationale": _generate_rationale(fname, prompt)
            }
            for i, (fname, score, tags) in enumerate(top)
        ]
    }


def _generate_rationale(filename: str, prompt: str) -> str:
    name = filename.replace("_", " ").replace(".jpg", "").replace(".png", "")
    meta = _fake_metadata(filename)
    return (f"{name} — {meta['contrast']} contrast, {meta['brightness']} brightness, "
            f"{meta['tone']} tones. Suitable for: {', '.join(meta['suitable_for'])}.")


if __name__ == "__main__":
    print("Starting FF Creative Assets MCP server...")
    mcp.run()
