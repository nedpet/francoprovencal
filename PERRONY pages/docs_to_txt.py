""" takes pages in docx format and puts them in a single txt file 
"""

from docx import Document
import os

def formatted_num(num: int) -> str:
    if num < 10:
        return f"0{num}"
    else:
        return num

if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    open('content.txt', 'w', encoding='utf-8-sig').close()

    for i in range(4, 58, 1):
        doc = Document(f"docx_pages/P0{formatted_num(i)}.docx")
        for para in doc.paragraphs:
            with open('content.txt', 'a', encoding='utf-8-sig') as f:
                f.write(para.text + "\n")