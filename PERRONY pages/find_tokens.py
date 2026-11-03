import re
import os
import pympi
import functools
import subprocess
import tempfile
import tkinter as tk
from tkinter import font, messagebox, ttk
from dataclasses import dataclass

CHAPTER_START = 1
CHAPTER_END = 33
MISSING_CHAPTERS = [21, 23, 26, 31]
CONTEXT_WORDS = 3

@dataclass
class FoundWord:
    word: str
    chapter: int
    start: float
    end: float
    before: str
    after: str

# identifies the word with the match
def identify_word(line: str, match) -> tuple[str, int]:
    start, end = match.span()
    while line[end] not in [" ", "\n"]:
        end += 1
    if line[start] == " ":
        start += 1
    while line[start - 1] != " " and start > 0:
        start -= 1
    return line[start:end], end

# returns this chapter's eaf words (start, end, value) in time order, and a map from each word to the index of its first occurrence
# cached so each eaf is only loaded once, the first time it's needed
@functools.cache
def load_eaf_words(chapter: int) -> tuple[list[tuple[int, int, str]], dict[str, int]]:
    eaf = pympi.Elan.Eaf(f'aligned_audios/chapter{chapter}.eaf')
    annotations = sorted(eaf.get_annotation_data_for_tier("Word"))
    first_index = {}
    for i, (_, _, value) in enumerate(annotations):
        first_index.setdefault(value, i)
    return annotations, first_index

# adds matches in this line to the found set
def process_line(chapter: int, line: str, regex: str, found: list[FoundWord], exclude_propers: bool):
    match = re.search(regex, line)
    while line != "" and match is not None:
        word, new_start = identify_word(line, match)
        if word not in [foundword.word for foundword in found] and (not exclude_propers or word[0].islower()):
            annotations, first_index = load_eaf_words(chapter)
            i = first_index.get(word)
            if i is not None:
                start, end, _ = annotations[i]
                before = " ".join(value for _, _, value in annotations[max(0, i - CONTEXT_WORDS):i])
                after = " ".join(value for _, _, value in annotations[i + 1:i + 1 + CONTEXT_WORDS])
                found_word = FoundWord(word, chapter, start, end, before, after)
                found.append(found_word)
        line = line[new_start:]
        match = re.search(regex, line)

# adds the set of matches in this chapter to found words
def process_chapter(num: int, regex: str, exclude_propers: bool, found_words: list[FoundWord]):
    if num in MISSING_CHAPTERS:
        return
    with open(f"stripped/chapter{num}.txt", "r", encoding="utf-8-sig") as f:
        line = f.readline()
        while (line != ""):
            process_line(num, line, regex, found_words, exclude_propers)
            line = f.readline()

# returns all matching words across every chapter
def find_words(regex: str, exclude_propers: bool) -> list[FoundWord]:
    found_words = []
    for i in range(CHAPTER_START, CHAPTER_END + 1):
        process_chapter(i, regex, exclude_propers, found_words)
    return found_words

# trims the chapter audio to this word, padded by buffer seconds on each side, and saves it to out_path
def extract_clip(word: FoundWord, buffer: float, out_path: str):
    start = max(0, word.start / 1000 - buffer)
    end = word.end / 1000 + buffer
    subprocess.run(["ffmpeg", "-loglevel", "quiet", "-y", "-ss", str(start), "-t", str(end - start),
                    "-i", f"audios/chapter{word.chapter}.mp3", out_path], check=True)

class App(tk.Tk):
    def __init__(self, regex: str, exclude_propers: bool, buffer: float):
        super().__init__()
        self.title("Find tokens")
        self.geometry("750x300")
        self.found_words = []
        self.index = 0
        self.buffer = buffer
        self.clips = []
        self.tmpdir = None
        self.player = None
        self.home = self.build_home(regex, exclude_propers, buffer)
        self.word_screen = self.build_word_screen()
        self.home.pack(fill="both", expand=True)
        self.bind("<space>", lambda e: self.hotkey(self.play_button))
        self.bind("<Tab>", lambda e: self.hotkey(self.next_button))
        self.bind("<Shift-Tab>", lambda e: self.hotkey(self.prev_button))
        self.bind("<ISO_Left_Tab>", lambda e: self.hotkey(self.prev_button))

    def build_home(self, regex: str, exclude_propers: bool, buffer: float) -> tk.Frame:
        frame = tk.Frame(self, padx=20, pady=20)
        self.regex_var = tk.StringVar(value=regex)
        self.propers_var = tk.BooleanVar(value=exclude_propers)
        self.buffer_var = tk.StringVar(value=str(buffer))
        tk.Label(frame, text="Regex").grid(row=0, column=0, sticky="w")
        tk.Entry(frame, textvariable=self.regex_var, width=30).grid(row=0, column=1, pady=5)
        tk.Label(frame, text="Exclude proper nouns").grid(row=1, column=0, sticky="w")
        tk.Checkbutton(frame, variable=self.propers_var).grid(row=1, column=1, sticky="w", pady=5)
        tk.Label(frame, text="Buffer (seconds)").grid(row=2, column=0, sticky="w")
        tk.Entry(frame, textvariable=self.buffer_var, width=30).grid(row=2, column=1, pady=5)
        self.run_button = tk.Button(frame, text="Run", command=self.run)
        self.run_button.grid(row=3, column=0, columnspan=2, pady=15)
        self.progress = ttk.Progressbar(frame, length=300)
        self.progress.grid(row=4, column=0, columnspan=2)
        self.progress.grid_remove()
        self.status_label = tk.Label(frame)
        self.status_label.grid(row=5, column=0, columnspan=2)
        return frame

    def build_word_screen(self) -> tk.Frame:
        frame = tk.Frame(self, padx=20, pady=20)
        nav = tk.Frame(frame)
        nav.pack(side="bottom", fill="x")
        self.prev_button = tk.Button(nav, text="Previous (Shift+Tab)", command=lambda: self.move(-1))
        self.prev_button.pack(side="left")
        self.next_button = tk.Button(nav, text="Next (Tab)", command=lambda: self.move(1))
        self.next_button.pack(side="left", padx=5)
        tk.Button(nav, text="Finish", command=self.finish).pack(side="right")

        word_row = tk.Frame(frame)
        word_row.pack(expand=True)
        normal, bold = font.Font(size=16), font.Font(size=16, weight="bold")
        self.before_label = tk.Label(word_row, font=normal)
        self.before_label.pack(side="left")
        self.word_label = tk.Label(word_row, font=bold)
        self.word_label.pack(side="left", padx=5)
        self.after_label = tk.Label(word_row, font=normal)
        self.after_label.pack(side="left")

        self.info_label = tk.Label(frame)
        self.info_label.pack()
        self.play_button = tk.Button(frame, text="▶ Play (Space)", command=self.play)
        self.play_button.pack(pady=10)
        return frame

    def run(self):
        regex = self.regex_var.get()
        try:
            re.compile(regex)
        except re.error as e:
            messagebox.showerror("Invalid regex", str(e))
            return
        try:
            self.buffer = float(self.buffer_var.get())
        except ValueError:
            messagebox.showerror("Invalid buffer", "Buffer must be a number of seconds")
            return
        self.run_button.config(state="disabled")
        self.config(cursor="watch")
        self.status_label.config(text="Searching...")
        self.update()
        self.found_words = find_words(regex, self.propers_var.get())
        self.config(cursor="")
        if self.found_words:
            self.load_clips()
        self.status_label.config(text="")
        self.run_button.config(state="normal")
        if not self.found_words:
            messagebox.showinfo("No results", "No words found")
            return
        self.index = 0
        self.home.pack_forget()
        self.word_screen.pack(fill="both", expand=True)
        self.word_screen.focus_set()
        self.show_word()

    # cuts every found word's clip into a temp folder, updating the progress bar as it goes
    def load_clips(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.clips = []
        self.progress.config(maximum=len(self.found_words), value=0)
        self.progress.grid()
        for i, word in enumerate(self.found_words):
            self.status_label.config(text=f"Loading audio {i + 1} / {len(self.found_words)}")
            self.update()
            path = os.path.join(self.tmpdir.name, f"{i}.wav")
            try:
                extract_clip(word, self.buffer, path)
                self.clips.append(path)
            except (subprocess.CalledProcessError, FileNotFoundError):
                self.clips.append(None)
            self.progress.config(value=i + 1)
        self.progress.grid_remove()

    def show_word(self):
        self.stop()
        word = self.found_words[self.index]
        clip = self.clips[self.index]
        self.before_label.config(text=f"... {word.before}")
        self.word_label.config(text=word.word)
        self.after_label.config(text=f"{word.after} ...")
        info = f"Chapter {word.chapter}  ·  {self.index + 1} / {len(self.found_words)}"
        self.info_label.config(text=info if clip else info + "  ·  audio unavailable")
        self.play_button.config(state="normal" if clip else "disabled")
        self.prev_button.config(state="normal" if self.index > 0 else "disabled")
        self.next_button.config(state="normal" if self.index < len(self.found_words) - 1 else "disabled")

    # presses this word screen button from its hotkey, stopping the key from doing anything else
    def hotkey(self, button: tk.Button):
        if self.word_screen.winfo_ismapped():
            button.invoke()
            return "break"

    def move(self, step: int):
        self.index += step
        self.show_word()

    def play(self):
        self.stop()
        self.player = subprocess.Popen(["ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet", self.clips[self.index]],
                                       stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # stops any clip that is still playing
    def stop(self):
        if self.player is not None:
            self.player.terminate()
            self.player = None

    def finish(self):
        self.stop()
        self.word_screen.pack_forget()
        self.home.pack(fill="both", expand=True)

def main(regex: str, exclude_propers: bool, buffer: float):
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    App(regex, exclude_propers, buffer).mainloop()

if __name__ == "__main__":
    regex = r'[^aeouàâäéèì]illi'
    exclude_propers = False
    buffer = 0.5
    main(regex, exclude_propers, buffer)