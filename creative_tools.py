"""
creative_tools.py — Stil editing tools
Five functions that simulate creative tool calls, plus PIL-based preview rendering.
"""

import json
import io
from PIL import Image, ImageEnhance, ImageFilter


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


def adjust_contrast(filename: str, level: int) -> dict:
    """Adjust image contrast. Level: -100 (flat) to +100 (high contrast)."""
    level = max(-100, min(100, int(level)))
    direction = "increased" if level > 0 else "decreased"
    return {
        "status": "ok",
        "action": f"contrast {direction} by {abs(level)}%",
        "file": filename,
        "contrast_delta": level,
        "new_contrast": 50 + level
    }


def crop_image(filename: str, ratio: str) -> dict:
    """Crop image to a standard ratio."""
    ratios = {
        "square": "1:1",
        "landscape": "16:9",
        "portrait": "4:5",
        "wide": "21:9",
        "instagram": "1:1",
        "story": "9:16",
        "tiktok": "9:16",
        "reels": "9:16",
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
        "tiktok":    {"width": 1080, "height": 1920, "format": "jpg", "quality": 85, "colorspace": "sRGB"},
        "reels":     {"width": 1080, "height": 1920, "format": "jpg", "quality": 85, "colorspace": "sRGB"},
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


def preview_edits(image_bytes: bytes, tool_trace: list) -> bytes | None:
    """
    Apply visual edits from tool_trace to image_bytes using Pillow.
    Returns JPEG bytes of the edited image, or None if no visual edits were applied.
    """
    visual_tools = {"apply_filter", "adjust_brightness", "adjust_contrast", "crop_image"}
    if not any(t.get("tool") in visual_tools for t in tool_trace):
        return None

    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")

    for call in tool_trace:
        tool = call.get("tool", "")
        inp = call.get("input", {})

        if tool == "apply_filter":
            img = _apply_pil_filter(img, inp.get("filter_type", "warm"))
        elif tool == "adjust_brightness":
            level = inp.get("level", 0)
            factor = 1.0 + (level / 200.0)  # -100→0.5x, 0→1.0x, +100→1.5x
            img = ImageEnhance.Brightness(img).enhance(max(0.1, factor))
        elif tool == "adjust_contrast":
            level = inp.get("level", 0)
            factor = 1.0 + (level / 150.0)
            img = ImageEnhance.Contrast(img).enhance(max(0.1, factor))
        elif tool == "crop_image":
            img = _apply_pil_crop(img, inp.get("ratio", "square"))

    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=85)
    return buf.getvalue()


def _apply_pil_filter(img: Image.Image, filter_type: str) -> Image.Image:
    ft = filter_type.lower()
    if ft == "bw":
        return img.convert("L").convert("RGB")
    if ft == "warm":
        r, g, b = img.split()
        r = r.point(lambda i: min(255, int(i * 1.15)))
        b = b.point(lambda i: int(i * 0.85))
        return Image.merge("RGB", (r, g, b))
    if ft == "cool":
        r, g, b = img.split()
        r = r.point(lambda i: int(i * 0.85))
        b = b.point(lambda i: min(255, int(i * 1.15)))
        return Image.merge("RGB", (r, g, b))
    if ft == "vintage":
        img = ImageEnhance.Color(img).enhance(0.65)
        r, g, b = img.split()
        r = r.point(lambda i: min(255, int(i * 1.1)))
        b = b.point(lambda i: int(i * 0.8))
        return Image.merge("RGB", (r, g, b))
    if ft == "dramatic":
        img = ImageEnhance.Contrast(img).enhance(1.5)
        return ImageEnhance.Color(img).enhance(1.2)
    if ft == "soft":
        img = img.filter(ImageFilter.GaussianBlur(radius=1))
        return ImageEnhance.Contrast(img).enhance(0.9)
    if ft == "vivid":
        img = ImageEnhance.Color(img).enhance(1.5)
        return ImageEnhance.Contrast(img).enhance(1.15)
    return img


def _apply_pil_crop(img: Image.Image, ratio: str) -> Image.Image:
    ratios = {
        "square": (1, 1), "instagram": (1, 1),
        "landscape": (16, 9), "wide": (21, 9),
        "portrait": (4, 5), "story": (9, 16), "tiktok": (9, 16), "reels": (9, 16),
        "1:1": (1, 1), "16:9": (16, 9), "4:5": (4, 5), "9:16": (9, 16), "21:9": (21, 9),
    }
    tw, th = ratios.get(ratio.lower(), (1, 1))
    w, h = img.size
    target_ar = tw / th
    current_ar = w / h
    if current_ar > target_ar:
        new_w = int(h * target_ar)
        left = (w - new_w) // 2
        img = img.crop((left, 0, left + new_w, h))
    else:
        new_h = int(w / target_ar)
        top = (h - new_h) // 2
        img = img.crop((0, top, w, top + new_h))
    return img


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
        "name": "adjust_contrast",
        "description": "Adjust image contrast. Level from -100 (flat/low contrast) to +100 (high contrast).",
        "input_schema": {
            "type": "object",
            "properties": {
                "filename": {"type": "string", "description": "Image filename"},
                "level": {"type": "integer", "description": "Contrast adjustment -100 to +100"}
            },
            "required": ["filename", "level"]
        }
    },
    {
        "name": "crop_image",
        "description": "Crop image to a ratio. Options: square, landscape, portrait, instagram, story, tiktok, reels, wide.",
        "input_schema": {
            "type": "object",
            "properties": {
                "filename": {"type": "string", "description": "Image filename"},
                "ratio": {"type": "string", "description": "Crop ratio e.g. square, instagram, portrait, tiktok"}
            },
            "required": ["filename", "ratio"]
        }
    },
    {
        "name": "set_export_preset",
        "description": "Set export settings for a platform. Options: instagram, tiktok, reels, print, web, twitter, linkedin.",
        "input_schema": {
            "type": "object",
            "properties": {
                "filename": {"type": "string", "description": "Image filename"},
                "platform": {"type": "string", "description": "Target platform e.g. instagram, tiktok, print, web"}
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
    "adjust_contrast": adjust_contrast,
    "crop_image": crop_image,
    "set_export_preset": set_export_preset,
    "list_layers": list_layers,
}


if __name__ == "__main__":
    print("--- creative_tools.py smoke test ---")
    print(json.dumps(apply_filter("portrait.jpg", "warm"), indent=2))
    print(json.dumps(adjust_contrast("portrait.jpg", 30), indent=2))
    print(json.dumps(crop_image("portrait.jpg", "tiktok"), indent=2))
    print(json.dumps(set_export_preset("portrait.jpg", "tiktok"), indent=2))
    print("All tools OK")
