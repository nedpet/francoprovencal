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

# identifies the word with the match, treating any whitespace (spaces, tabs, newlines) as a word boundary
def identify_word(line: str, match) -> tuple[str, int]:
    start, end = match.span()
    while end < len(line) and not line[end].isspace():
        end += 1
    if line[start].isspace():
        start += 1
    while start > 0 and not line[start - 1].isspace():
        start -= 1
    return line[start:end], end

# returns this chapter's eaf words (start, end, value) in time order, and a map from each word to the indices of its occurrences
# cached so each eaf is only loaded once, the first time it's needed
@functools.cache
def load_eaf_words(chapter: int) -> tuple[list[tuple[int, int, str]], dict[str, list[int]]]:
    eaf = pympi.Elan.Eaf(f'aligned_audios/chapter{chapter}.eaf')
    annotations = sorted(eaf.get_annotation_data_for_tier("Word"))
    occurrences = {}
    for i, (_, _, value) in enumerate(annotations):
        occurrences.setdefault(value, []).append(i)
    return annotations, occurrences

# turns one space at the front or back of the regex into a word boundary, so " illi" matches words starting
# with illi and "illi " matches words ending with it, without the match running into the neighbouring word
def word_boundary_regex(regex: str) -> str:
    if regex.startswith(" "):
        regex = r"(?<!\S)" + regex[1:]
    if regex.endswith(" ") and not regex.endswith("\\ "):
        regex = regex[:-1] + r"(?!\S)"
    return regex

# yields each word in this line that contains a match
def matched_words(line: str, regex: str):
    regex = word_boundary_regex(regex)
    match = re.search(regex, line)
    while line != "" and match is not None:
        word, new_start = identify_word(line, match)
        yield word
        line = line[new_start:]
        match = re.search(regex, line)

# adds matches in this line to the found set, stopping once it holds limit words
def process_line(chapter: int, line: str, regex: str, found: list[FoundWord], exclude_propers: bool, allow_duplicates: bool, limit: int):
    for word in matched_words(line, regex):
        if len(found) >= limit:
            break
        if (allow_duplicates or word not in [foundword.word for foundword in found]) and (not exclude_propers or word[0].islower()):
            annotations, occurrences = load_eaf_words(chapter)
            # the nth time a word is found in this chapter's text is its nth occurrence in the eaf
            n = sum(1 for foundword in found if foundword.word == word and foundword.chapter == chapter)
            indices = occurrences.get(word, [])
            if n < len(indices):
                i = indices[n]
                start, end, _ = annotations[i]
                before = " ".join(value for _, _, value in annotations[max(0, i - CONTEXT_WORDS):i])
                after = " ".join(value for _, _, value in annotations[i + 1:i + 1 + CONTEXT_WORDS])
                found_word = FoundWord(word, chapter, start, end, before, after)
                found.append(found_word)

# adds the set of matches in this chapter to found words, stopping once it holds limit words
def process_chapter(num: int, regex: str, exclude_propers: bool, allow_duplicates: bool, found_words: list[FoundWord], limit: int):
    if num in MISSING_CHAPTERS:
        return
    with open(f"stripped/chapter{num}.txt", "r", encoding="utf-8-sig") as f:
        line = f.readline()
        while (line != "" and len(found_words) < limit):
            process_line(num, line, regex, found_words, exclude_propers, allow_duplicates, limit)
            line = f.readline()

# returns the first limit matching words across every chapter
# should_stop is checked before each chapter, and ends the search early if it returns True
def find_words(regex: str, exclude_propers: bool, allow_duplicates: bool, limit: int, should_stop=lambda: False) -> list[FoundWord]:
    found_words = []
    for i in range(CHAPTER_START, CHAPTER_END + 1):
        if len(found_words) >= limit or should_stop():
            break
        process_chapter(i, regex, exclude_propers, allow_duplicates, found_words, limit)
    return found_words

# returns the matching words in each missing chapter (which have no eaf) that aren't already in found_words
def find_missing_chapter_words(regex: str, exclude_propers: bool, allow_duplicates: bool, found_words: list[FoundWord]) -> dict[int, list[str]]:
    seen = {foundword.word for foundword in found_words}
    missing_words = {}
    for num in MISSING_CHAPTERS:
        missing_words[num] = []
        with open(f"stripped/chapter{num}.txt", "r", encoding="utf-8-sig") as f:
            for line in f:
                for word in matched_words(line, regex):
                    if (allow_duplicates or word not in seen) and (not exclude_propers or word[0].islower()):
                        seen.add(word)
                        missing_words[num].append(word)
    return missing_words

# trims the chapter audio to this word, padded by buffer seconds on each side, and saves it to out_path
def extract_clip(word: FoundWord, buffer: float, out_path: str):
    start = max(0, word.start / 1000 - buffer)
    end = word.end / 1000 + buffer
    subprocess.run(["ffmpeg", "-loglevel", "quiet", "-y", "-ss", str(start), "-t", str(end - start),
                    "-i", f"audios/chapter{word.chapter}.mp3", out_path], check=True)

class App(tk.Tk):
    def __init__(self, regex: str, exclude_propers: bool, allow_duplicates: bool, buffer: float, limit: int):
        super().__init__()
        self.title("Find tokens")
        self.geometry("750x340")
        self.found_words = []
        self.index = 0
        self.buffer = buffer
        self.clips = []
        self.tmpdir = None
        self.player = None
        self.cancelled = False
        self.missing_words = {}
        self.home =self.build_home(regex, exclude_propers, allow_duplicates, buffer, limit)
        self.word_screen = self.build_word_screen()
        self.home.pack(fill="both", expand=True)
        self.bind("<space>", lambda e: self.hotkey(self.play_button) or self.hotkey(self.run_button))
        self.bind("<Tab>", lambda e: self.hotkey(self.next_button))
        self.bind("<Shift-Tab>", lambda e: self.hotkey(self.prev_button))
        self.bind("<ISO_Left_Tab>", lambda e: self.hotkey(self.prev_button))
        self.bind("<Escape>", lambda e: self.hotkey(self.finish_button))

    def build_home(self, regex: str, exclude_propers: bool, allow_duplicates: bool, buffer: float, limit: int) -> tk.Frame:
        frame = tk.Frame(self, padx=20, pady=20)
        self.regex_var = tk.StringVar(value=regex)
        self.propers_var = tk.BooleanVar(value=exclude_propers)
        self.duplicates_var = tk.BooleanVar(value=allow_duplicates)
        self.buffer_var = tk.StringVar(value=str(buffer))
        self.limit_var = tk.StringVar(value=str(limit))
        tk.Label(frame, text="Regex").grid(row=0, column=0, sticky="w")
        tk.Entry(frame, textvariable=self.regex_var, width=30).grid(row=0, column=1, pady=5)
        tk.Label(frame, text="Exclude proper nouns").grid(row=1, column=0, sticky="w")
        tk.Checkbutton(frame, variable=self.propers_var, takefocus=0).grid(row=1, column=1, sticky="w", pady=5)
        tk.Label(frame, text="Allow duplicates").grid(row=2, column=0, sticky="w")
        tk.Checkbutton(frame, variable=self.duplicates_var, takefocus=0).grid(row=2, column=1, sticky="w", pady=5)
        tk.Label(frame, text="Buffer (seconds)").grid(row=3, column=0, sticky="w")
        tk.Entry(frame, textvariable=self.buffer_var, width=30).grid(row=3, column=1, pady=5)
        tk.Label(frame, text="Max matches").grid(row=4, column=0, sticky="w")
        tk.Entry(frame, textvariable=self.limit_var, width=30).grid(row=4, column=1, pady=5)
        # clicking outside the fields takes focus out of them, so space can run
        frame.bind("<Button-1>", lambda e: frame.focus_set())
        buttons = tk.Frame(frame)
        buttons.grid(row=5, column=0, columnspan=2, pady=15)
        self.run_button = tk.Button(buttons, text="Run", command=self.run)
        self.run_button.pack(side="left")
        self.cancel_button = tk.Button(buttons, text="Cancel", command=self.cancel, state="disabled")
        self.cancel_button.pack(side="left", padx=5)
        self.progress = ttk.Progressbar(frame, length=300)
        self.progress.grid(row=6, column=0, columnspan=2)
        self.progress.grid_remove()
        self.status_label = tk.Label(frame)
        self.status_label.grid(row=7, column=0, columnspan=2)
        return frame

    def build_word_screen(self) -> tk.Frame:
        frame = tk.Frame(self, padx=20, pady=20)
        nav = tk.Frame(frame)
        nav.pack(side="bottom", fill="x")
        self.prev_button = tk.Button(nav, text="Previous", command=lambda: self.move(-1))
        self.prev_button.pack(side="left")
        self.next_button = tk.Button(nav, text="Next", command=lambda: self.move(1))
        self.next_button.pack(side="left", padx=5)
        self.finish_button = tk.Button(nav, text="Finish", command=self.finish)
        self.finish_button.pack(side="right")

        self.word_content = tk.Frame(frame)
        word_row = tk.Frame(self.word_content)
        word_row.pack(expand=True)
        normal, bold = font.Font(size=16), font.Font(size=16, weight="bold")
        self.before_label = tk.Label(word_row, font=normal)
        self.before_label.pack(side="left")
        self.word_label = tk.Label(word_row, font=bold)
        self.word_label.pack(side="left", padx=5)
        self.after_label = tk.Label(word_row, font=normal)
        self.after_label.pack(side="left")
        self.info_label = tk.Label(self.word_content)
        self.info_label.pack()
        self.play_button = tk.Button(self.word_content, text="▶ Play", command=self.play)
        self.play_button.pack(pady=10)

        # final screen, listing extra matches in the chapters with no eaf
        self.missing_content = tk.Frame(frame)
        tk.Label(self.missing_content, text="Extra matches in chapters without alignments",
                 font=font.Font(size=13, weight="bold")).pack(pady=(0, 10))
        self.missing_text = tk.Text(self.missing_content, wrap="word", height=8, takefocus=0,
                                    relief="flat", background=frame.cget("background"))
        self.missing_text.tag_config("chapter", font=font.Font(weight="bold"))
        self.missing_text.pack(fill="both", expand=True)
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
        try:
            limit = int(self.limit_var.get())
            if limit < 1:
                raise ValueError
        except ValueError:
            messagebox.showerror("Invalid max matches", "Max matches must be a whole number above 0")
            return
        self.cancelled = False
        self.run_button.config(state="disabled")
        self.cancel_button.config(state="normal")
        self.config(cursor="watch")
        self.status_label.config(text="Searching...")
        self.found_words = find_words(regex, self.propers_var.get(), self.duplicates_var.get(), limit, self.poll_cancel)
        if not self.cancelled:
            self.missing_words = find_missing_chapter_words(regex, self.propers_var.get(), self.duplicates_var.get(), self.found_words)
        self.config(cursor="")
        if self.found_words and not self.cancelled:
            self.load_clips()
        self.status_label.config(text="Cancelled" if self.cancelled else "")
        self.cancel_button.config(state="disabled")
        self.run_button.config(state="normal")
        if self.cancelled:
            return
        if not self.found_words and not any(self.missing_words.values()):
            messagebox.showinfo("No results", "No words found")
            return
        self.index = 0
        self.home.pack_forget()
        self.word_screen.pack(fill="both", expand=True)
        self.word_screen.focus_set()
        self.show_word()

    # lets the window handle clicks mid-search, and reports whether cancel was pressed
    def poll_cancel(self) -> bool:
        self.update()
        return self.cancelled

    def cancel(self):
        self.cancelled = True

    # cuts every found word's clip into a temp folder, updating the progress bar as it goes
    def load_clips(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.clips = []
        self.progress.config(maximum=len(self.found_words), value=0)
        self.progress.grid()
        for i, word in enumerate(self.found_words):
            self.status_label.config(text=f"Loading audio {i + 1} / {len(self.found_words)}")
            self.update()
            if self.cancelled:
                break
            path = os.path.join(self.tmpdir.name, f"{i}.wav")
            try:
                extract_clip(word, self.buffer, path)
                self.clips.append(path)
            except (subprocess.CalledProcessError, FileNotFoundError):
                self.clips.append(None)
            self.progress.config(value=i + 1)
        self.progress.grid_remove()

    # shows the word screen for the current index, or the missing chapters screen after the last word
    def show_word(self):
        self.stop()
        self.prev_button.config(state="normal" if self.index > 0 else "disabled")
        self.next_button.config(state="normal" if self.index < len(self.found_words) else "disabled")
        if self.index == len(self.found_words):
            self.show_missing()
            return
        self.missing_content.pack_forget()
        self.word_content.pack(fill="both", expand=True)
        word = self.found_words[self.index]
        clip = self.clips[self.index]
        self.before_label.config(text=f"... {word.before}")
        self.word_label.config(text=word.word)
        self.after_label.config(text=f"{word.after} ...")
        info = f"Chapter {word.chapter}  ·  {self.index + 1} / {len(self.found_words)}"
        self.info_label.config(text=info if clip else info + "  ·  audio unavailable")
        self.play_button.config(state="normal" if clip else "disabled")

    def show_missing(self):
        self.word_content.pack_forget()
        self.missing_content.pack(fill="both", expand=True)
        self.missing_text.config(state="normal")
        self.missing_text.delete("1.0", "end")
        for num, words in self.missing_words.items():
            self.missing_text.insert("end", f"Chapter {num}: ", "chapter")
            self.missing_text.insert("end", (", ".join(words) if words else "no extra matches") + "\n")
        self.missing_text.config(state="disabled")

    # presses this button from its hotkey if its screen is showing and no field is being typed in,
    # stopping the key from doing anything else
    def hotkey(self, button: tk.Button):
        if button.winfo_ismapped() and not isinstance(self.focus_get(), tk.Entry):
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

def main(regex: str, exclude_propers: bool, allow_duplicates: bool, buffer: float, limit: int):
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    App(regex, exclude_propers, allow_duplicates, buffer, limit).mainloop()

if __name__ == "__main__":
    regex = r'[^aeouàâäéèì]illi'
    exclude_propers = False
    allow_duplicates = False
    buffer = 0.5
    limit = 50
    main(regex, exclude_propers, allow_duplicates, buffer, limit)