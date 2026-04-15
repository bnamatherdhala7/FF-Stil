"""
creative_tools.py — Stil editing tools
Five functions that simulate creative tool calls.
No real image processing — returns convincing JSON results.
"""

import json


def apply_filter(filename: str, filter_type: str) -> dict:
    """Apply a visual filter to an image."""
    valid_filters = ["warm", "cool", "vintage", "dramatic", "soft", "vivid", "bw"]
    if filter_type.lower() not in valid_filters:
        filter_type = "warm"
    return {
        "status": "ok",
        "action": f"applied {filter_type} filter",
        "file": filename,
        "filter": filter_type,
        "intensity": 75,
        "preview": f"assets/preview_{filename}"
    }


def adjust_brightness(filename: str, level: int) -> dict:
    """Adjust image brightness. Level: -100 (darker) to +100 (brighter)."""
    level = max(-100, min(100, int(level)))
    direction = "brightened" if level > 0 else "darkened"
    return {
        "status": "ok",
        "action": f"{direction} by {abs(level)}%",
        "file": filename,
        "brightness_delta": level,
        "new_brightness": 50 + level
    }


def crop_image(filename: str, ratio: str) -> dict:
    """Crop image to a standard ratio."""
    ratios = {
        "square": "1:1",
        "landscape": "16:9",
        "portrait": "4:5",
        "wide": "21:9",
        "instagram": "1:1",
        "story": "9:16"
    }
    canonical = ratios.get(ratio.lower(), ratio)
    return {
        "status": "ok",
        "action": f"cropped to {canonical}",
        "file": filename,
        "ratio": canonical,
        "dimensions": _get_dimensions(canonical)
    }


def set_export_preset(filename: str, platform: str) -> dict:
    """Set export settings optimised for a target platform."""
    presets = {
        "instagram": {"width": 1080, "height": 1080, "format": "jpg", "quality": 85, "colorspace": "sRGB"},
        "print":     {"width": 3000, "height": 3000, "format": "tiff", "quality": 100, "colorspace": "ProPhotoRGB"},
        "web":       {"width": 1200, "height": 630, "format": "jpg", "quality": 80, "colorspace": "sRGB"},
        "twitter":   {"width": 1200, "height": 675, "format": "jpg", "quality": 85, "colorspace": "sRGB"},
        "linkedin":  {"width": 1200, "height": 627, "format": "jpg", "quality": 85, "colorspace": "sRGB"},
    }
    preset = presets.get(platform.lower(), presets["web"])
    return {
        "status": "ok",
        "action": f"export preset applied for {platform}",
        "file": filename,
        "platform": platform,
        **preset,
        "estimated_size_kb": 250
    }


def list_layers(filename: str) -> dict:
    """List the layers in an image file."""
    return {
        "status": "ok",
        "file": filename,
        "layers": [
            {"name": "Background", "type": "pixel", "visible": True},
            {"name": "Color Grading", "type": "adjustment", "visible": True},
            {"name": "Crop Mask", "type": "mask", "visible": True},
            {"name": "Text Overlay", "type": "text", "visible": False},
        ],
        "layer_count": 4
    }


def _get_dimensions(ratio: str) -> dict:
    dim_map = {
        "1:1":  {"width": 1080, "height": 1080},
        "16:9": {"width": 1920, "height": 1080},
        "4:5":  {"width": 1080, "height": 1350},
        "9:16": {"width": 1080, "height": 1920},
        "21:9": {"width": 2560, "height": 1080},
    }
    return dim_map.get(ratio, {"width": 1080, "height": 1080})


TOOL_DEFINITIONS = [
    {
        "name": "apply_filter",
        "description": "Apply a visual filter to an image. Options: warm, cool, vintage, dramatic, soft, vivid, bw.",
        "input_schema": {
            "type": "object",
            "properties": {
                "filename": {"type": "string", "description": "Image filename"},
                "filter_type": {"type": "string", "description": "Filter name e.g. warm, cool, vintage"}
            },
            "required": ["filename", "filter_type"]
        }
    },
    {
        "name": "adjust_brightness",
        "description": "Adjust image brightness. Level from -100 (darker) to +100 (brighter).",
        "input_schema": {
            "type": "object",
            "properties": {
                "filename": {"type": "string", "description": "Image filename"},
                "level": {"type": "integer", "description": "Brightness adjustment -100 to +100"}
            },
            "required": ["filename", "level"]
        }
    },
    {
        "name": "crop_image",
        "description": "Crop image to a ratio. Options: square, landscape, portrait, instagram, story, wide.",
        "input_schema": {
            "type": "object",
            "properties": {
                "filename": {"type": "string", "description": "Image filename"},
                "ratio": {"type": "string", "description": "Crop ratio e.g. square, instagram, portrait"}
            },
            "required": ["filename", "ratio"]
        }
    },
    {
        "name": "set_export_preset",
        "description": "Set export settings for a platform. Options: instagram, print, web, twitter, linkedin.",
        "input_schema": {
            "type": "object",
            "properties": {
                "filename": {"type": "string", "description": "Image filename"},
                "platform": {"type": "string", "description": "Target platform e.g. instagram, print, web"}
            },
            "required": ["filename", "platform"]
        }
    },
    {
        "name": "list_layers",
        "description": "List all layers in an image file.",
        "input_schema": {
            "type": "object",
            "properties": {
                "filename": {"type": "string", "description": "Image filename"}
            },
            "required": ["filename"]
        }
    }
]


TOOL_MAP = {
    "apply_filter": apply_filter,
    "adjust_brightness": adjust_brightness,
    "crop_image": crop_image,
    "set_export_preset": set_export_preset,
    "list_layers": list_layers,
}


if __name__ == "__main__":
    print("--- creative_tools.py smoke test ---")
    print(json.dumps(apply_filter("portrait.jpg", "warm"), indent=2))
    print(json.dumps(crop_image("portrait.jpg", "square"), indent=2))
    print(json.dumps(set_export_preset("portrait.jpg", "instagram"), indent=2))
    print("All tools OK")
