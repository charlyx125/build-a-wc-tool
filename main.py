import sys

def get_bytes(content):
    return len(content)  # bytes = number of raw bytes

def get_chars(content):
    return len(content.decode("utf-8"))

def get_lines(content):
    return content.decode("utf-8").count("\n")  # lines = number of newline characters

def get_words(content):
    return len(content.decode("utf-8").split())  # words = pieces split on whitespace


def read_content(files):
    if files:
        try:
            with open(files[0], "rb") as fp:
                return fp.read()
        except FileNotFoundError:
            print(f"ccwc: {files[0]}: No such file or directory")
            sys.exit(1)
    return sys.stdin.buffer.read()


def main():
    args = sys.argv[1:]
    flags = [a for a in args if a.startswith("-")]
    files = [a for a in args if not a.startswith("-")]

    content = read_content(files)

    handlers = {"-l": get_lines, "-w": get_words, "-c": get_bytes, "-m": get_chars}

    selected = flags if flags else ["-l", "-w", "-c"]

    results = [
        f"{handlers[f](content)}"
        if f in handlers.keys()
        else f"ccwc : {f} invalid option\n"
        for f in selected
    ]
    print(" ".join(results))


if __name__ == "__main__":
    main()
