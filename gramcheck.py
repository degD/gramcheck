from colored import Fore
import argparse
import sys
import os
import dotenv
from google import genai

dotenv.load_dotenv()
client = genai.Client()

file_read_error = "Unable to read from file. Please try again."

number_error = "Text number \"-n\" is not an integer."

number_range_error = "The number specified is not in the range of number of texts in file (counting starts from 0)."

def build_arg_parser() -> argparse.ArgumentParser:
    return argparse.ArgumentParser(
        prog="grc",
        description=(
            "Read lines from FILE and check them for grammatical errors using LLMs.\n"
            "Or grammar check TEXT with \"-t\" option.\n"
            "To check NUMBERth text in FILE, use the \"-n\" option.\n"
            "To check FILE as a whole, use option \"-a\"."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

def parse_text_number(value: str) -> int:
    try:
        return int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(number_error) from exc

def text_grammer_check(text: str):
    prompt = "You are a tool made for language teaching. Check the text given by the user sentence by sentence for syntatic and semantic errors. Avoid any greetings or fillings." + "\n\n"
    response = client.models.generate_content(
        model="gemini-3.1-flash-lite",
        contents=prompt + text
    )
    return response.text
        
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
        text_first_half = " ".join(text.split()[:word_count//2])
        text_second_half = " ".join(text.split()[word_count//2:])
        return flatten_list([parse_long_text(text_first_half), parse_long_text(text_second_half)])

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
    for text in texts:
        responses.append(text_grammer_check(text))

    for i in range(len(texts)):
        print("\n" + "#" * os.get_terminal_size().columns + "\n")
        print(f"{Fore.red}{texts[i]}\n\n{Fore.green}{responses[i]}{Fore.white}")
    print("\n" + "#" * os.get_terminal_size().columns + "\n")

if __name__ == "__main__":
    parser = build_arg_parser()
    parser.add_argument("file", nargs="?", help="File to read")
    parser.add_argument("-t", "--text", help="Text to check")
    parser.add_argument(
        "-n",
        "--number",
        type=parse_text_number,
        help="Check NUMBERth text in FILE (0-based)",
    )
    parser.add_argument(
        "-a",
        "--all",
        action="store_true",
        help="Check FILE as a whole",
    )

    args = parser.parse_args()

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
            texts = text_or_texts if isinstance(text_or_texts, list) else [text_or_texts]
        else:
            texts = parse_file_text(file_text)

    main(texts)
