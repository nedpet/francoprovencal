import re
import os

CHAPTER_START = 1
CHAPTER_END = 33

# identifies the word with the match
def find_word(line: str, match) -> tuple[str, int]:
    start, end = match.span()
    while line[end] not in [" ", "\n"]:
        end += 1
    if line[start] == " ":
        start += 1
    while line[start - 1] != " " and start > 0:
        start -= 1
    return line[start:end], end

# adds matches in this line to the found set
def process_line(line: str, regex: str, found: set[str], exclude_propers):
    match = re.search(regex, line)
    while line != "" and match is not None:
        word, new_start = find_word(line, match)
        if word not in found and (not exclude_propers or word[0].islower()):
            found.add(word)
        line = line[new_start:]
        match = re.search(regex, line)

# returns a set of matches in this chapter
def process_chapter(num: int, regex: str, exclude_propers) -> set[str]:
    found_words = set()
    with open(f"stripped/chapter{num}.txt", "r", encoding="utf-8-sig") as f:
        line = f.readline()
        while (line != ""):
            process_line(line, regex, found_words, exclude_propers)
            line = f.readline()
    return found_words

def main(regex: str, exclude_propers):
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    chapter_matches = []
    for i in range(CHAPTER_START, CHAPTER_END + 1):
        found_words = process_chapter(i, regex, exclude_propers)
        chapter_matches.append((i, len(list(found_words)), found_words))
    chapter_matches.sort(key=lambda i: i[1], reverse=True)
    print("Chapter\tTokens\tList")
    printed_something = False
    for i in range(CHAPTER_START - 1, CHAPTER_END):
        if chapter_matches[i][1] == 0:
            continue
        printed_something = True
        print(f"{chapter_matches[i][0]}\t{chapter_matches[i][1]}\t{chapter_matches[i][2]}")
    if not printed_something:
        print("None")

if __name__ == "__main__":
    regex = r'[^aeouàâäéèì]illi'
    exclude_propers = False
    main(regex, exclude_propers)