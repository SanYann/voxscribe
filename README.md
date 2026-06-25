# voxscribe

Transcribe voice notes — WhatsApp `.opus`, `.mp3`, `.m4a`, `.ogg`, anything `ffmpeg` reads — **locally**, on your machine, with [whisper.cpp](https://github.com/ggerganov/whisper.cpp). No cloud, no API keys, no audio leaving your laptop.

It started as a one-off: a friend sent a 1-minute WhatsApp voice note and asked "can you transcribe this?". This is that, packaged.

> 🍎 **macOS only** for now. voxscribe is built and tested for Mac — it won't run on Windows, and Linux isn't supported.

```console
$ voxscribe "WhatsApp Audio 2026-06-23.opus" -l fr
Et donc en fait, tous les ans, avant le 30 juin, il faut déposer les comptes auprès du greffe...
```

## Easy install (no coding needed) 🟢

For macOS — you don't need to understand any of this, just follow along.

1. Open the **Terminal** app (press `⌘ + Space`, type `Terminal`, hit Enter).
2. Copy the line below, paste it into the Terminal (`⌘ + V`), and press Enter:

   ```bash
   curl -fsSL https://raw.githubusercontent.com/SanYann/voxscribe/main/install.sh | bash
   ```

3. Wait. It installs everything for you (it may ask for your Mac password — that's
   normal, type it and press Enter; the characters stay invisible).
4. When it says **Done! 🎉**, **close the Terminal and open a new one**.

That's it. To transcribe a voice note, drag-and-drop is easiest:

```bash
voxscribe 
```

…type `voxscribe ` then a space, **drag your audio file onto the Terminal window**
(its path appears automatically), and press Enter. Add `-l fr` for French:

```bash
voxscribe "/Users/you/Downloads/note.opus" -l fr
```

> The very first run downloads a small AI model (~140 MB). That happens once.

If you also use **Claude**, the installer connects voxscribe automatically — then
you can just tell Claude *"transcribe this voice note"* and it does it for you.
See [Use it from Claude](#use-it-from-claude-mcp) below.

---

## Manual install (for developers)

voxscribe wraps two native tools — install them first:

```bash
brew install ffmpeg whisper-cpp
```

Then install voxscribe itself:

```bash
pipx install voxscribe        # recommended
# or
pip install voxscribe
# or run from a clone without installing
pip install -e .
```

> The whisper.cpp binary may be called `whisper-cli`, `whisper-cpp`, or `main`
> depending on how you installed it — voxscribe finds whichever is on your PATH.

## Usage

```bash
voxscribe note.opus                      # auto-detect language, print to stdout
voxscribe note.opus -l fr                # force French
voxscribe note.opus -m medium            # use a bigger, more accurate model
voxscribe note.opus -f srt -o note.srt   # write subtitles
voxscribe note.m4a -l es --translate     # transcribe + translate to English
voxscribe *.opus -l fr                   # batch: writes note.txt next to each file
```

| Option | Description |
| --- | --- |
| `-l, --language` | Language code (`fr`, `en`, …) or `auto` (default) |
| `-m, --model` | Model name or path to a `.bin` (default `base`) |
| `-f, --format` | `txt` (default), `srt`, `vtt`, `json` |
| `-o, --output` | Write to a file instead of stdout (single input) |
| `--translate` | Translate the speech to English |
| `-t, --threads` | Number of threads |
| `-q, --quiet` | Suppress whisper.cpp logging |

### Models

The first time you use a model, voxscribe downloads its GGML weights into
`~/.cache/voxscribe/models/` (override with `VOXSCRIBE_HOME`).

| Model | Size | Notes |
| --- | --- | --- |
| `tiny` | ~75 MB | fastest, lowest quality |
| `base` | ~142 MB | fast, decent quality (**default**) |
| `small` | ~466 MB | better quality |
| `medium` | ~1.5 GB | high quality |
| `large-v3` | ~3.1 GB | best quality |
| `large-v3-turbo` | ~1.6 GB | fast + near-best quality, great for long notes |

For everyday voice notes, `base` is fine; reach for `medium` or
`large-v3-turbo` when accuracy matters or the audio is noisy.

## Use it from Claude (MCP)

voxscribe ships an [MCP](https://modelcontextprotocol.io) server so Claude can
transcribe audio for you — "transcribe this voice note" just works, the file
never leaves your machine.

Install with the `mcp` extra so the `voxscribe-mcp` command is on your PATH:

```bash
pipx install "voxscribe[mcp]"     # recommended (keeps it on PATH)
# or
pip install "voxscribe[mcp]"
```

It exposes two tools:

| Tool | Description |
| --- | --- |
| `transcribe` | Transcribe a local audio file (`path`, `language`, `model`, `format`, `translate`) |
| `list_models` | List available models and their size / quality trade-offs |

### Claude Code

```bash
claude mcp add voxscribe -- voxscribe-mcp
```

Then just ask: *"transcribe ~/Downloads/note.opus in French"*.

### Claude Desktop

Add this to `claude_desktop_config.json`
(macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "voxscribe": {
      "command": "voxscribe-mcp"
    }
  }
}
```

Restart Claude Desktop and the **voxscribe** tools appear in the 🔌 menu.

> Uses the stdio transport, so it works in any MCP-compatible client.

## How it works

1. `ffmpeg` converts the input to 16 kHz mono WAV (what whisper.cpp expects).
2. whisper.cpp runs the model and emits the chosen format.
3. voxscribe hands you the text.

Everything runs offline on your CPU/GPU.

## License

[MIT](LICENSE) © SanYann
