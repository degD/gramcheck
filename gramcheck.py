import argparse
import json
import os
import sys
import urllib.parse as urlparse

import dotenv
import requests
from colored import Fore


def get_config_env_path() -> str:
    project_root = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(project_root, ".env")


SEED = 4224442
_GC_SERVER_URL_PROVIDED = True
CONFIG_ENV_PATH = get_config_env_path()
dotenv.load_dotenv(CONFIG_ENV_PATH)
_GC_SERVER_URL = os.getenv('_GC_SERVER_URL')
if _GC_SERVER_URL is None: _GC_SERVER_URL = ''
HEALTH_URL = urlparse.urljoin(_GC_SERVER_URL, 'health')
COMPLETION_URL = urlparse.urljoin(_GC_SERVER_URL, 'completion')

try:
    if requests.head(str(HEALTH_URL)).status_code == 200:
        _GC_SERVER_URL_PROVIDED = True
    else: 
        _GC_SERVER_URL_PROVIDED = False
except:
    _GC_SERVER_URL_PROVIDED = False

system_prompt = "You are a tool made for language teaching. Check the text given by the user sentence by sentence for syntactic and semantic errors. Strictly avoid any greetings or filler."
file_read_error = "Unable to read from file. Please try again."
number_error = 'Text number "-n" is not an integer.'
number_range_error = "The number specified is not in the range of number of texts in file (counting starts from 0)."


post_req = {
    'prompt': system_prompt,
    'seed': SEED,
    'stream': False,    # TODO: Stream in future

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


def text_grammar_check(text: str):
    data = post_req.copy()
    data['prompt'] += '\n\n' + text  # ty: ignore[unsupported-operator]
    r = requests.post(
        COMPLETION_URL,
        json.dumps(data)
    )
    s = r.content.decode().strip()
    s = json.loads(s)['content']
    return s


def flatten_list(l: list):
    l_flat = []
    count = 0
    for l_inner in l:
        if isinstance(l_inner, list):
            count += 1
            l_flat.extend(l_inner)
    if count == 0:
        return l
    else:
        return flatten_list(l_flat)


def parse_long_text(text: str):
    word_count = len(text.split())
    if word_count < 40_000:
        return text
    else:
        text_first_half = " ".join(text.split()[: word_count // 2])
        text_second_half = " ".join(text.split()[word_count // 2 :])
        return flatten_list(
            [parse_long_text(text_first_half), parse_long_text(text_second_half)]
        )


def parse_file_text(file_text: str):
    texts = []
    for text in file_text.splitlines():
        if text:
            texts.append(parse_long_text(text))
    return texts


def parse_only_file_text(file_text: str):
    texts = []
    for text in file_text.splitlines():
        if text:
            texts.append(text)
    return texts


def read_from_file(path: str):
    with open(path) as fp:
        file_text = "".join(fp.readlines())
        return file_text


def main(texts: list[str]):
    responses = []
    print(texts)
    for text in texts:
        responses.append(text_grammar_check(text))

    for i in range(len(texts)):
        print("\n" + "#" * os.get_terminal_size().columns + "\n")
        print(f"{Fore.red}{texts[i]}\n\n{Fore.green}{responses[i]}{Fore.white}")
    print("\n" + "#" * os.get_terminal_size().columns + "\n")


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

    if _GC_SERVER_URL_PROVIDED:
        if not args.text and not args.file:
            parser.print_help()
            sys.exit(0)
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
    else:
        parser.error(
            "No server URL key was provided. Please pass a valid URL using --set-server-url"
        )

    if args.text:
        texts = parse_file_text(args.text)
    else:
        try:
            file_text = read_from_file(args.file)
        except:
            sys.stderr.write(file_read_error + "\n")
            sys.exit(1)

        if args.number is not None:
            file_texts = parse_only_file_text(file_text)
            if args.number < 0 or args.number >= len(file_texts):
                sys.stderr.write(number_range_error + "\n")
                sys.exit(3)
            file_text = file_texts[args.number]
            texts = parse_file_text(file_text)
        elif args.all:
            text_or_texts = parse_long_text(file_text)
            texts = (
                text_or_texts if isinstance(text_or_texts, list) else [text_or_texts]
            )
        else:
            texts = parse_file_text(file_text)
    main(texts)


if __name__ == "__main__":
    cli()
