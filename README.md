# GRAMCHECK
This is a Python script to check a given text for grammar mistakes by using online LLMs. 

## Disclaimer
This script has been written for educational purposes only. It utilizes [Google AI Studio](https://aistudio.google.com/) under the hood. To use this tool, you have to provide your own API key. You can create an API key for free, without even adding a billing address.

## How to Install?
1. Install the [`uv`](https://docs.astral.sh/uv/) project manager.
2. Clone the project and run `uv sync` to install packages.
3. Run `echo GEMINI_API_KEY=<YOUR_API_KEY_HERE> > .env`. 

## How to use?
1. Run: `chmod +x grc`.
2. Create a symbolic link: `ln -s -T /path/to/gramcheck/grc /path/to/link/grc`.
4. For command information, run: `grc --help`.
5. As an example, run `./grc example.txt`.