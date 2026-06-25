# voxscribe

Transcribe voice notes — WhatsApp `.opus`, `.mp3`, `.m4a`, `.ogg`, anything `ffmpeg` reads — **locally**, on your machine, with [whisper.cpp](https://github.com/ggerganov/whisper.cpp). No cloud, no API keys, no audio leaving your laptop.

It started as a one-off: a friend sent a 1-minute WhatsApp voice note and asked "can you transcribe this?". This is that, packaged.

```console
$ voxscribe "WhatsApp Audio 2026-06-23.opus" -l fr
Et donc en fait, tous les ans, avant le 30 juin, il faut déposer les comptes auprès du greffe...
```

## Install

voxscribe wraps two native tools — install them first:

| Platform | ffmpeg | whisper.cpp |
| --- | --- | --- |
| macOS (Homebrew) | `brew install ffmpeg` | `brew install whisper-cpp` |
| Debian / Ubuntu | `sudo apt install ffmpeg` | [build from source](https://github.com/ggerganov/whisper.cpp) |

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

## How it works

1. `ffmpeg` converts the input to 16 kHz mono WAV (what whisper.cpp expects).
2. whisper.cpp runs the model and emits the chosen format.
3. voxscribe hands you the text.

Everything runs offline on your CPU/GPU.

## License

[MIT](LICENSE) © SanYann
