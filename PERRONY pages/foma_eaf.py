import pympi
import os
import subprocess
from foma import FST

def foma_file(chapter: int):
    filepath = f"aligned_audios/chapter{chapter}.eaf"
    g2p = FST.load('g2p.fomabin')
    p2p = FST.load('p2p.fomabin')

    eaf = pympi.Elan.Eaf(filepath)
    eaf.add_tier("FOMA")
    words = eaf.get_annotation_data_for_tier("Word")

    for start, end, value, *_ in words:
        phonemic = next(g2p.apply_down(value), "")
        if phonemic != "":
            phonetic = next(p2p.apply_down(phonemic), "")
        else:
            phonetic = ""
        eaf.add_annotation("FOMA", start, end, phonetic)
        print(f"value: '{value}', '{phonetic}'")

    eaf.to_file(filepath)
    

def run():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    subprocess.run(['foma', '-e', 'source g2p.foma', '-e', 'save stack g2p.fomabin', '-e', 'quit'])
    subprocess.run(['foma', '-e', 'source p2p.foma', '-e', 'save stack p2p.fomabin', '-e', 'quit'])

    foma_file(1)
    # for i in range(1, 34, 1):
    #     if i in {10, 21, 23, 26, 31}:
    #         continue
    #     foma_file(i)

if __name__ == "__main__":
    run()