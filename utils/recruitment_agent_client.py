"""
Client for the Churchgate Recruitment Agent (Cloud Run).
Provides:
  - screen_candidate()  : trigger AI screening (blocking, returns full JSON result)
  - stream_chat()       : SSE generator for conversational queries
  - chat()              : blocking version of stream_chat
"""

import json
import uuid
import requests
from typing import Optional

AGENT_URL = "https://recruitment-agent-o3o33wvgya-uc.a.run.app"


def new_session_id() -> str:
    return str(uuid.uuid4())


def screen_candidate(candidate_ref: str, job_id: str, timeout: int = 120) -> dict:
    """
    Triggers a full AI screening of a candidate against a job requisition.
    Blocking call — waits for the agent to complete the full evaluation.

    Returns a dict with keys: status, candidate_ref, job_id, summary.
    Raises requests.RequestException on connection failure.
    Raises RuntimeError if the agent returns an error status.
    """
    payload = {"candidate_ref": candidate_ref, "job_id": job_id}
    resp = requests.post(
        f"{AGENT_URL}/api/screen-candidate",
        json=payload,
        timeout=timeout,
    )
    resp.raise_for_status()
    data = resp.json()
    if data.get("status") != "success":
        raise RuntimeError(data.get("summary", "Unknown error from recruitment agent."))
    return data


def stream_chat(message: str, session_id: str):
    """
    Generator that yields text chunks from the recruitment agent SSE stream.
    Use for conversational queries about candidates, job requisitions, or screening results.
    Raises requests.RequestException on connection failure.
    """
    payload = {"message": message, "session_id": session_id}

    with requests.post(
        f"{AGENT_URL}/api/chat",
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


def chat(message: str, session_id: str) -> str:
    """Blocking version — collects the full streamed response and returns it."""
    return "".join(stream_chat(message, session_id))
