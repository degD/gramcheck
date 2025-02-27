import asyncio
from duck_chat import DuckChat, ModelType
from colored import Fore
import sys
import os

help_msg = """
Usage: dgc [FILE] [-t TEXT] [FILE -n NUMBER]
\tRead lines from FILE and check them for grammatical errors using "duck.ai".
\tOr grammer check TEXT with "-t" option.
\tTo check NUMBERth text in FILE, use the "-n" option.  
"""

file_read_error = "Unable to read from file. Please try again."

number_error = "Text number \"-n\" is not an integer."

number_range_error = "The number specified is not in the range of number of texts in file (counting starts from 0)."

async def text_grammer_check(text: str):
    async with DuckChat(model=ModelType.Llama) as client:
        prompt = "You are a helpful assistant made for language teaching. Check the text given by the user sentence by sentence for syntatic errors." + "\n\n"
        answer = await client.ask_question(prompt + text)
        return answer
        
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

async def main(texts: list[str]):
    responses = []
    for text in texts:
        responses.append(await text_grammer_check(text))

    for i in range(len(texts)):
        print("\n" + "#" * os.get_terminal_size().columns + "\n")
        print(f"{Fore.red}{texts[i]}\n\n{Fore.green}{responses[i]}{Fore.white}")
    print("\n" + "#" * os.get_terminal_size().columns + "\n")

if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] not in ["-h", "--help", "-t"]:
        try:
            file_text = read_from_file(sys.argv[1])
        except:
            sys.stderr.write(file_read_error + "\n")
            exit(1)
    elif len(sys.argv) == 3 and sys.argv[1] == "-t":
        file_text = sys.argv[2]
    elif len(sys.argv) == 4 and sys.argv[2] == "-n":
        try:
            number_of_text = int(sys.argv[3])
        except:
            sys.stderr.write(number_error + "\n")
            print("b")
            exit(2)
        try:
            file_text = read_from_file(sys.argv[1])
            file_texts = parse_only_file_text(file_text)
        except:
            sys.stderr.write(file_read_error + "\n")
            exit(1)
        if number_of_text < 0 or number_of_text >= len(file_texts):
            sys.stderr.write(number_range_error + "\n")
            exit(3)
        else:
            file_text = file_texts[number_of_text]
    else:
        print(help_msg)
        exit(0)

    texts = parse_file_text(file_text)
    texts = texts
    asyncio.run(main(texts))
