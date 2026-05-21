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

def run() -> tuple[str, str]:
    d = get_dict()
    exMap = "define ExMap [ "
    exFix = "define ExFix [ "
    for key in d:
        exMap += f'"{key}" -> "{"{" + key + "}"}" || .#. _ .#. .o. ' 
        exFix += f'"{"{" + key + "}"}" -> "{d[key]}" || .#. _ .#. .o. ' 
    return exMap[:-4] + "] ;", exFix[:-4] + "] ;"

# define ExMap [ "etot" -> "{etot}" .o. "dents" -> "{EX_dents}" ] ;
# define ExFix [ "{etot}" -> "eto" .o. "{EX_dents}" -> "di" ] ;    

if __name__ == "__main__":
    result = run()
    print(result[0])
    print(result[1])