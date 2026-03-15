# Jarvis-CLI

Voice middleware for [Claude Code](https://claude.com/claude-code) — speech-to-text in **PT-BR** and **EN**.

Jarvis captures audio from your microphone, transcribes it using [faster-whisper](https://github.com/SYSTRAN/faster-whisper), and injects the text into Claude Code via a `/jarvis` skill. Speak in Portuguese or English and let Claude act on your voice commands.

## Architecture

```
+---------------------+     +------------------+     +--------------+
|   Daemon (Python)   |     |   JSON (temp)    |     |  Claude Code  |
|                     |     |                  |     |              |
| Hotkey > Record     |---->| last_transcript  |<----| /jarvis skill |
| VAD > Stop          |     | .json            |     | reads & sends |
| Whisper > Transcribe|     |                  |     |              |
| Auto-type /jarvis   |     |                  |     |              |
+---------------------+     +------------------+     +--------------+
```

- **Daemon** loads the Whisper model once, stays resident in the system tray
- **Skill** (`/jarvis`) reads the transcription JSON and passes it to Claude as if the user typed it
- **Hands-free**: after transcription, Jarvis auto-types `/jarvis` + Enter in the active terminal

## Features

- **System tray icon** with status indicators (idle/recording/transcribing)
- **Configurable hotkey** — keyboard shortcut or mouse button (e.g. Mouse5)
- **Toggle recording** — press hotkey once to start, again to stop immediately
- **Auto-silence detection** (VAD) stops recording after 2s of silence
- **GPU acceleration** — auto-detects CUDA, uses `distil-large-v3` on GPU
- **CPU fallback** — uses `small` model with `float32` when no GPU available
- **Audio feedback** — 3 distinct beeps: start, stop, transcription ready
- **Auto-submit** — types `/jarvis` + Enter automatically when transcription is ready
- **PT-BR optimized** — language hint + tech vocabulary prompt for better accuracy
- Atomic file operations for reliable IPC
- Persistent settings (hotkey, preferences)

## Requirements

- Python 3.10+
- Windows 10/11
- A working microphone
- **Optional**: NVIDIA GPU with CUDA support (RTX series recommended)

## Installation

### Quick Install

```bash
install.bat
```

This installs dependencies, downloads the appropriate Whisper model (auto-detects GPU), and sets everything up.

### Manual Install

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -e .
jarvis download-model
```

## GPU Setup (Optional)

If you have an NVIDIA GPU (e.g. RTX 4060), Jarvis will auto-detect it and use the `distil-large-v3` model with `float16` — transcription is nearly instant (~0.1s).

The CUDA libraries (`nvidia-cublas-cu12`, `nvidia-cudnn-cu12`) are installed automatically as dependencies.

Without a GPU, Jarvis uses the `small` model on CPU with `float32` — still good quality, ~2-3s per transcription.

| Setup | Model | Speed | Quality |
|-------|-------|-------|---------|
| GPU (CUDA) | `distil-large-v3` | ~0.1s | Excellent |
| CPU | `small` | ~2-3s | Good |

## Usage

### Quick Start

```bash
run.bat
```

This runs tests, installs the `/jarvis` skill, and starts the daemon in the system tray.

### How It Works

1. **Press your hotkey** (default: `Ctrl+Alt+J`) to start recording
2. **Speak** your command in Portuguese or English
3. **Stop** — either press the hotkey again, or wait for silence detection
4. **Beep sounds**: start beep → stop beep → ready beep (triple ascending)
5. **Auto-submit** — Jarvis types `/jarvis` + Enter in your terminal automatically
6. **Claude responds** to your voice command

### System Tray

Jarvis runs as a system tray icon (near the clock). Right-click for options:

- **Status** — current state (Idle/Recording/Transcribing)
- **Hotkey** — shows current hotkey
- **Change Hotkey...** — open dialog to set a new key or mouse button
- **System Info...** — shows model, device, GPU, compute type
- **Quit** — stop the daemon

### CLI Commands

| Command               | Description                              |
|-----------------------|------------------------------------------|
| `jarvis daemon`      | Start the daemon with tray icon          |
| `jarvis daemon --no-tray` | Start in console mode (no tray)     |
| `jarvis download-model` | Download the Whisper model             |
| `jarvis test`        | Record and transcribe a clip (testing)   |
| `jarvis status`      | Check if the daemon is running           |
| `jarvis stop`        | Stop the running daemon                  |
| `jarvis install-skill` | Install `/jarvis` skill into Claude Code |

## Configuration

### Hotkey

Configure via the tray icon ("Change Hotkey...") or environment variable:

| Variable             | Default        | Description                |
|----------------------|----------------|----------------------------|
| `JARVIS_HOTKEY`     | `ctrl+alt+j`  | Global hotkey to record    |
| `JARVIS_WHISPER_MODEL` | `small`    | Whisper model (CPU default) |

Supported hotkeys: any keyboard combination (`ctrl+alt+j`, `f5`, `shift+f1`) or mouse button (`mouse4`, `mouse5`).

### Whisper Models

Available models (in order of quality/size):

| Model | Parameters | Best for |
|-------|-----------|----------|
| `tiny` | 39M | Quick tests |
| `base` | 74M | Basic usage |
| `small` | 244M | CPU default — good quality |
| `medium` | 769M | Better quality, slower CPU |
| `distil-large-v3` | 756M | GPU default — fast + excellent |
| `large-v3` | 1.5B | Maximum quality, slower |

## Tech Stack

| Library          | Purpose            | Why                                              |
|------------------|--------------------|--------------------------------------------------|
| `faster-whisper` | Speech-to-text     | 4x faster than openai-whisper, CUDA support      |
| `sounddevice`    | Audio capture      | Clean API over PortAudio, works well on Windows  |
| `numpy`          | Audio buffers      | Required by sounddevice, float32 arrays           |
| `keyboard`       | Global hotkey      | Works on Windows without elevation               |
| `mouse`          | Mouse button hotkey | Same author as keyboard, supports side buttons   |
| `pystray`        | System tray icon   | Lightweight, native Windows tray integration     |
| `Pillow`         | Icon generation    | Programmatic icon creation, no external assets   |
| `click`          | CLI framework      | Clean subcommands                                |

## Project Structure

```
jarvis-cli/
├── pyproject.toml          # Package configuration
├── install.bat             # One-click install
├── run.bat                 # One-click run (system tray)
├── src/jarvis/
│   ├── cli.py              # Click CLI commands
│   ├── config.py           # Constants and paths
│   ├── daemon.py           # Main loop: hotkey > record > transcribe > save
│   ├── recorder.py         # Audio capture (16kHz mono)
│   ├── vad.py              # Silence detection by RMS energy
│   ├── transcriber.py      # faster-whisper wrapper (GPU auto-detect)
│   ├── storage.py          # Atomic JSON read/write
│   ├── audio_feedback.py   # Start/stop/ready beeps
│   ├── icon.py             # Programmatic tray icon generation
│   ├── tray.py             # System tray integration
│   ├── settings.py         # Persistent settings (JSON)
│   ├── hotkey_dialog.py    # Hotkey capture dialog (tkinter)
│   ├── info_dialog.py      # System info dialog
│   └── download_model.py   # Model download with feedback
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
