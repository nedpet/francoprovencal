# takes an eaf file in aligned_audios and its "Word" transcription tier, then
# creates a new tier "FOMA" which are the words in IPA according to g2p and p2p

import pympi
import os
import subprocess
from foma import FST
from choose_foma import choose

# grapheme to phone
def grapheme_to_phone(word: str, g2p: FST, p2p: FST) -> str:
    phonemic = choose(list(g2p.apply_down(word)))
    if phonemic != "":
        return choose(list(p2p.apply_down(phonemic)))
    return ""

# takes a single chapter and adds the ipa tier
def foma_file(chapter: int):
    FST.decode = lambda self, text: text.decode('utf-8-sig', errors='ignore')
    g2p = FST.load('g2p.fomabin')
    p2p = FST.load('p2p.fomabin')

    filepath = f"aligned_audios/chapter{chapter}.eaf"
    eaf = pympi.Elan.Eaf(filepath)

    if "FOMA" in eaf.get_tier_names():
        eaf.remove_tier("FOMA")
    eaf.add_tier("FOMA")
    words = eaf.get_annotation_data_for_tier("Word")

    for start, end, value, *_ in words:
        eaf.add_annotation("FOMA", start, end, grapheme_to_phone(value.lower(), g2p, p2p))

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

    # subprocess.run(['foma', '-e', 'source g2p.foma', '-e', 'save stack g2p.fomabin', '-e', 'quit'])
    # subprocess.run(['foma', '-e', 'source p2p.foma', '-e', 'save stack p2p.fomabin', '-e', 'quit'])
    # FST.decode = lambda self, text: text.decode('utf-8-sig')
    # g2p = FST.load('g2p.fomabin')
    # p2p = FST.load('p2p.fomabin')
    # print(grapheme_to_phone("catchayes", g2p, p2p))