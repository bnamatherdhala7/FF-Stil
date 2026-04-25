"""
agent.py — Stil core agent loop
Handles: memory loading, Claude API calls, tool execution, memory extraction,
session logging. Used by app.py (Streamlit) and runnable standalone in terminal.
"""

import base64
import io
import json
import os
import datetime
from typing import Generator
from dotenv import load_dotenv
import anthropic
from PIL import Image
from creative_tools import TOOL_DEFINITIONS, TOOL_MAP

load_dotenv()
client = anthropic.Anthropic()
MODEL = "claude-haiku-4-5"
MEMORY_FILE = "style_profile.json"
LOGS_DIR = "logs"

SYSTEM_PROMPT = """You are Stil, an AI assistant for creative professionals.
When an image is provided, briefly describe what you see — subject, lighting, tone, composition — then execute the user's request using the available tools.
When no image is provided, work from the user's description.
Be concise. Confirm what you did in 1-2 sentences. Never explain what tools are — just use them."""


def _compress_image(image_bytes: bytes, max_bytes: int = 4_500_000) -> tuple[bytes, str]:
    """
    Resize and JPEG-compress image to stay under max_bytes.
    Anthropic hard limit is 5 MB; we target 4.5 MB to be safe.
    Returns (compressed_bytes, "image/jpeg").
    """
    img = Image.open(io.BytesIO(image_bytes))

    # Normalise to RGB (handles RGBA PNGs, CMYK, palette, etc.)
    if img.mode != "RGB":
        img = img.convert("RGB")

    # Shrink to ≤1568 px on the longest side (Claude's recommended max)
    MAX_DIM = 1568
    w, h = img.size
    if max(w, h) > MAX_DIM:
        scale = MAX_DIM / max(w, h)
        img = img.resize((int(w * scale), int(h * scale)), Image.LANCZOS)

    # Compress at decreasing quality until it fits
    for quality in (85, 75, 60, 45):
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=quality, optimize=True)
        if buf.tell() <= max_bytes:
            return buf.getvalue(), "image/jpeg"

    # Last resort: halve resolution and save at q=50
    img = img.resize((img.width // 2, img.height // 2), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=50, optimize=True)
    return buf.getvalue(), "image/jpeg"


def extract_color_palette(image_bytes: bytes) -> list:
    """Extract up to 5 dominant colors from image bytes. Returns hex strings."""
    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    img = img.resize((100, 100), Image.LANCZOS)
    quantized = img.quantize(colors=8)
    palette_data = quantized.getpalette()
    colors = []
    for i in range(0, 24, 3):  # 8 colors × 3 channels
        r, g, b = palette_data[i], palette_data[i + 1], palette_data[i + 2]
        brightness = (r + g + b) / 3
        if 20 < brightness < 240:  # skip near-black and near-white
            colors.append(f"#{r:02x}{g:02x}{b:02x}")
    return colors[:5]


def load_style() -> dict:
    """Load user style profile from style_profile.json."""
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r") as f:
            return json.load(f)
    return {}


def save_style(memory: dict):
    """Write memory dict to style_profile.json."""
    memory["last_updated"] = datetime.datetime.now().isoformat()
    with open(MEMORY_FILE, "w") as f:
        json.dump(memory, f, indent=2)


def update_choices_log(tool_trace: list, existing_style: dict = None) -> dict:
    """
    Record explicit tool choices from the session into a deterministic choices_log.
    Ground truth — read directly from tool calls, no AI guessing.
    Newest entry first, capped at 10.
    """
    style = existing_style or {}

    choices = {}
    for call in tool_trace:
        tool = call.get("tool", "")
        inp = call.get("input", {})
        if tool == "apply_filter" and inp.get("filter_type"):
            choices["filter"] = inp["filter_type"]
        elif tool == "crop_image" and inp.get("ratio"):
            choices["crop"] = inp["ratio"]
        elif tool == "set_export_preset" and inp.get("platform"):
            choices["export"] = inp["platform"]
        elif tool == "adjust_brightness" and inp.get("level") is not None:
            choices["brightness"] = inp["level"]

    if not choices:
        return style

    choices["ts"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    log = style.get("choices_log", [])
    log.insert(0, choices)
    style["choices_log"] = log[:10]
    save_style(style)
    return style


def build_system_prompt(memory: dict) -> str:
    """
    Inject style preferences into system prompt.
    Priority: choices_log (deterministic, from actual tool calls) > style_signature (AI-extracted).
    """
    base = SYSTEM_PROMPT
    sig = memory.get("style_signature") or {}
    log = memory.get("choices_log") or []
    recent = log[0] if log else {}

    lines = []

    # Filter / tone — recent log wins
    if recent.get("filter"):
        lines.append(f"- Preferred filter: {recent['filter']} (last used)")
    elif sig.get("filter_style") and sig["filter_style"] != "none":
        lines.append(f"- Preferred filter: {sig['filter_style']}")
    elif sig.get("tone"):
        lines.append(f"- Tone: {sig['tone']}")

    # Crop — recent log wins
    if recent.get("crop"):
        lines.append(f"- Crop: {recent['crop']} (last used)")
    elif sig.get("crop_preference") and sig["crop_preference"] != "none":
        lines.append(f"- Crop: {sig['crop_preference']}")

    # Export — recent log wins
    if recent.get("export"):
        lines.append(f"- Export for: {recent['export']} (last used)")
    elif sig.get("export_targets"):
        lines.append(f"- Export targets: {', '.join(sig['export_targets'])}")

    # Brightness hint if last session had an explicit level
    if recent.get("brightness") is not None:
        lines.append(f"- Brightness adjustment: {recent['brightness']:+d} (last used)")

    if sig.get("notes"):
        lines.append(f"- Aesthetic: {sig['notes']}")

    if lines:
        return base + "\n\nUser style profile (apply unless told otherwise):\n" + "\n".join(lines)
    return base


def execute_tool(tool_name: str, tool_input: dict) -> str:
    """Execute a ps_tool function and return result as JSON string."""
    func = TOOL_MAP.get(tool_name)
    if not func:
        return json.dumps({"status": "error", "message": f"Unknown tool: {tool_name}"})
    result = func(**tool_input)
    return json.dumps(result)


def run_agent(user_message: str, memory: dict = None) -> tuple[str, list]:
    """
    Run the agent loop synchronously.
    Returns: (final_response_text, tool_trace)
    tool_trace is a list of {"tool": name, "input": dict, "result": dict}
    """
    if memory is None:
        memory = load_style()

    messages = [{"role": "user", "content": user_message}]
    system = build_system_prompt(memory)
    tool_trace = []

    for _ in range(6):
        response = client.messages.create(
            model=MODEL,
            max_tokens=1000,
            system=system,
            tools=TOOL_DEFINITIONS,
            messages=messages
        )

        if response.stop_reason == "end_turn":
            final_text = ""
            for block in response.content:
                if hasattr(block, "text"):
                    final_text = block.text
            return final_text, tool_trace

        if response.stop_reason == "tool_use":
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    result_str = execute_tool(block.name, block.input)
                    result_dict = json.loads(result_str)
                    tool_trace.append({
                        "tool": block.name,
                        "input": block.input,
                        "result": result_dict
                    })
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result_str
                    })

            messages.append({"role": "assistant", "content": response.content})
            messages.append({"role": "user", "content": tool_results})

    return "Task completed.", tool_trace


def run_agent_streaming(user_message: str, memory: dict = None,
                        image_bytes: bytes = None, image_media_type: str = "image/jpeg",
                        conversation_history: list = None) -> Generator:
    """
    Generator for Streamlit streaming.
    Yields dicts: {"type": "text", "content": str}
                  {"type": "tool_start", "tool": str, "input": dict}
                  {"type": "tool_end", "tool": str, "result": dict}
                  {"type": "done", "tool_trace": list, "api_messages": list}
                  {"type": "error", "content": str}

    Pass conversation_history (prior Claude API messages) for multi-turn sessions.
    The image from turn 1 stays in context automatically — no need to re-upload.
    Pass image_bytes only when a new image is being introduced.
    """
    if memory is None:
        memory = load_style()

    # Build the new user message content — multimodal if a new image is provided
    if image_bytes:
        image_bytes, image_media_type = _compress_image(image_bytes)
        new_content = [
            {
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": image_media_type,
                    "data": base64.standard_b64encode(image_bytes).decode("utf-8"),
                },
            },
            {"type": "text", "text": user_message},
        ]
    else:
        new_content = user_message

    # Append new message to existing history (or start fresh)
    messages = list(conversation_history) + [{"role": "user", "content": new_content}] \
        if conversation_history else [{"role": "user", "content": new_content}]

    system = build_system_prompt(memory)
    tool_trace = []

    try:
        for _ in range(6):
            response = client.messages.create(
                model=MODEL,
                max_tokens=1000,
                system=system,
                tools=TOOL_DEFINITIONS,
                messages=messages
            )

            if response.stop_reason == "end_turn":
                for block in response.content:
                    if hasattr(block, "text"):
                        for word in block.text.split(" "):
                            yield {"type": "text", "content": word + " "}
                # Append final assistant message so caller can persist the full history
                messages.append({"role": "assistant", "content": response.content})
                yield {"type": "done", "tool_trace": tool_trace, "api_messages": messages}
                return

            if response.stop_reason == "tool_use":
                tool_results = []
                for block in response.content:
                    if block.type == "tool_use":
                        yield {"type": "tool_start", "tool": block.name, "input": block.input}
                        result_str = execute_tool(block.name, block.input)
                        result_dict = json.loads(result_str)
                        tool_trace.append({
                            "tool": block.name,
                            "input": block.input,
                            "result": result_dict
                        })
                        yield {"type": "tool_end", "tool": block.name, "result": result_dict, "input": block.input}
                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": result_str
                        })

                messages.append({"role": "assistant", "content": response.content})
                messages.append({"role": "user", "content": tool_results})

    except anthropic.AuthenticationError:
        yield {"type": "error", "content": "API key invalid. Add your full key to `stil/.env`: `ANTHROPIC_API_KEY=sk-ant-...`"}
        return
    except anthropic.APIConnectionError:
        yield {"type": "error", "content": "Could not reach Anthropic API. Check your internet connection."}
        return
    except Exception as e:
        yield {"type": "error", "content": f"Unexpected error: {e}"}
        return

    yield {"type": "done", "tool_trace": tool_trace, "api_messages": messages}


def extract_and_save_style(session_log: list, existing_style: dict = None) -> dict:
    """
    After a session, extract style signature using Haiku and merge into style_profile.json.
    session_log: list of {"role": ..., "content": ...} dicts
    """
    if not session_log:
        return existing_style or {}

    log_text = "\n".join([
        f"{m['role'].upper()}: {m['content']}"
        for m in session_log
        if isinstance(m.get('content'), str)
    ])

    prompt = f"""From this creative editing session, extract the user's style preferences.
Focus on what the user EXPLICITLY requested in this session — their latest request overrides earlier ones.

Return ONLY valid JSON, no other text:
{{
  "tone": "warm|cool|neutral",
  "filter_style": "warm|cool|vintage|dramatic|bw|none",
  "crop_preference": "square|landscape|portrait|story|none",
  "export_targets": ["platform1"],
  "notes": "one sentence capturing the dominant aesthetic the user was going for"
}}

Rules:
- tone: the colour temperature preference (warm=golden/orange, cool=blue/grey, neutral=balanced)
- filter_style: the most recent explicit filter the user applied or requested — this takes priority
- If the user changed their mind mid-session, use the LATEST preference, not the first
- If a field is unclear from the session, omit it from the JSON (do not guess)

Session:
{log_text}"""

    response = client.messages.create(
        model=MODEL,
        max_tokens=200,
        messages=[{"role": "user", "content": prompt}]
    )

    try:
        raw = response.content[0].text.strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        new_sig = json.loads(raw.strip())
    except Exception:
        new_sig = {}

    style = existing_style or {}
    style["user_id"] = "default"
    style["style_signature"] = {**(style.get("style_signature") or {}), **new_sig}
    save_style(style)
    return style


def write_session_log(messages: list, tool_trace: list):
    """Write session to logs/session_TIMESTAMP.jsonl"""
    os.makedirs(LOGS_DIR, exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filepath = os.path.join(LOGS_DIR, f"session_{timestamp}.jsonl")
    with open(filepath, "w") as f:
        for msg in messages:
            f.write(json.dumps({"type": "message", "data": msg}) + "\n")
        for trace in tool_trace:
            f.write(json.dumps({"type": "tool_call", "data": trace}) + "\n")
    return filepath


if __name__ == "__main__":
    print("Stil — terminal mode")
    print("Type 'quit' to exit\n")
    style = load_style()
    session_messages = []
    all_tool_trace = []

    if style.get("style_signature"):
        print(f"Memory loaded: {style['style_signature']}\n")

    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in ("quit", "exit", "q"):
            break
        if not user_input:
            continue

        session_messages.append({"role": "user", "content": user_input})
        response, tool_trace = run_agent(user_input, style)
        all_tool_trace.extend(tool_trace)

        if tool_trace:
            for t in tool_trace:
                print(f"  ⚡ {t['tool']}({t['input']}) → {t['result']['action']}")

        print(f"Agent: {response}\n")
        session_messages.append({"role": "assistant", "content": response})

    if session_messages:
        style = extract_and_save_style(session_messages, style)
        write_session_log(session_messages, all_tool_trace)
        print("\nMemory updated and session saved.")
