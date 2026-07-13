import os
import sys


def get_bytes(file_path):
    try:
        return os.path.getsize(file_path)
    except Exception:
        print(f"wc: {file_path}: No such file or directory")
        return None


def get_lines(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as fp:
            return sum(1 for line in fp)
    except Exception:
        print(f"wc: {file_path}: No such file or directory")
        return None


def get_words(file_path):
    try:
        count = 0
        with open(file_path, "r", encoding="utf-8") as fp:
            data = fp.read()
            words = data.split()
            count += len(words)
            return count
    except Exception:
        print(f"wc: {file_path}: No such file or directory")
        return None


def main():
    result = get_words("test.txt")
    if result is not None:
        print(result)
    print(sys.argv)


if __name__ == "__main__":
    main()
