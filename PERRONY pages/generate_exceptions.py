import os

def get_dict() -> dict[str, str]:
    d = {}
    with open("exceptions.txt", "r", encoding="utf-8-sig") as f:
        line = f.readline()
        while line != "":
            line_lst = line.split(":")
            d[line_lst[0]] = line_lst[1].replace("\n", "")
            line = f.readline()
    return d

def space_word(word: str):
    return " ".join([char for char in word])

def run() -> tuple[str, str]:
    d = get_dict()
    exMap = "define ExMap [ "
    exFix = "define ExFix [ "
    for key in d:
        exMap += f'{space_word(key)} -> "EX_{key}" || WB _ WB .o. ' 
        exFix += f'"EX_{key}" -> {space_word(d[key])} || WB _ WB .o. ' 
    return exMap[:-4] + "] ;", exFix[:-4] + "] ;"

# define ExMap [ e t o t -> "etot" || WB _ WB .o. d e n t s -> "dents" || WB _ WB ] ;
# define ExFix [ "etot" -> e t o || WB _ WB .o. "dents" -> d i || WB _ WB ] ;    

if __name__ == "__main__":
    result = run()
    print(result[0])
    print(result[1])