# Jarvis-CLI

Voice middleware for [Claude Code](https://claude.com/claude-code) — speech-to-text in **PT-BR** and **EN**.

Jarvis captures audio from your microphone, transcribes it using [faster-whisper](https://github.com/SYSTRAN/faster-whisper), and injects the text into Claude Code via a `/jarvis` skill. Speak in Portuguese or English and let Claude act on your voice commands.

## Architecture

```
+---------------------+     +------------------+     +--------------+
|   Daemon (Python)   |     |   JSON (temp)    |     |  Claude Code  |
|                     |     |                  |     |              |
| Ctrl+Alt+J > Record |---->| last_transcript  |<----| /jarvis skill |
| VAD > Stop          |     | .json            |     | reads & sends |
| Whisper > Transcribe|     |                  |     |              |
+---------------------+     +------------------+     +--------------+
```

- **Daemon** loads the Whisper model once and stays resident in memory
- **Skill** (`/jarvis`) reads the transcription JSON and passes it to Claude as if the user typed it
- Communication via filesystem is simple and reliable

## Features

- Global hotkey (Ctrl+Alt+J) to start recording
- Automatic silence detection (VAD) stops recording after 1.5s of silence
- Auto-detects language (Portuguese, English, and others)
- Audio feedback beeps for recording start/stop
- Atomic file operations for reliable IPC
- Claude Code skill integration via `/jarvis`

## Requirements

- Python 3.10+
- Windows 10/11 (uses `winsound` for beeps and `keyboard` for global hotkeys)
- A working microphone

## Installation

### Quick Install

```bash
install.bat
```

### Manual Install

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -e .
```

## Usage

### Quick Start

```bash
run.bat
```

This will run tests, install the `/jarvis` skill, and start the daemon.

### Manual Start

```bash
# 1. Install the /jarvis skill into Claude Code
jarvis install-skill

# 2. Start the daemon
jarvis daemon

# 3. In Claude Code:
#    - Press Ctrl+Alt+J to start recording
#    - Speak in Portuguese or English
#    - Wait for the stop beep (silence detection)
#    - Type /jarvis and press Enter
#    - Claude receives your transcribed text and acts on it
```

### CLI Commands

| Command               | Description                              |
|-----------------------|------------------------------------------|
| `jarvis daemon`      | Start the voice daemon (blocks)          |
| `jarvis test`        | Record and transcribe a clip (testing)   |
| `jarvis status`      | Check if the daemon is running           |
| `jarvis stop`        | Stop the running daemon                  |
| `jarvis install-skill` | Install `/jarvis` skill into Claude Code |

## Configuration

Environment variables for customization:

| Variable             | Default        | Description                |
|----------------------|----------------|----------------------------|
| `JARVIS_HOTKEY`     | `ctrl+alt+j`  | Global hotkey to record    |
| `JARVIS_WHISPER_MODEL` | `base`      | Whisper model size         |

Available Whisper models: `tiny`, `base`, `small`, `medium`, `large-v3`

## Tech Stack

| Library          | Purpose            | Why                                              |
|------------------|--------------------|--------------------------------------------------|
| `faster-whisper` | Speech-to-text     | 4x faster than openai-whisper, auto language detection |
| `sounddevice`    | Audio capture      | Clean API over PortAudio, works well on Windows  |
| `numpy`          | Audio buffers      | Required by sounddevice, float32 arrays for Whisper |
| `keyboard`       | Global hotkey      | Works on Windows without elevation               |
| `click`          | CLI framework      | Clean subcommands                                |

## Project Structure

```
jarvis-cli/
├── pyproject.toml          # Package configuration
├── install.bat             # One-click install
├── run.bat                 # One-click run
├── src/jarvis/
│   ├── cli.py              # Click CLI commands
│   ├── config.py           # Constants and paths
│   ├── daemon.py           # Main loop: hotkey > record > transcribe > save
│   ├── recorder.py         # Audio capture (16kHz mono)
│   ├── vad.py              # Silence detection by RMS energy
│   ├── transcriber.py      # faster-whisper wrapper
│   ├── storage.py          # Atomic JSON read/write
│   └── audio_feedback.py   # Start/stop beeps
└── tests/
    ├── test_storage.py
    └── test_transcriber.py
```

## Testing

```bash
# Activate venv
.venv\Scripts\activate

# Run all tests
python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/test_storage.py -v
```

## Contributing

Contributions are welcome! Please read the [Contributing Guidelines](CONTRIBUTING.md) and [Code of Conduct](CODE_OF_CONDUCT.md) before submitting a pull request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Security

Please see [SECURITY.md](SECURITY.md) for reporting vulnerabilities.

## Acknowledgments

- [faster-whisper](https://github.com/SYSTRAN/faster-whisper) by SYSTRAN
- [Claude Code](https://claude.com/claude-code) by Anthropic
- [OpenAI Whisper](https://github.com/openai/whisper) for the original model
