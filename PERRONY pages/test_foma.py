# 

import os
import subprocess
import re
from foma import FST

def process_line(line: str, d: dict[str, str]):
    fst = FST.load('g2p.fomabin')
    line = "".join([char for char in line if char.isalpha() or char in ['(', ')', '[', ']', ' ']])
    if line == "":
        return
    line_lst = line.strip().split(" ")
    for word in line_lst:
        if word == "" or not word.isascii():
            continue
        results = list(fst.apply_down(word.lower()))
        if results is None:
            continue
        word_ipa = results[0]
        if not re.search("[^(\\t)0123456789.(Sentence)pbt(tː)dkgmnɲfvsSzʃʒʁwljʎ(t͡s)(d͡z)(t͡ʃ)(d͡ʒ)iyueəøoɛaø̃õɛ̃œ̃ã ]", word_ipa) is None:
            if word[0].isupper() or any((char in word) for char in ['(', ')', '[', ']']) or word in d:
                continue
            d[word] = word_ipa
            print(f"{word}: {word_ipa}")

def run():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    subprocess.run(['foma', '-e', 'source g2p.foma', '-e', 'save stack g2p.fomabin', '-e', 'quit'])
    

    d = {}
    with open("content.txt", "r", encoding="utf-8-sig") as f:
        line = f.readline()
        i = 0
        while (line != ""):
            if 174 <= i <= 3312:
                process_line(line, d)
            line = f.readline()
            i += 1
    
    # for word in d:
    #     print(f"{word}: {d[word]}")

if __name__ == "__main__":
    run()
    
