# convert content_ipa.txt to only the ipa, with no whitespace or chapter breaks

import os

# eliminates all numbers and also rids the line of any text within the parentheses
def process_line(line: str) -> str:
    line = "".join([char for char in line if char.isalpha() or char in [' ', '(', ')', '\n']])
    while line.find('(') != -1:
        opening = line.find('(')
        closing = line.find(')')
        if closing == -1:
            return line[:opening]
        elif closing < opening:
            return line[closing + 1:]
        else:
            line = line[:opening] + line[closing + 1:]
    return line

def run():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    with open("content_ipa.txt", "r", encoding="utf-8-sig") as f:
        with open("only_ipa.txt", "w", encoding="utf-8-sig") as f2:
            line = f.readline()
            i = 0
            while (line != ""):
                if len(line) > 10 and 174 <= i <= 3312:
                    f2.write(process_line(line))
                line = f.readline()
                i += 1

if __name__ == "__main__":
    run()
    
