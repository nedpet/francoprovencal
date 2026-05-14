#!/home/nedpet/foma-env/bin/python

from foma import FST
import os
import subprocess

def preserve_parentheses(line: str) -> str:
    i = 0
    while i < len(line):
        if line[i] == '(':
            j = i
            while j < len(line) and line[j] != ')':
                if line[j] == ' ':
                    line = line[:j] + "+" + line[j+1:]
                j += 1
            i = j
        i += 1
    return line

def process_line(line: str, f: FST) -> str:
    line = "".join(char.lower() for char in line if char.isalnum() or char in [' ', '(', ')'])
    line = preserve_parentheses(line)

    line_lst = [word for word in line.split(" ") if word != '']
    new_line = ""
    for word in line_lst:
        if word[0] == '(' and word[-1] == ')':
            new_line += " " + word
        elif word.isnumeric():
            new_line += " " + word
        else:
            new_line += " " + "".join(f.apply_down(word))
    return new_line.replace("+", " ") + "\n"

def foma_words():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    subprocess.run(['foma', '-e', 'source g2p.foma', '-e', 'save stack g2p.fomabin', '-e', 'quit'])
    fst = FST.load('g2p.fomabin')
    with open("content.txt", "r", encoding="utf-8-sig") as f:
        with open("content_ipa.txt", "w", encoding="utf-8-sig") as f2:
            line = f.readline()
            while (line != ""):
                f2.write(process_line(line, fst))
                line = f.readline()

if __name__ == "__main__":
    result = foma_words()
    