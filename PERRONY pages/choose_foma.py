def filter_p2p(choices: list[str]):
    for i in range(len(choices) - 1, -1, -1):
        if 'pː' in choices[i] or 'bː' in choices[i] or 'ʀ' in choices[i]:
            choices.pop(i)

def filter_intervocal_v(choices: list[str]):
    if all((not 'ʋ' in word) for word in choices):
        return
    for i in range(len(choices) - 1, -1, -1):
        if not 'ʋ' in choices[i]:
            choices.pop(i)

def filter_nulls(choices: list[str]) -> str:
    min_word = choices[0]
    min_length = len(choices[0])
    for choice in choices:
        if len(choice) < min_length:
            min_length = len(choice)
            min_word = choice
    return min_word

def choose(choices: list[str]) -> str:

    if len(choices) == 1:
        return choices[0]

    filter_p2p(choices)
    filter_intervocal_v(choices)
    result = filter_nulls(choices)
    return result

