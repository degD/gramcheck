# GRAMCHECK
A Python script to check a given text for grammer mistakes by using online LLMs. 

## Disclaimer
This script has written for educational purpuoses only. It utilizes [Google AI Studio](https://aistudio.google.com/) under the hood. To use this tool, you have to bring your own API key. You can create an API key for free, without even adding a billing address.

## How to Install?
1. Install [`uv`](https://docs.astral.sh/uv/) project manager.
2. Clone project and run `uv sync` to install packages.
3. Run `echo GEMINI_API_KEY=<YOUR_API_KEY_HERE> > .env`. 

## How to use?
1. Run: `chmod +x grc`.
2. Create a symbolic link: `ln -s -T /path/to/gramcheck/grc /path/to/link/grc`.
3. Run: `./grc [FILE]` to grammer check a file where each line corresponds to a text, or `./gc -t [TEXT]` to grammer check a single text.
4. For more information, run: `./grc --help`.
5. As an example, run `./grc example.txt`.