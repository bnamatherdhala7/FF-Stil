"""
feed_analyzer.py — Feed consistency analysis and style transfer.
All Pillow-based. Zero API calls. $0 cost.
"""

import io
import colorsys
from PIL import Image, ImageStat


def _pil_metrics(image_bytes: bytes) -> dict:
    """Extract visual style metrics from a single image."""
    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    img_small = img.resize((100, 100), Image.LANCZOS)

    r_ch, _, b_ch = img_small.split()
    r_mean = ImageStat.Stat(r_ch).mean[0]
    b_mean = ImageStat.Stat(b_ch).mean[0]
    color_temp = r_mean / max(b_mean, 1.0)  # >1.2 = warm, <0.8 = cool

    l_img = img_small.convert("L")
    brightness = ImageStat.Stat(l_img).mean[0]
    contrast = ImageStat.Stat(l_img).stddev[0]

    hsv_pixels = [
        colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
        for r, g, b in img_small.getdata()
    ]
    saturation = sum(p[1] for p in hsv_pixels) / len(hsv_pixels)

    return {
        "color_temp": round(color_temp, 3),
        "brightness": round(brightness, 1),
        "contrast": round(contrast, 1),
        "saturation": round(saturation, 3),
    }


def score_cohesion(metrics_list: list) -> dict:
    """
    Compute a feed cohesion score (0–100) from per-image metrics.
    Higher = more consistent feed.
    """
    if len(metrics_list) < 2:
        return {"score": 100, "issues": [], "dimension_scores": {}}

    def variance(values):
        mean = sum(values) / len(values)
        return sum((v - mean) ** 2 for v in values) / len(values)

    temps = [m["color_temp"] for m in metrics_list]
    brights = [m["brightness"] for m in metrics_list]
    contrasts = [m["contrast"] for m in metrics_list]
    sats = [m["saturation"] for m in metrics_list]

    # Normalize each variance against the expected maximum for that dimension
    temp_norm = min(variance(temps) / 0.30, 1.0)
    bright_norm = min(variance(brights) / 1500.0, 1.0)
    contrast_norm = min(variance(contrasts) / 500.0, 1.0)
    sat_norm = min(variance(sats) / 0.05, 1.0)

    # Weighted penalty — color temp and brightness matter most for visual cohesion
    penalty = (
        temp_norm * 0.35 +
        bright_norm * 0.25 +
        contrast_norm * 0.25 +
        sat_norm * 0.15
    )
    score = max(0, round(100 - (penalty * 100)))

    THRESHOLDS = {
        "color_temp": 0.25,
        "brightness": 0.35,
        "contrast": 0.35,
        "saturation": 0.30,
    }
    norms = {
        "color_temp": temp_norm,
        "brightness": bright_norm,
        "contrast": contrast_norm,
        "saturation": sat_norm,
    }
    MESSAGES = {
        "color_temp": "Color temperature varies — some photos read warm, others cool",
        "brightness": "Brightness is inconsistent across your feed",
        "contrast": "Contrast levels differ — high-contrast and flat photos are mixed",
        "saturation": "Saturation varies — some vivid, others muted",
    }
    issues = [MESSAGES[dim] for dim, norm in norms.items() if norm > THRESHOLDS[dim]]

    return {
        "score": score,
        "issues": issues,
        "dimension_scores": {
            "Color temp": round((1 - temp_norm) * 100),
            "Brightness": round((1 - bright_norm) * 100),
            "Contrast": round((1 - contrast_norm) * 100),
            "Saturation": round((1 - sat_norm) * 100),
        },
    }


def analyze_feed(image_bytes_list: list, filenames: list = None) -> dict:
    """
    Full feed analysis: per-image metrics → cohesion score → issues → suggested fix.
    """
    if not image_bytes_list:
        return {"error": "No images provided"}

    metrics_list = [_pil_metrics(b) for b in image_bytes_list]
    cohesion = score_cohesion(metrics_list)

    dim_scores = cohesion.get("dimension_scores", {})
    lowest_dim = min(dim_scores, key=dim_scores.get) if dim_scores else None

    FIX_SUGGESTIONS = {
        "Color temp": "Apply a consistent warm or cool filter to every photo",
        "Brightness": "Set a uniform brightness target — aim for ±10 range across the feed",
        "Contrast": "Lock one contrast level (e.g. +30) and apply it to all photos",
        "Saturation": "Choose vivid (1.4×) or muted (0.8×) and apply it consistently",
    }
    suggested_fix = FIX_SUGGESTIONS.get(lowest_dim, "") if lowest_dim else ""

    return {
        "score": cohesion["score"],
        "issues": cohesion["issues"],
        "dimension_scores": cohesion["dimension_scores"],
        "suggested_fix": suggested_fix,
        "per_image_metrics": [
            {
                "filename": (filenames[i] if filenames and i < len(filenames) else f"Image {i+1}"),
                **m,
            }
            for i, m in enumerate(metrics_list)
        ],
    }


def extract_reference_style(image_bytes: bytes) -> dict:
    """
    Read the visual style from a reference image.
    Returns filter, brightness delta, contrast delta, tone, and a description.
    Pure Pillow — no API calls.
    """
    m = _pil_metrics(image_bytes)
    ct, sat, bright, contrast = m["color_temp"], m["saturation"], m["brightness"], m["contrast"]

    if sat < 0.12:
        filter_type = "bw"
    elif ct > 1.30 and sat > 0.28:
        filter_type = "warm"
    elif ct < 0.85:
        filter_type = "cool"
    elif sat < 0.22:
        filter_type = "vintage"
    elif contrast > 55:
        filter_type = "dramatic"
    elif sat > 0.50:
        filter_type = "vivid"
    else:
        filter_type = "soft"

    brightness_delta = int(max(-60, min(60, (bright - 128) * 0.5)))
    contrast_delta = int(max(-60, min(60, (contrast - 40) * 0.8)))
    tone = "warm" if ct > 1.15 else ("cool" if ct < 0.90 else "neutral")

    DESCRIPTIONS = {
        "bw": "black and white, desaturated tones",
        "warm": "warm golden tones with boosted reds",
        "cool": "cool blue-tinted aesthetic",
        "vintage": "faded vintage warmth with muted colors",
        "dramatic": "high contrast, bold and punchy",
        "vivid": "vibrant, highly saturated look",
        "soft": "soft, gentle tones with reduced contrast",
    }

    return {
        "filter_type": filter_type,
        "brightness_delta": brightness_delta,
        "contrast_delta": contrast_delta,
        "tone": tone,
        "description": DESCRIPTIONS[filter_type],
        "metrics": m,
    }


def apply_style_transfer(target_bytes: bytes, reference_bytes: bytes) -> bytes:
    """
    Apply the style extracted from reference_bytes onto target_bytes.
    Uses preview_edits() from creative_tools — no code duplication.
    Returns JPEG bytes.
    """
    from creative_tools import preview_edits

    ref = extract_reference_style(reference_bytes)

    tool_trace = [
        {"tool": "apply_filter", "input": {"filename": "target", "filter_type": ref["filter_type"]}, "result": {}}
    ]
    if abs(ref["brightness_delta"]) > 5:
        tool_trace.append({
            "tool": "adjust_brightness",
            "input": {"filename": "target", "level": ref["brightness_delta"]},
            "result": {},
        })
    if abs(ref["contrast_delta"]) > 5:
        tool_trace.append({
            "tool": "adjust_contrast",
            "input": {"filename": "target", "level": ref["contrast_delta"]},
            "result": {},
        })

    result = preview_edits(target_bytes, tool_trace)
    return result if result is not None else target_bytes
