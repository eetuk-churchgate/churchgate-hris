"""
Client for the Churchgate Onboarding Agent (Cloud Run).
Streams SSE responses from POST /api/onboard-chat.
"""

import json
import uuid
import requests

AGENT_URL = "https://onboarding-agent-281223373032.us-central1.run.app"


def new_session_id() -> str:
    return str(uuid.uuid4())


def stream_chat(message: str, session_id: str, employee_email: str | None = None):
    """
    Generator that yields text chunks from the onboarding agent SSE stream.
    Raises requests.RequestException on connection failure.
    """
    payload = {"message": message, "session_id": session_id}
    if employee_email:
        payload["employee_email"] = employee_email

    with requests.post(
        f"{AGENT_URL}/api/onboard-chat",
        json=payload,
        stream=True,
        timeout=60,
    ) as resp:
        resp.raise_for_status()
        for raw_line in resp.iter_lines():
            if not raw_line:
                continue
            line = raw_line.decode("utf-8") if isinstance(raw_line, bytes) else raw_line
            if not line.startswith("data:"):
                continue
            data = line[len("data:"):].strip()
            try:
                event = json.loads(data)
            except json.JSONDecodeError:
                continue
            if event.get("error"):
                raise RuntimeError(event["error"])
            chunk = event.get("chunk", "")
            if chunk:
                yield chunk
            if event.get("done"):
                break


def chat(message: str, session_id: str, employee_email: str | None = None) -> str:
    """Blocking version — collects the full streamed response and returns it."""
    return "".join(stream_chat(message, session_id, employee_email))
