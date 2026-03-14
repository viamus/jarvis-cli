"""Claude Code hook entry point.

Protocol:
  stdin  -> JSON with prompt, session_id, hook_event_name, etc.
  stdout -> JSON with decision and reason
  exit 0 -> pass-through (not a trigger word)
  exit 2 -> block with feedback (Claude receives the reason text)
"""

from __future__ import annotations

import json
import sys

from jarvis.config import TRIGGER_WORDS
from jarvis.storage import load_transcription


def main() -> None:
    try:
        data = json.loads(sys.stdin.read())
    except (json.JSONDecodeError, EOFError):
        sys.exit(0)

    prompt = data.get("prompt", "").strip().lower()

    # Not a trigger word — pass through
    if prompt not in TRIGGER_WORDS:
        sys.exit(0)

    # Try to load transcription
    transcription = load_transcription(consume=True)

    if transcription is None:
        result = {
            "decision": "block",
            "reason": (
                "[Jarvis] No transcription available. "
                "Press Ctrl+Alt+J to record first, then type /voz again."
            ),
        }
    else:
        result = {
            "decision": "block",
            "reason": f"[Jarvis] [{transcription.language}] {transcription.text}",
        }

    json.dump(result, sys.stdout, ensure_ascii=False)
    sys.exit(2)


if __name__ == "__main__":
    main()
