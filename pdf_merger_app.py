from __future__ import annotations

import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from i18n import DEFAULT_LANGUAGE, LANGUAGES, t
from pdf_tools import MergeOptions, MergePdfOperation, PdfMergeError, operation_registry


class PdfMergerApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.geometry("860x570")
        self.minsize(760, 500)

        self.language = tk.StringVar(value=DEFAULT_LANGUAGE)
        self.pdf_paths: list[Path] = []
        self.output_path = tk.StringVar()
        self.status_text = tk.StringVar()
        self.keep_metadata = tk.BooleanVar(value=True)
        self.translatable_widgets: dict[str, tuple[tk.Widget, str]] = {}

        self._build_ui()
        self.apply_language()

    def tr(self, key: str, **kwargs: object) -> str:
        return t(self.language.get(), key, **kwargs)

    def _build_ui(self) -> None:
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        header = ttk.Frame(self, padding=(16, 14, 16, 8))
        header.grid(row=0, column=0, sticky="ew")
        header.columnconfigure(0, weight=1)

        self.title_label = ttk.Label(header, font=("Microsoft YaHei UI", 18, "bold"))
        self.title_label.grid(row=0, column=0, sticky="w")
        self.translatable_widgets["title_label"] = (self.title_label, "app_title")

        self.subtitle_label = ttk.Label(header, foreground="#59636e")
        self.subtitle_label.grid(row=1, column=0, sticky="w", pady=(4, 0))

        language_frame = ttk.Frame(header)
        language_frame.grid(row=0, column=1, rowspan=2, sticky="e")

        self.language_label = ttk.Label(language_frame)
        self.language_label.grid(row=0, column=0, sticky="e", padx=(0, 8))
        self.translatable_widgets["language_label"] = (self.language_label, "language")

        self.language_selector = ttk.Combobox(
            language_frame,
            state="readonly",
            width=12,
            textvariable=self.language,
            values=list(LANGUAGES),
        )
        self.language_selector.grid(row=0, column=1, sticky="e")
        self.language_selector.bind("<<ComboboxSelected>>", lambda _event: self.apply_language())

        main = ttk.Frame(self, padding=(16, 8, 16, 8))
        main.grid(row=1, column=0, sticky="nsew")
        main.columnconfigure(0, weight=1)
        main.rowconfigure(0, weight=1)

        self.list_frame = ttk.LabelFrame(main, padding=10)
        self.list_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        self.list_frame.columnconfigure(0, weight=1)
        self.list_frame.rowconfigure(0, weight=1)
        self.translatable_widgets["list_frame"] = (self.list_frame, "file_list_title")

        self.file_list = tk.Listbox(
            self.list_frame,
            selectmode=tk.EXTENDED,
            activestyle="none",
            font=("Microsoft YaHei UI", 10),
        )
        self.file_list.grid(row=0, column=0, sticky="nsew")

        scrollbar = ttk.Scrollbar(self.list_frame, orient="vertical", command=self.file_list.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.file_list.configure(yscrollcommand=scrollbar.set)

        controls = ttk.Frame(main)
        controls.grid(row=0, column=1, sticky="ns")

        self.add_button = ttk.Button(controls, command=self.add_files)
        self.add_button.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        self.translatable_widgets["add_button"] = (self.add_button, "add_pdf")

        self.remove_button = ttk.Button(controls, command=self.remove_selected)
        self.remove_button.grid(row=1, column=0, sticky="ew", pady=(0, 8))
        self.translatable_widgets["remove_button"] = (self.remove_button, "remove_selected")

        self.up_button = ttk.Button(controls, command=lambda: self.move_selected(-1))
        self.up_button.grid(row=2, column=0, sticky="ew", pady=(0, 8))
        self.translatable_widgets["up_button"] = (self.up_button, "move_up")

        self.down_button = ttk.Button(controls, command=lambda: self.move_selected(1))
        self.down_button.grid(row=3, column=0, sticky="ew", pady=(0, 8))
        self.translatable_widgets["down_button"] = (self.down_button, "move_down")

        self.clear_button = ttk.Button(controls, command=self.clear_files)
        self.clear_button.grid(row=4, column=0, sticky="ew", pady=(0, 16))
        self.translatable_widgets["clear_button"] = (self.clear_button, "clear_list")

        self.metadata_check = ttk.Checkbutton(controls, variable=self.keep_metadata)
        self.metadata_check.grid(row=5, column=0, sticky="w")
        self.translatable_widgets["metadata_check"] = (self.metadata_check, "keep_metadata")

        self.output_frame = ttk.LabelFrame(self, padding=12)
        self.output_frame.grid(row=2, column=0, sticky="ew", padx=16, pady=(0, 8))
        self.output_frame.columnconfigure(1, weight=1)
        self.translatable_widgets["output_frame"] = (self.output_frame, "output_settings")

        self.save_to_label = ttk.Label(self.output_frame)
        self.save_to_label.grid(row=0, column=0, sticky="w", padx=(0, 8))
        self.translatable_widgets["save_to_label"] = (self.save_to_label, "save_to")

        ttk.Entry(self.output_frame, textvariable=self.output_path).grid(row=0, column=1, sticky="ew", padx=(0, 8))

        self.choose_button = ttk.Button(self.output_frame, command=self.choose_output)
        self.choose_button.grid(row=0, column=2, sticky="e")
        self.translatable_widgets["choose_button"] = (self.choose_button, "choose_location")

        footer = ttk.Frame(self, padding=(16, 4, 16, 16))
        footer.grid(row=3, column=0, sticky="ew")
        footer.columnconfigure(0, weight=1)

        ttk.Label(footer, textvariable=self.status_text, foreground="#59636e").grid(row=0, column=0, sticky="w")
        self.merge_button = ttk.Button(footer, command=self.merge_files)
        self.merge_button.grid(row=0, column=1, sticky="e")
        self.translatable_widgets["merge_button"] = (self.merge_button, "merge")

    def apply_language(self) -> None:
        self.title(self.tr("app_title"))
        self.language_selector.configure(values=list(LANGUAGES))

        for widget, key in self.translatable_widgets.values():
            widget.configure(text=self.tr(key))

        self.subtitle_label.configure(
            text=self.tr("available_operations", operations=", ".join(operation_registry.names()))
        )

        if not self.status_text.get():
            self.status_text.set(self.tr("initial_status"))
        elif not self.pdf_paths:
            self.status_text.set(self.tr("initial_status"))
        else:
            self.status_text.set(self.tr("selected_count", count=len(self.pdf_paths)))

    def add_files(self) -> None:
        filenames = filedialog.askopenfilenames(
            title=self.tr("choose_pdf_title"),
            filetypes=[(self.tr("pdf_files"), "*.pdf"), (self.tr("all_files"), "*.*")],
        )
        for filename in filenames:
            path = Path(filename)
            if path.suffix.lower() == ".pdf" and path not in self.pdf_paths:
                self.pdf_paths.append(path)
        self.refresh_file_list()
        self.status_text.set(self.tr("selected_count", count=len(self.pdf_paths)))

    def remove_selected(self) -> None:
        selected = sorted(self.file_list.curselection(), reverse=True)
        for index in selected:
            del self.pdf_paths[index]
        self.refresh_file_list()
        self.status_text.set(self.tr("selected_count", count=len(self.pdf_paths)))

    def clear_files(self) -> None:
        self.pdf_paths.clear()
        self.refresh_file_list()
        self.status_text.set(self.tr("list_cleared"))

    def move_selected(self, direction: int) -> None:
        selected = list(self.file_list.curselection())
        if not selected:
            return

        indexes = selected if direction < 0 else reversed(selected)
        for index in indexes:
            new_index = index + direction
            if 0 <= new_index < len(self.pdf_paths):
                self.pdf_paths[index], self.pdf_paths[new_index] = self.pdf_paths[new_index], self.pdf_paths[index]

        self.refresh_file_list()
        for index in selected:
            new_index = index + direction
            if 0 <= new_index < len(self.pdf_paths):
                self.file_list.selection_set(new_index)

    def choose_output(self) -> None:
        filename = filedialog.asksaveasfilename(
            title=self.tr("save_merged_title"),
            defaultextension=".pdf",
            filetypes=[(self.tr("pdf_files"), "*.pdf")],
            initialfile=self.tr("default_output_name"),
        )
        if filename:
            self.output_path.set(filename)

    def refresh_file_list(self) -> None:
        self.file_list.delete(0, tk.END)
        for index, path in enumerate(self.pdf_paths, start=1):
            self.file_list.insert(tk.END, f"{index}. {path.name}    [{path.parent}]")

    def merge_files(self) -> None:
        try:
            output_value = self.output_path.get().strip()
            if not output_value:
                raise ValueError(self.tr("choose_output_error"))
            output_path = Path(output_value).expanduser()
            if output_path.suffix.lower() != ".pdf":
                output_path = output_path.with_suffix(".pdf")
                self.output_path.set(str(output_path))
        except Exception as exc:
            messagebox.showerror(self.tr("app_title"), str(exc))
            return

        self.set_busy(True)
        self.status_text.set(self.tr("merging"))

        def worker() -> None:
            try:
                operation = MergePdfOperation(
                    self.pdf_paths,
                    MergeOptions(output_path=output_path, keep_metadata=self.keep_metadata.get()),
                )
                operation.run()
            except Exception as exc:
                self.after(0, lambda: self.on_merge_failed(exc))
            else:
                self.after(0, lambda: self.on_merge_success(output_path))

        threading.Thread(target=worker, daemon=True).start()

    def set_busy(self, busy: bool) -> None:
        state = tk.DISABLED if busy else tk.NORMAL
        self.merge_button.configure(state=state)
        self.add_button.configure(state=state)

    def on_merge_success(self, output_path: Path) -> None:
        self.set_busy(False)
        self.status_text.set(self.tr("merge_done_status", path=output_path))
        messagebox.showinfo(self.tr("app_title"), self.tr("merge_done_message", path=output_path))

    def on_merge_failed(self, exc: Exception) -> None:
        self.set_busy(False)
        self.status_text.set(self.tr("merge_failed_status"))
        if isinstance(exc, PdfMergeError):
            message = self.tr(exc.code, **exc.details)
        else:
            message = str(exc)
        messagebox.showerror(self.tr("app_title"), message)


if __name__ == "__main__":
    app = PdfMergerApp()
    app.mainloop()
