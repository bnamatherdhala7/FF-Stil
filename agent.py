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


def build_system_prompt(memory: dict) -> str:
    """Inject memory into system prompt if available."""
    base = SYSTEM_PROMPT
    if memory.get("style_signature"):
        sig = memory["style_signature"]
        memory_block = f"""
User style profile (apply these preferences unless told otherwise):
- Tone: {sig.get('tone', 'not set')}
- Crop preference: {sig.get('crop_preference', 'not set')}
- Export targets: {', '.join(sig.get('export_targets', []))}
- Notes: {sig.get('notes', 'none')}"""
        return base + memory_block
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
                        yield {"type": "tool_end", "tool": block.name, "result": result_dict}
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
Return ONLY valid JSON, no other text:
{{
  "tone": "warm|cool|neutral",
  "crop_preference": "square|landscape|portrait|none",
  "export_targets": ["platform1"],
  "notes": "one sentence summary of preferences"
}}

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
