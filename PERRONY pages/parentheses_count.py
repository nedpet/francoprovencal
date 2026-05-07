""" counts the number of words in parentheses in context.txt and also outputs them
"""
def process_line(line: str) -> int:
    line_lst = line.split("(")
    count = 0
    all_words = []
    for i in range(1, len(line_lst)):
        line_lst[i] = line_lst[i][:line_lst[i].find(")")]
        words = line_lst[i].split(" ")
        count += len(words)
        all_words += words
    return count, all_words

if __name__ == "__main__":
    count = 0
    all_words = []
    with open("content.txt", "r", encoding="utf-8-sig") as f:
        line = f.readline()
        while (line != ""):
            processed = process_line(line)
            count += processed[0]
            all_words += processed[1]
            line = f.readline()
    print(all_words)
    print(count)