# from stupid elan tab-delimited format to readable excel format!
import os

def build_arrs(filename: str):
    words = []
    adriana = []
    eliana = []
    silas = []

    with open(filename, "r") as f:
        line = f.readline()
        line_lst = line.split('\t')
        switch (line_lst):
            case "Word Orth":
                words.append((line_lst[2], line_lst[1]))
            case "Eliana":
                eliana.append((line_lst[2], line_lst[1]))
            case "Silas":
                silas.append((line_lst[2], line_lst[1]))
            case "Adriana":
                adriana.append((line_lst[2], line_lst[1]))
    return words, adriana, eliana, silas

def extract_min(words, adriana, eliana, silas) -> str:
    lsts = [lst for lst in [words, adriana, eliana, silas] if len(lst) != 0]

    min_time = min(lst[0][1] for lst in lsts)
    line = ""

    if words in lsts and words[0][1] == min_time:
        line += words.pop(0)
    line += '\t'

    if adriana in lsts and adriana[0][1] == min_time:
        line += adriana.pop(0)
    line += '\t'
    
    if eliana in lsts and eliana[0][1] == min_time:
        line += eliana.pop(0)
    line += '\t'

    if silas in lsts and silas[0][1] == min_time:
        line += silas.pop(0)
    
    return line + '\n'


if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    filename = input("filename: ")
    words, adriana, eliana, silas = build_arrs(filename)

    with open("output.txt", "w") as f:
        while any([len(lst) != 0 for lst in [words, adriana, eliana, silas]])
            f.write(extract_min(words, adriana, eliana, silas))
    



    
    
                
        

