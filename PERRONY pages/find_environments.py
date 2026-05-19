import os

def process_line(line: str, d: dict[str, list[str]]):
    line = line.replace(" ", "#")
    for i in range(len(line) - 1):
        if line[i] == '#':
            continue
        environment = line[i - 1] + "_" + line[i + 1]
        if not line[i] in d:
            d[line[i]] = [environment]
        elif line[i] in d and not environment in d[line[i]]:
            d[line[i]].append(environment)

def find_minimal_pairs(d: dict[str, list[str]]):
    pair_d = {}
    for key in d:
        pair_d[key] = {}
        for other_key in d:
            if other_key == key:
                continue
            for env in d[other_key]:
                if env in d[key]:
                    pair_d[key][other_key] = env
                    break
    return pair_d

def find_index(env: str) -> tuple[int, int]:
    i = 1
    with open("content_ipa.txt", "r", encoding="utf-8-sig") as f:
        line = f.readline()
        while (f != ""):
            if env in line:
                line_lst = line.split(" ")
                j = 0
                while not env in line_lst[j]:
                    j += 1
                return (i, j)
            i += 1
            line = f.readline()
    return (-1, -1)

def find_context(env: str) -> tuple[str, str]:
    index = find_index(env)
    if index[0] == -1:
        return "err", "err"
    with open("content.txt", "r", encoding="utf-8-sig") as f:
        for _ in range(index[0]):
            line = f.readline()
        line_lst = line.split(" ")
        word = line_lst[index[1] - 1]
    return word, line

def min_pairs(pairs):
    first_phone = input("First phone: ")
    second_phone = input("Second phone: ")
    if second_phone in pairs[first_phone]:
        print(f"Minimal pair found: {pairs[first_phone][second_phone]}")
    else:
        print("No minimal pairs")

def find_envir():
    envir = input("The environment: ")
    envir = envir.replace("#", " ")
    result = find_context(envir)
    print(f"The word is {result[0]}, found in: {result[1]}")

def run():

    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    d = {}

    with open("only_ipa.txt", "r", encoding="utf-8-sig") as f:
        line = f.readline()
        while (line != ""):
            process_line(line, d)
            line = f.readline()
    pairs = find_minimal_pairs(d)

    while True:
        option = input("Select option: \n1 to find minimal pairs\n2 to find an environment\n3 to terminate\n")
        if option == "1":
            min_pairs(pairs)
        elif option == "2":
            find_envir()
        else:
            break
        

if __name__ == "__main__":
    run()