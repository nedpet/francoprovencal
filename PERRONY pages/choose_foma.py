# takes the list of options that foma spits out, and chooses the most likely option
# below are the list of options and the more frequent one:
# pː vs p word-initially:   p
# bː vs b word-initially:   b
# ʁ vs ʀ word-initially:    ʁ
# ave vs a word-finally:    a
# v vs ʋ vs ∅ intervocally: ʋ
# n vs ∅ intervocalically:  ∅ 
# t vs ∅ word-finally:      ∅
# r vs ∅ word-finally:      ∅

# takes ungeminated choices or choices starting with ʁ over ʀ
def filter_p2p(choices: list[str]):
    for i in range(len(choices) - 1, -1, -1):
        if 'pː' in choices[i] or 'bː' in choices[i] or 'ʀ' in choices[i]:
            choices.pop(i)

# takes choices with -a over -ave
def filter_ave(choices: list[str]):
    if all((not word.endswith("avɛ")) for word in choices):
        return
    for i in range(len(choices) - 1, -1, -1):
        if choices[i].endswith("avɛ"):
            choices.pop(i)

# takes choices with ʋ over v and ∅
def filter_intervocal_v(choices: list[str]):
    if all((not 'ʋ' in word) for word in choices):
        return
    max_count = max([word.count('ʋ') for word in choices])
    for i in range(len(choices) - 1, -1, -1):
        if choices[i].count('ʋ') != max_count:
            choices.pop(i)

# takes choices with nasals over ones without
def filter_nasals(choices: list[str]):
    for nasal in ["ã", "ɛ̃", "õ", "ø̃"]:
        filter_nasal(choices, nasal)

# takes choices with this nasal over ones without
def filter_nasal(choices: list[str], nasal: str):
    if all ((not nasal in word) for word in choices):
        return
    max_count = max([word.count(nasal) for word in choices])
    for i in range(len(choices) - 1, -1, -1):
        if choices[i].count(nasal) != max_count:
            choices.pop(i)

# takes choices with the least characters to favour the deletion
def filter_nulls(choices: list[str]) -> str:
    min_word = choices[0]
    min_length = len(choices[0])
    for choice in choices:
        if len(choice) < min_length:
            min_length = len(choice)
            min_word = choice
    return min_word

# for a list of options, return the most likely one
def choose(choices: list[str]) -> str:

    if len(choices) == 1:
        return choices[0]

    filter_p2p(choices)
    filter_ave(choices)
    filter_intervocal_v(choices)
    filter_nasals(choices)
    result = filter_nulls(choices)
    return result

if __name__ == "__main__":
    print(choose(["matena", "matɛ̃a"]))
