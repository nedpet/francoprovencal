# takes the tws files in perrony_extracted with french numbers and translated
# only those numbers into francoprovencal

import os

number_dict = {
    "un": "un",
    "deux": "dous",
    "trois": "treis",
    "quatre": "quatro",
    "cinq": "cinq",
    "six": "choués",
    "sept": "sat",
    "huit": "huet",
    "neuf": "nou",
    "dix": "dies",
    "onze": "onze",
    "douze": "doze",
    "treize": "treze",
    "quatorze": "quatorze",
    "quinze": "quinze",
    "seize": "seize",
    "vingt": "vingt",
    "trente": "trenta",
    "quarante": "quaranta",
    "cinquante": "cinquanta",
    "soixante": "chouessanta",
    "septante": "setanta",
    "huitante": "huitanta",
    "nonante": "nonanta",
    "cent": "cent",
    "mille": "meulle",
    "et": "et",
    "cents": "cents",
    "milles": "milles"
}

special_teens = {
    "onze": "un",
    "douze": "deux",
    "treize": "trois",
    "quatorze": "quatre",
    "quinze": "cinq",
    "seize": "six",
    "dix sept": "sept",
    "dix huit": "huit",
    "dix neuf": "neuf"
}

special_tens = {
    "soixante": "septante",
    "quatre vingts": "nonante"
}

ones = ["un", "dous", "treis", "quatro", "cinq", "choués", "sat", "huet", "nou"]
tens = ["dies", "vingt", "trenta", "quaranta", "cinquanta", "chouessanta", "setanta", "huitanta", "nonanta"]

# return whether line is a french number
def is_number(line: str) -> str:
    return all((word in number_dict or word in ["vingts", "cents", "meulles", "et"]) for word in line.split(" "))

# takes care of soixante-dix and quatre-vingts and all that messy business
def replace_weird_tens(line: str) -> str:
    combinations = [(tens, ones) for tens in special_tens for ones in special_teens]
    for comb in combinations:
        line = line.replace(f"{comb[0]} {comb[1]}", f"{special_tens[comb[0]]} {special_teens[comb[1]]}")
    return line.replace("quatre vingts", "huitante")

# inserts an et between the ones and tens if applicable (ex. quaranta et cinq)
def insert_ets(line: str) -> str:
    words = line.split(" ")
    if len(words) >= 2 and words[-1] in ones and words[-2] in tens:
        words.insert(len(words) - 1, "et")
    return " ".join(words)

# takes each cent and meulle and makes them plural if preceded by a digit > 1
def pluralize(line: str) -> str:
    line_lst = line.split(" ")
    for i in range(len(line_lst)):
        if line_lst[i] in ["meulle", "cent"] and i > 0:
            if line_lst[i - 1] in ones and line_lst[i - 1] != "un":
                line_lst[i] = line_lst[i] + "s"
    return " ".join(line_lst)

# runs the process on a single line
def transform_line(line: str) -> str:
    line_lst = line.split("\t")

    line_lst[3] = line_lst[3][:-1]
    if not is_number(line_lst[3]):
        return line
    
    line_lst[3] = replace_weird_tens(line_lst[3])
    line_lst[3] = insert_ets(line_lst[3])
    line_lst[3] = " ".join([number_dict[word] for word in line_lst[3].split(" ")])
    line_lst[3] = insert_ets(line_lst[3])
    line_lst[3] = pluralize(line_lst[3])

    return "\t".join(line_lst) + "\n"

# runs the process on a single file
def transform_file(filename: str):
    with open(f"{filename}", "r", encoding="utf-8-sig") as f:
        lines = f.readlines()
    with open(f"new_{filename}", "w", encoding="utf-8-sig") as f:
        for line in lines:
            f.write(transform_line(line))

def run():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    for i in range(1, 34, 1):
        if i in {21, 23, 26, 31}:
            continue
        transform_file(f"perrony_extracted/chapter{i}.tws")

if __name__ == "__main__":
    run()