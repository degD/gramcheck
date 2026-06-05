# GRAMCHECK
This is a Python tool to check text for grammar mistakes using online LLMs. It uses [Google AI Studio](https://aistudio.google.com/) under the hood. You must provide your own API key.

## Install
1. Install from PyPI: `pipx install gramcheck`.
2. Set your API key: `gramcheck --set-api-key <YOUR_API_KEY_HERE>` (writes to `.env` in the project directory).

## Usage
1. Check a file: `gramcheck example.txt`.
2. Check a single text: `gramcheck -t "Your text here"`.
3. Check the Nth line in a file: `gramcheck example.txt -n 0`.
4. Check a file as a whole: `gramcheck example.txt -a`.
5. Show help: `gramcheck --help`.

## Development
1. Install the [`uv`](https://docs.astral.sh/uv/) project manager.
2. Clone the project and run `uv sync`.
3. Set your API key in `.env` as shown above.
4. Run locally with `python gramcheck.py` or `./gramcheck`.