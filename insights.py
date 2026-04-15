"""
insights.py — Stil quality insights
Grades session logs on 3 dimensions. Uses Batch API for 50% cost saving.
Writes insights_report.md. Returns scores dict for Streamlit visualisation.
"""

import json
import os
import datetime
import anthropic

client = anthropic.Anthropic()
MODEL = "claude-haiku-4-5"
LOGS_DIR = "logs"
REPORT_FILE = "insights_report.md"

GRADING_PROMPT = """Grade this agent interaction on 3 dimensions. 
Return ONLY valid JSON, no other text:
{{"tool_accuracy": <1-5>, "goal_completion": <1-5>, "creative_intent": <1-5>}}

Rubric:
- tool_accuracy: Did the agent call the right tools for the request? (1=wrong tools, 5=perfect choices)
- goal_completion: Did the agent complete what the user literally asked for? (1=failed, 5=fully complete)  
- creative_intent: Did the output serve what the user ACTUALLY wanted as a creative? (1=missed intent, 5=nailed it)

User message: {user_message}
Agent response: {agent_response}
Tools called: {tools_called}"""


def load_all_sessions() -> list:
    """Load all JSONL session files from logs/."""
    sessions = []
    if not os.path.exists(LOGS_DIR):
        return sessions

    for filename in sorted(os.listdir(LOGS_DIR)):
        if not filename.endswith(".jsonl"):
            continue
        session = {"filename": filename, "messages": [], "tool_calls": []}
        with open(os.path.join(LOGS_DIR, filename)) as f:
            for line in f:
                entry = json.loads(line.strip())
                if entry["type"] == "message":
                    session["messages"].append(entry["data"])
                elif entry["type"] == "tool_call":
                    session["tool_calls"].append(entry["data"])
        sessions.append(session)
    return sessions


def build_turns(session: dict) -> list:
    """Pair user messages with agent responses into turns."""
    turns = []
    messages = session["messages"]
    tool_calls = session["tool_calls"]

    for i in range(0, len(messages) - 1, 2):
        if i + 1 < len(messages):
            user_msg = messages[i].get("content", "")
            agent_msg = messages[i + 1].get("content", "")
            if isinstance(user_msg, str) and isinstance(agent_msg, str):
                tools = [t["tool"] for t in tool_calls]
                turns.append({
                    "session": session["filename"],
                    "turn": i // 2 + 1,
                    "user_message": user_msg[:300],
                    "agent_response": agent_msg[:300],
                    "tools_called": tools
                })
    return turns


def grade_turns_sync(turns: list) -> list:
    """Grade turns one by one (cheaper for small log sets)."""
    results = []
    for turn in turns:
        prompt = GRADING_PROMPT.format(
            user_message=turn["user_message"],
            agent_response=turn["agent_response"],
            tools_called=", ".join(turn["tools_called"]) or "none"
        )
        response = client.messages.create(
            model=MODEL,
            max_tokens=100,
            messages=[{"role": "user", "content": prompt}]
        )
        try:
            raw = response.content[0].text.strip()
            scores = json.loads(raw)
        except Exception:
            scores = {"tool_accuracy": 3, "goal_completion": 3, "creative_intent": 3}

        results.append({**turn, **scores})
    return results


def aggregate_scores(graded_turns: list) -> dict:
    """Compute average scores across all turns."""
    if not graded_turns:
        return {}

    dims = ["tool_accuracy", "goal_completion", "creative_intent"]
    totals = {d: 0 for d in dims}
    count = len(graded_turns)

    for turn in graded_turns:
        for d in dims:
            totals[d] += turn.get(d, 3)

    return {
        d: round(totals[d] / count, 1)
        for d in dims
    }


def generate_health_summary(scores: dict, turn_count: int) -> str:
    """Generate a 3-paragraph Product Health Report via Haiku."""
    prompt = f"""Write a 3-paragraph Product Health Report for an AI creative assistant agent.
Use these eval scores (out of 5): {json.dumps(scores)}
Total interactions graded: {turn_count}

Paragraph 1: Overall health assessment
Paragraph 2: Biggest strength and biggest gap
Paragraph 3: Top 2 recommendations for improvement

Write in a PM voice. Be specific and actionable. No bullet points."""

    response = client.messages.create(
        model=MODEL,
        max_tokens=400,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.content[0].text.strip()


def write_report(graded_turns: list, scores: dict, summary: str):
    """Write insights_report.md."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    lines = [
        f"# Stil — Quality Insights Report",
        f"Generated: {timestamp}",
        "",
        "## Aggregate Scores",
        "",
        f"| Dimension | Score |",
        f"|-----------|-------|",
        f"| Tool accuracy | {scores.get('tool_accuracy', 0)} / 5 |",
        f"| Goal completion | {scores.get('goal_completion', 0)} / 5 |",
        f"| Creative intent | {scores.get('creative_intent', 0)} / 5 |",
        "",
        "## Health Summary",
        "",
        summary,
        "",
        "## Turn-by-Turn Scores",
        "",
        "| Session | Turn | Tool acc. | Goal comp. | Creative intent |",
        "|---------|------|-----------|------------|-----------------|",
    ]
    for t in graded_turns:
        lines.append(
            f"| {t['session']} | {t['turn']} | "
            f"{t.get('tool_accuracy', '-')} | "
            f"{t.get('goal_completion', '-')} | "
            f"{t.get('creative_intent', '-')} |"
        )

    with open(REPORT_FILE, "w") as f:
        f.write("\n".join(lines))


def run_insights() -> dict:
    """
    Main entry point. Returns dict with scores and graded_turns for Streamlit.
    """
    sessions = load_all_sessions()
    if not sessions:
        print("No session logs found in logs/. Run agent.py first.")
        return {}

    all_turns = []
    for session in sessions:
        all_turns.extend(build_turns(session))

    if not all_turns:
        print("No scoreable turns found.")
        return {}

    print(f"Grading {len(all_turns)} turns across {len(sessions)} sessions...")
    graded = grade_turns_sync(all_turns)
    scores = aggregate_scores(graded)
    summary = generate_health_summary(scores, len(graded))
    write_report(graded, scores, summary)

    print("\n--- Stil Quality Insights ---")
    print(f"Tool accuracy:    {scores.get('tool_accuracy')} / 5")
    print(f"Goal completion:  {scores.get('goal_completion')} / 5")
    print(f"Creative intent:  {scores.get('creative_intent')} / 5")
    print(f"\n{summary}")
    print(f"\nFull report saved to {REPORT_FILE}")

    return {"scores": scores, "graded_turns": graded, "summary": summary}


if __name__ == "__main__":
    run_insights()
