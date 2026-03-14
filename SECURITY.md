# Security Policy

## Supported Versions

| Version | Supported          |
|---------|--------------------|
| 0.1.x   | Yes                |

## Reporting a Vulnerability

If you discover a security vulnerability in Jarvis-CLI, please report it responsibly.

**Do NOT open a public issue for security vulnerabilities.**

Instead, please send a detailed report to the repository maintainers via GitHub private vulnerability reporting:

1. Go to the [Security tab](../../security) of this repository
2. Click "Report a vulnerability"
3. Provide a detailed description of the vulnerability

### What to include

- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

### What to expect

- Acknowledgment within 48 hours
- A fix or mitigation plan within 7 days for critical issues
- Credit in the release notes (unless you prefer to remain anonymous)

## Security Considerations

### Audio Data

- Audio is recorded only when explicitly triggered by the user (hotkey press)
- Audio data is processed locally — no data is sent to external servers
- Transcriptions are stored in the system temp directory and marked as consumed after use

### File System

- Transcription files use atomic writes to prevent partial reads
- PID files are stored in the system temp directory
- The Claude Code hook only reads local JSON files

### Dependencies

- All speech-to-text processing happens locally via faster-whisper
- No network requests are made during normal operation
- The Whisper model is downloaded once from Hugging Face Hub on first use
