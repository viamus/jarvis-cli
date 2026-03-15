"""Claude Code hook entry point.

Protocol (UserPromptSubmit):
  stdin  -> JSON with prompt, session_id, hook_event_name, etc.
  stdout -> plain text becomes additionalContext for Claude
           JSON with "decision":"block" + exit 2 blocks the prompt
  exit 0 -> success, stdout is added as context
  exit 2 -> block the prompt (reason shown to user, not to Claude)
"""

from __future__ import annotations

import json
import sys

from jarvis.config import TRIGGER_WORDS
from jarvis.storage import load_transcription


def _log(msg: str) -> None:
    """Debug log to temp file."""
    from pathlib import Path
    import tempfile
    log_dir = Path(tempfile.gettempdir()) / "jarvis-cli"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_path = log_dir / "hook.log"
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(msg + "\n")


def main() -> None:
    _log("Hook called")
    try:
        raw = sys.stdin.read()
        _log(f"stdin: {raw}")
        data = json.loads(raw)
    except (json.JSONDecodeError, EOFError) as e:
        _log(f"Parse error: {e}")
        return

    prompt = data.get("prompt", "").strip().lower().lstrip("/")

    # Not a trigger word — pass through
    if prompt not in TRIGGER_WORDS:
        return

    # Try to load transcription
    transcription = load_transcription(consume=True)

    if transcription is None:
        # Block: no transcription available
        result = json.dumps({
            "decision": "block",
            "reason": "[Jarvis] No transcription available. "
                      "Press Ctrl+Alt+J to record first, then type 'voz' again.",
        })
        print(result)
        sys.exit(2)
    else:
        # Block with transcription so user sees it, then can re-submit
        result = json.dumps({
            "decision": "block",
            "reason": f"[{transcription.language}] {transcription.text}",
        })
        print(result)
        sys.exit(2)


if __name__ == "__main__":
    main()
