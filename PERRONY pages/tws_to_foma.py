import os
import subprocess
from foma import FST

def foma_line(line: str, fst: FST) -> str:
    line_lst = line.split("\t")
    line_lst[3] = next(fst.apply_down(line_lst[3][:-1]), None)
    return "\t".join(line_lst) + "\n"

def foma_file(filename: str, fst: FST):
    with open(f"perrony_extracted/{filename}", "r", encoding="utf-8-sig") as input_file:
        with open(f"perrony_ipa/{filename}", "w", encoding="utf-8-sig") as output_file:
            line = input_file.readline()
            while line != "":
                output_file.write(foma_line(line, fst))
                line = input_file.readline()

def run(wav_files_exist: bool = False):
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    subprocess.run(['foma', '-e', 'source g2p.foma', '-e', 'save stack g2p.fomabin', '-e', 'quit'])
    fst = FST.load('g2p.fomabin')

    for i in range(1, 34, 1):
        if i in {21, 23, 26, 31}:
            continue
        foma_file(f"chapter{i}.tws", fst)
        if not wav_files_exist:
            subprocess.run(['cp', f"perrony_extracted/chapter{i}.wav", 'perrony_ipa'])

if __name__ == "__main__":
    run(True)