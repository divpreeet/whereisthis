from __future__ import annotations
import argparse
import os
import re
import subprocess
import sys
import threading
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence
from textual.app import App, ComposeResult
from textual.containers import Horizontal
from textual.widgets import DataTable, Footer, Header, Input, Markdown, Static
from match import fuzzy, match
from scanner import scan


def tokenize(text: str) -> list[str]:
    return [t for t in re.split(r"[^a-z0-9]+", text.lower()) if t]


@dataclass(frozen=True)
class ResultRow:
    score: int
    path: str


def score_path(path: str, query: str | Sequence[str]):
    if isinstance(query, (list, tuple)):
        query = " ".join(query)

    terms = tokenize(query)
    if not terms:
        return None

    filename = Path(path).name.lower()
    tokens = tokenize(filename)

    total_score = 0
    if all(term in filename for term in terms):
        total_score += 40

    for term in terms:
        best = None
        for t in tokens:
            score = fuzzy(term, t)
            if score is not None and (best is None or score > best):
                best = score

        if best is None:
            return None

        total_score += best

    return total_score


def open_path(path: str) -> None:
    p = Path(path)
    if sys.platform == "darwin":
        subprocess.Popen(["open", str(p)])
    elif os.name == "nt":
        os.startfile(str(p))
    else:
        subprocess.Popen(["xdg-open", str(p)])


def reveal(path: str):
    p = Path(path)
    if sys.platform == "darwin":
        subprocess.Popen(["open", "-R", str(p)])
    elif os.name == "nt":
        subprocess.Popen(["explorer", "/select,", str(p)])
    else:
        subprocess.Popen(["xdg-open", str(p.parent)])


def preview(path: str, max_chars: int = 7000) -> str:
    p = Path(path)
    try:
        stat = p.stat()
        size = stat.st_size
        modified = stat.st_mtime
    except OSError as e:
        return f"# {p.name}\n\nCould not inspect file: `{e}`"

    suffix = p.suffix.lower()
    text_ext = {
        ".txt", ".md", ".py", ".js", ".ts", ".tsx", ".json", ".yaml", ".yml",
        ".html", ".css", ".scss", ".xml", ".csv", ".toml", ".ini", ".sh", ".rs",
        ".go", ".java", ".c", ".cpp", ".h", ".hpp", ".swift", ".kt", ".dart",
    }

    kind = "text"
    if suffix in text_ext or not suffix:
        try:
            text = p.read_text(encoding="utf-8", errors="replace")[:max_chars]
        except Exception:
            text = "[unreadable text file]"
            kind = "binary"

        lines = text.splitlines()
        preview_text = "\n".join(lines[:140])
        if len(lines) > 140:
            preview_text += "\n\n..."
    else:
        kind = "metadata"
        preview_text = "[preview not available for this type of file]"

    return (
        f"# {p.name}\n\n"
        f"**Path:** `{p}`\n\n"
        f"**Type:** `{kind}`  \n"
        f"**Size:** `{size} bytes`  \n"
        f"**Modified:** `{modified}`\n\n"
        f"## Preview\n\n"
        f"```text\n{preview_text}\n```"
    )


class whereisthis(App):
    TITLE = "whereisthis"
    SUB_TITLE = "human language based fzf"
    CSS_PATH = "styles.tcss"
    BINDINGS = [
        ("ctrl+q", "quit", "Quit"),
        ("ctrl+r", "rescan", "Rescan"),
        ("enter", "open_selected", "Open"),
        ("o", "open_selected", "Open"),
        ("v", "reveal_selected", "Reveal"),
        ("c", "copy_path", "Copy path"),
        ("/", "focus_search", "Search"),
        ("esc", "clear_search", "Clear search"),
        ("f5", "rescan", "Refresh"),
    ]

    def __init__(self, directory: str = ".", hidden: bool = False, query: str = ""):
        super().__init__()
        self.directory = directory
        self.show_hidden = hidden
        self.initial_query = query
        self.all_files: list[str] = []
        self.current_results: list[ResultRow] = []

    def compose(self) -> ComposeResult:
        yield Header()
        yield Input(value=self.initial_query, placeholder="search for files", id="search")
        yield Static(f"Query: {self.initial_query}", id="queryline")
        yield Static("Searching", id="status")
        with Horizontal(id="body"):
            yield DataTable(id="results")
            yield Markdown("# Preview\n\nSelect a file", id="preview")
        yield Static(
            "Enter/o open - v reveal - c copy path - / search - ctrl+r refresh - esc clear",
            id="hintbar"
        )
        yield Footer()

    def on_mount(self):
        table = self.query_one("#results", DataTable)
        table.cursor_type = "row"
        table.add_columns("#", "Score", "Path")

        self.query_one("#search", Input).focus()
        self.set_status("scanning...")
        threading.Thread(target=self.load_index, daemon=True).start()

    def set_status(self, text: str):
        self.query_one("#status", Static).update(text)

    def set_queryline(self, text: str):
        self.query_one("#queryline", Static).update(f"Query: {text}")

    def set_preview(self, path: str | None):
        widget = self.query_one("#preview", Markdown)
        if not path:
            widget.update("# Preview\n\nSelect a file")
            return
        widget.update(preview(path))

    def rebuild_table(self, rows: Sequence[ResultRow]):
        table = self.query_one("#results", DataTable)
        table.clear()
        for i, row in enumerate(rows, 1):
            table.add_row(str(i), str(row.score), row.path)

        if rows:
            table.cursor_coordinate = (0, 0)
            self.set_preview(rows[0].path)
        else:
            self.set_preview(None)

    def load_index(self):
        try:
            files = scan(self.directory, hidden=self.show_hidden)
        except Exception as e:
            self.call_from_thread(self.set_status, f"scan failed: {e}")
            return

        self.call_from_thread(self.finish_index, files)

    def finish_index(self, files: list[str]):
        self.all_files = files
        self.set_status(f"indexed {len(files)} files in {self.directory}")
        self.apply_query(self.query_one("#search", Input).value)

    def apply_query(self, query: str):
        self.set_queryline(query)

        if not self.all_files:
            self.current_results = []
            self.rebuild_table([])
            return

        if not query.strip():
            self.current_results = []
            self.set_status(f"indexed {len(self.all_files)} files in {self.directory}")
            self.rebuild_table([])
            return

        filtered = match(self.all_files, query)
        rows: list[ResultRow] = []
        for path in filtered:
            score = score_path(path, query)
            if score is not None:
                rows.append(ResultRow(score, path))

        rows.sort(key=lambda r: (-r.score, r.path))
        self.current_results = rows
        self.set_status(f"{len(rows)} results")
        self.rebuild_table(rows[:500])

    def selected_path(self):
        table = self.query_one("#results", DataTable)
        if not self.current_results:
            return None

        row = table.cursor_row
        if row is None or row < 0 or row >= len(self.current_results):
            return None
        return self.current_results[row].path

    def action_focus_search(self):
        self.query_one("#search", Input).focus()

    def action_clear_search(self):
        search = self.query_one("#search", Input)
        search.value = ""
        search.focus()
        self.apply_query("")

    def action_rescan(self):
        self.set_status("rescanning")
        threading.Thread(target=self.load_index, daemon=True).start()

    def action_open_selected(self):
        path = self.selected_path()
        if path:
            open_path(path)

    def action_reveal_selected(self):
        path = self.selected_path()
        if path:
            reveal(path)

    def action_copy_path(self):
        path = self.selected_path()
        if not path:
            return
        try:
            self.copy_to_clipboard(path)
            self.set_status(f"copied: {path}")
        except Exception:
            self.set_status("copy failed on the terminal")

    def on_input_changed(self, event: Input.Changed):
        if event.input.id == "search":
            self.apply_query(event.value)

    def on_data_table_row_highlighted(self, event: DataTable.RowHighlighted):
        if event.data_table.id != "results":
            return
        if 0 <= event.cursor_row < len(self.current_results):
            self.set_preview(self.current_results[event.cursor_row].path)

    def on_data_table_row_selected(self, event: DataTable.RowSelected):
        if event.data_table.id != "results":
            return
        if 0 <= event.cursor_row < len(self.current_results):
            self.set_preview(self.current_results[event.cursor_row].path)
            open_path(self.current_results[event.cursor_row].path)

def parse_args(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="a human language based fzf")
    parser.add_argument("query", nargs="*", default=[], help="optional initial query")
    parser.add_argument("--dir", default=".", help="directory to scan")
    parser.add_argument("--hidden", action="store_true", help="include hidden files")
    return parser.parse_args(argv)


if __name__ == "__main__":
    args = parse_args(sys.argv[1:])
    app = whereisthis(directory=args.dir, hidden=args.hidden, query=" ".join(args.query))
    app.run()