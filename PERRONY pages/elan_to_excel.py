# from stupid elan tab-delimited format to readable excel format!

# file > export as > tab-delimited text
# check: tiers Word Orth, Adriana, Silas, Eliana
# exclude participant names from output
# include time column for begin time only
# include time format in ss.msec

import os
import subprocess
from foma import FST

def build_arrs(filename: str):
    words = []
    adriana = []
    eliana = []
    silas = []

    with open(filename, "r", encoding="utf-8-sig") as f:
        line = "".join([char for char in f.readline() if char != "\n"])
        while line != "":
            line_lst = line.split('\t')
            match line_lst[0]:
                case "Word Orth":
                    words.append((line_lst[2], line_lst[1]))
                case "Eliana":
                    eliana.append((line_lst[2], line_lst[1]))
                case "Silas":
                    silas.append((line_lst[2], line_lst[1]))
                case "Adriana":
                    adriana.append((line_lst[2], line_lst[1]))
            line = "".join([char for char in f.readline() if char != "\n"])
    return words, adriana, eliana, silas

def extract_min(words, adriana, eliana, silas, fst: FST) -> str:
    do_foma = False
    lsts = [lst for lst in [words, adriana, eliana, silas] if len(lst) != 0]
    
    min_time = min([lst[0][1] for lst in lsts])
    line = ""

    if len(words) != 0 and words[0][1] == min_time:
        word = words.pop(0)[0]
        line += word
        do_foma = True
    line += '\t'

    line += min_time + '\t'

    if len(adriana) != 0 and adriana[0][1] == min_time:
        line += adriana.pop(0)[0]
    line += '\t'
    
    if len(eliana) != 0 and eliana[0][1] == min_time:
        line += eliana.pop(0)[0]
    line += '\t'

    if len(silas) != 0 and silas[0][1] == min_time:
        line += silas.pop(0)[0]
    line += '\t'

    if do_foma:
        line += "".join(fst.apply_down(word.lower()))
    
    return line + '\n'

def write_file(words, adriana, eliana, silas, fst: FST, filename: str = "output.txt"):
    with open(filename, "w", encoding="utf-8-sig") as f:
        f.write("Word\tTiming\tAdriana\tEliana\tSilas\tFOMA\n")
        while any([len(lst) != 0 for lst in [words, adriana, eliana, silas]]):
            f.write(extract_min(words, adriana, eliana, silas, fst))


if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    subprocess.run(['foma', '-e', 'source g2p.foma', '-e', 'save stack g2p.fomabin', '-e', 'quit'])
    fst = FST.load('g2p.fomabin')
    words, adriana, eliana, silas = build_arrs("merged_chapter_10.txt")
    write_file(words, adriana, eliana, silas, fst)
    



    
    
                
        

