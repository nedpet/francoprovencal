""" splits context.txt into the different txt files for each chapter
"""

import os
from num2words import num2words

def to_roman(num):
    values = [
        (1000, 'M'), (900, 'CM'), (500, 'D'), (400, 'CD'),
        (100, 'C'),  (90, 'XC'),  (50, 'L'),  (40, 'XL'),
        (10, 'X'),   (9, 'IX'),   (5, 'V'),   (4, 'IV'), (1, 'I')
    ]
    result = ''
    for value, numeral in values:
        while num >= value:
            result += numeral
            num -= value
    return result

def process_line(line: str, strip_punc: bool) -> str:
    if strip_punc:
        line = ''.join(c for c in line if c.isalnum() or c in [" ", "\n", "\t"])
    i = 0
    while i < len(line):
        if line[i].isdigit():
            j = i + 1
            while j < len(line) and line[j].isdigit():
                j += 1
            remaining = line[j:]
            line = line[:i] + "\n" + num2words(int(line[i:j]), lang='fr') + "\n" + remaining
            i = line.find(remaining)
        else:
            i += 1
    return line

if __name__ == "__main__":

    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    num = 0

    for i in range(0, 21, 1):
        open(f"raw/chapter{num}.txt", "w", encoding="utf-8-sig").close()
        open(f"stripped/chapter{num}.txt", "w", encoding="utf-8-sig").close()

    with open("content.txt", 'r', encoding="utf-8-sig") as f:
        while (num < 21):
            with open(f"raw/chapter{num}.txt", "a", encoding="utf-8-sig") as f2:
                with open(f"stripped/chapter{num}.txt", "a", encoding="utf-8-sig") as f3:
                    line = f.readline()
                    if line == '':
                        break
                    if line == f"{to_roman(num + 1)}\n":
                        num += 1
                    else:
                        f2.write(process_line(line, False))
                        f3.write(process_line(line, True))
