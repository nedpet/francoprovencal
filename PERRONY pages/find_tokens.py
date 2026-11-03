import re
import os
import pympi
from dataclasses import dataclass

CHAPTER_START = 1
CHAPTER_END = 33
MISSING_CHAPTERS = [21, 23, 26, 31]

@dataclass
class FoundWord:
    word: str
    chapter: int
    start: float
    end: float

# identifies the word with the match
def identify_word(line: str, match) -> tuple[str, int]:
    start, end = match.span()
    while line[end] not in [" ", "\n"]:
        end += 1
    if line[start] == " ":
        start += 1
    while line[start - 1] != " " and start > 0:
        start -= 1
    return line[start:end], end

# returns the timestamp (minutes, seconds) of this word in this chapter
def find_word_in_eaf(word: str, chapter: int) -> tuple[int, int]:
    if chapter in MISSING_CHAPTERS or chapter < CHAPTER_START or chapter > CHAPTER_END:
        return None
    eaf = pympi.Elan.Eaf(f'aligned_audios/chapter{chapter}.eaf')
    for start, end, value in eaf.get_annotation_data_for_tier("Word"):
        if value == word:
            return start, end
    return None

# adds matches in this line to the found set
def process_line(chapter: int, line: str, regex: str, found: list[FoundWord], exclude_propers: bool):
    match = re.search(regex, line)
    while line != "" and match is not None:
        word, new_start = identify_word(line, match)
        if word not in [foundword.word for foundword in found] and (not exclude_propers or word[0].islower()):
            result = find_word_in_eaf(word, chapter)
            if result is not None:
                start, end = result
                found_word = FoundWord(word, chapter, start, end)
                found.append(found_word)
        line = line[new_start:]
        match = re.search(regex, line)

# adds the set of matches in this chapter to found words
def process_chapter(num: int, regex: str, exclude_propers: bool, found_words: list[FoundWord]):
    with open(f"stripped/chapter{num}.txt", "r", encoding="utf-8-sig") as f:
        line = f.readline()
        while (line != ""):
            process_line(num, line, regex, found_words, exclude_propers)
            line = f.readline()

def ms_to_min_sec(ms: float) -> tuple[int, float]:
    return ms // 1000 // 60, ms % 1000

def main(regex: str, exclude_propers: bool):
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    found_words = []
    for i in range(CHAPTER_START, CHAPTER_END + 1):
        process_chapter(i, regex, exclude_propers, found_words)
    print("Word\tChapter\tTimestamp")
    for word in found_words:
        start_time, end_time = ms_to_min_sec(word.start), ms_to_min_sec(word.end)
        print(f"{word.word}\t{word.chapter}\t{start_time[0]}:{start_time[1]} to {end_time[0]}:{end_time[1]}")

if __name__ == "__main__":
    regex = r'[^aeouàâäéèì]illi'
    exclude_propers = False
    main(regex, exclude_propers)