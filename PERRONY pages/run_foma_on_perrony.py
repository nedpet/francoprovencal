import foma
import os

def process_line(line: str) -> int:
    f = foma.FST.load('g2p.foma')
    line = "".join(char for char in line if char.isalpha() or char == ' ')
    line_lst = line.split(" ")
    all_words = []
    for word in line_lst:
        all_words.append(f.apply_down(word))
    return all_words

def count_words() -> tuple[int, int]:
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    all_words = []
    with open("content.txt", "r", encoding="utf-8-sig") as f:
        line = f.readline()
        while (line != ""):
            all_words += process_line(line)
            line = f.readline()
    return count, correct_count

if __name__ == "__main__":
    result = count_words()
    print(result[0])
    print(result[1])