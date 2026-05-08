""" counts the number of words in parentheses in context.txt and also outputs them
"""

import os

def process_line(line: str) -> int:
    line_lst = line.split("(")
    count = 0
    all_words = []
    for i in range(1, len(line_lst)):
        line_lst[i] = line_lst[i][:line_lst[i].find(")")]
        words = line_lst[i].split(" ")
        count += len(words)
        all_words += words
    return count, all_words

def count_words() -> tuple[int, list[str]]:
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    count = 0
    all_words = []
    with open("content.txt", "r", encoding="utf-8-sig") as f:
        line = f.readline()
        while (line != ""):
            processed = process_line(line)
            count += processed[0]
            all_words += processed[1]
            line = f.readline()
    return count, all_words

if __name__ == "__main__":
    result = count_words()
    print(result[1])
    print(result[0])