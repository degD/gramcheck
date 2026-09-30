# GRAMCHECK

A Python tool to check text for grammar mistakes using local LLMs.
It connects to any OpenAI-compatible server (e.g. `llama-server`) and
streams corrections back as they are generated.

Because of the probabilistic nature of LLMs, results may or may not be
correct. Take them with a grain of salt. Results are generated using a
predefined seed to keep them consistent.

Currently does not support API keys. Future versions will plan API keys
to enable support for online providers. Example tests are also planned
for future versions.

## Requirements

- Python 3.8+
- A running `llama-server` (or any OpenAI-compatible endpoint)
- A capable instruction-tuned model. Recommended: Q4 or higher
  quantization. Q2 quants and sub-4B models often fail to follow the
  output format.

## Install

1. Install from PyPI: `pipx install gramcheck`.
2. Point it at your server:
   `gramcheck --set-server-url http://127.0.0.1:8080`
   (writes `_GC_SERVER_URL` to `.env` in the project directory).

## Usage

1. Check a file: `gramcheck example.txt`.
2. Check a single text: `gramcheck -t 'Your text here'`.
3. Check the Nth line in a file: `gramcheck example.txt -n 0`
   (0-based, so `-n 0` is the first line).
4. Check a file as a whole: `gramcheck example.txt -a`.
5. Show help: `gramcheck --help`.

## Output

Each text is printed in red, followed by the model's corrections in green.
Corrections are one line per error in the form `original -> corrected`.
If a text has no errors, the model outputs `OK`.

## Development

1. Install the [`uv`](https://docs.astral.sh/uv/) project manager.
2. Clone the repository:
   `git clone https://github.com/degD/gramcheck` and run `uv sync`.
3. Point it at your server:
   `gramcheck --set-server-url http://127.0.0.1:8080`
   (or edit `.env` directly).
4. Run locally with `python gramcheck.py`
   (or `./gramcheck` on Unix-like systems).

## Supported servers

Any endpoint that implements the OpenAI Chat Completions API
(`/v1/chat/completions`) with streaming SSE. Tested with `llama-server`
from [`llama.cpp`](https://github.com/ggml-org/llama.cpp).

See the [documentation](https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md) for `llama-server`-specific configuration.

## License

MIT