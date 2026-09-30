import argparse
import json
import os
import shutil
import sys
import urllib.parse as urlparse

import dotenv
import requests
from colorama import Fore, Style, just_fix_windows_console

just_fix_windows_console()


def get_config_env_path() -> str:
    project_root = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(project_root, ".env")


CONTEXT_LEN = 4000
SEED = 4224442
_GC_SERVER_URL_PROVIDED = True
CONFIG_ENV_PATH = get_config_env_path()
dotenv.load_dotenv(CONFIG_ENV_PATH)
_GC_SERVER_URL = os.getenv('_GC_SERVER_URL')
if _GC_SERVER_URL is None:
    _GC_SERVER_URL = ''
if _GC_SERVER_URL and not _GC_SERVER_URL.endswith('/'):
    _GC_SERVER_URL += '/'

HEALTH_URL = urlparse.urljoin(_GC_SERVER_URL, 'health')
COMPLETION_URL = urlparse.urljoin(_GC_SERVER_URL, 'v1/chat/completions')
try:
    if requests.head(str(HEALTH_URL), timeout=3).status_code == 200:
        _GC_SERVER_URL_PROVIDED = True
    else:
        _GC_SERVER_URL_PROVIDED = False
except Exception:
    _GC_SERVER_URL_PROVIDED = False

system_prompt = "You are a tool made for language teaching. Check the text given by the user sentence by sentence for syntactic and semantic errors. Strictly avoid any greetings or filler."
file_read_error = "Unable to read from file. Please try again."
number_error = 'Text number "-n" is not an integer.'
number_range_error = "The number specified is not in the range of number of texts in file (counting starts from 0)."


post_req = {
    'messages': [
        {'role': 'system', 'content': system_prompt},
    ],
    'seed': SEED,
    'stream': True,
}


def set__GC_SERVER_URL(_GC_SERVER_URL: str) -> str:
    env_path = CONFIG_ENV_PATH
    os.makedirs(os.path.dirname(env_path), exist_ok=True)

    lines = []
    if os.path.exists(env_path):
        with open(env_path) as fp:
            lines = fp.read().splitlines()

    updated = False
    for index, line in enumerate(lines):
        if line.startswith("_GC_SERVER_URL="):
            lines[index] = f"_GC_SERVER_URL={_GC_SERVER_URL}"
            updated = True
            break
    if not updated:
        lines.append(f"_GC_SERVER_URL={_GC_SERVER_URL}")

    with open(env_path, "w") as fp:
        fp.write("\n".join(lines).rstrip("\n") + "\n")

    return env_path


def build_arg_parser() -> argparse.ArgumentParser:
    return argparse.ArgumentParser(
        prog="gramcheck",
        description=(
            "Read lines from FILE and check them for grammatical errors using LLMs.\n"
            'Or grammar check TEXT with "-t" option.\n'
            'To check Nth text in FILE, use the "-n" option.\n'
            'To check FILE as a whole, use option "-a".'
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )


def parse_text_number(value: str) -> int:
    try:
        return int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(number_error) from exc


def stream_grammar_check(text: str):
    data = post_req.copy()
    data['messages'] = post_req['messages'] + [{'role': 'user', 'content': text}]  # ty: ignore[unsupported-operator]
    r = requests.post(COMPLETION_URL, json=data, stream=True)
    r.raise_for_status()
    buffer = ''
    for chunk in r.iter_content(chunk_size=None, decode_unicode=True):
        if not chunk:
            continue
        buffer += chunk  # ty: ignore[unsupported-operator]
        while '\n' in buffer:
            line, buffer = buffer.split('\n', 1)
            line = line.strip()
            if not line or not line.startswith('data:'):
                continue
            payload = line[len('data:'):].strip()
            if payload == '[DONE]':
                return
            try:
                obj = json.loads(payload)
            except json.JSONDecodeError:
                continue
            choices = obj.get('choices') or []
            if not choices:
                continue
            content = choices[0].get('delta', {}).get('content') or ''
            if content:
                yield content


def parse_long_text(text: str) -> list[str]:
    word_count = len(text.split())
    if word_count < CONTEXT_LEN:
        return [text]
    else:
        text_first_half = " ".join(text.split()[: word_count // 2])
        text_second_half = " ".join(text.split()[word_count // 2 :])
        return parse_long_text(text_first_half) + parse_long_text(text_second_half)


def parse_file_text(file_text: str) -> list[str]:
    texts = []
    for text in file_text.splitlines():
        if text:
            texts.extend(parse_long_text(text))
    return texts


def parse_only_file_text(file_text: str) -> list[str]:
    texts = []
    for text in file_text.splitlines():
        if text:
            texts.append(text)
    return texts


def read_from_file(path: str) -> str:
    with open(path, encoding='utf-8') as fp:
        file_text = "".join(fp.readlines())
        return file_text


def main(texts: list[str]):
    for text in texts:
        separator = "\n" + "#" * shutil.get_terminal_size().columns + "\n"
        print(separator)
        print(f"{Fore.RED}{text}{Style.RESET_ALL}\n")
        print(Fore.GREEN, end="", flush=True)
        try:
            for chunk in stream_grammar_check(text):
                print(chunk, end="", flush=True)
        finally:
            print(Style.RESET_ALL, flush=True)
    print(separator)


def cli():
    parser = build_arg_parser()
    parser.add_argument("file", nargs="?", help="File to read")
    parser.add_argument("-t", "--text", help="Text to check")
    parser.add_argument(
        "-n",
        "--number",
        type=parse_text_number,
        help="Check Nth text in FILE (0-based)",
    )
    parser.add_argument(
        "-a",
        "--all",
        action="store_true",
        help="Check FILE as a whole",
    )
    parser.add_argument(
        "--set-server-url",
        metavar="KEY",
        help="Store _GC_SERVER_URL in the user config",
    )

    args = parser.parse_args()

    if args.set_server_url:
        if args.text or args.file or args.number is not None or args.all:
            parser.error("--set-server-url cannot be combined with other options")
        env_path = set__GC_SERVER_URL(args.set_server_url)
        print(f"Saved _GC_SERVER_URL to {env_path}")
        sys.exit(0)

    if not _GC_SERVER_URL_PROVIDED:
        parser.error(
            "Server URL is not set or server is not reachable. "
            "Please set a valid URL using --set-server-url"
        )

    if args.text and args.file:
        parser.error("FILE and -t/--text cannot be used together")
    if args.text and args.number is not None:
        parser.error("-n/--number cannot be used with -t/--text")
    if args.number is not None and not args.file:
        parser.error("-n/--number requires FILE")
    if args.all and not args.file:
        parser.error("-a/--all requires FILE")
    if args.all and args.text:
        parser.error("-a/--all cannot be used with -t/--text")
    if args.number is not None and args.all:
        parser.error("-n/--number and -a/--all cannot be used together")

    if not args.text and not args.file:
        parser.print_help()
        sys.exit(0)

    if args.text:
        texts = parse_long_text(args.text)
    else:
        try:
            file_text = read_from_file(args.file)
        except Exception:
            sys.stderr.write(file_read_error + "\n")
            sys.exit(1)

        if args.number is not None:
            file_texts = parse_only_file_text(file_text)
            if args.number < 0 or args.number >= len(file_texts):
                sys.stderr.write(number_range_error + "\n")
                sys.exit(3)
            file_text = file_texts[args.number]
            texts = parse_long_text(file_text)
        elif args.all:
            texts = parse_long_text(file_text)
        else:
            texts = parse_file_text(file_text)

    main(texts)


if __name__ == "__main__":
    cli()