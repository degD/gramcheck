# GRAMCHECK
A Python script to check a given text for grammer mistakes by using online AI tools. 

## Disclaimer
This script has written for educational purpuoses only. It utilizes [duck.ai](duck.ai)
under the hood, which doesn't violate the [ToS](https://duckduckgo.com/duckai/privacy-terms).
Still, this might change in the future. Use at your own risk.

## How to Install?
1. You need to install Python3.12
2. Create a Python venv: `python -m venv .venv && source .venv/bin/activate`
3. Install [duck_chat](https://github.com/mrgick/duck_chat)

## How to use?
1. Activate venv: `source .venv/bin/activate`
2. Run: `chmod +x gc`
3. Run: `./gc [FILE]` to grammer check a file, or `./gc -t [TEXT]` to grammer check text.
4. For more information, run: `./gc --help`

## Troubleshooting
If running `gc` crashes with the error `ERR_CHALLENGE`, you may need to do a small modification to 
[duck_chat](https://github.com/mrgick/duck_chat) source code, as this modification hasn't merged yet.
1. Navigate to the duck_chat source code with `cd .venv/lib/python3.12/site-packages/duck_chat`
2. Open `api.py` with your favourite editor, like `vim api.py`
3. At the line `29`, there is a `headers` dictionary. Insert `"x-vqd-4": ""` inside it.
4. Save the file. Now the script should work.
