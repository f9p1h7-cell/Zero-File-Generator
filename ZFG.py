from pathlib import Path
import tkinter as tk
from tkinter import messagebox, ttk
from typing import Optional

MIN_ZEROS = 1
MAX_ZEROS = 80_000_000_000_000_000_000_000_000_000_000
CHUNK_SIZE = 1_048_576


def format_approx_size(num_bytes: int) -> str:
    units = ["B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB", "RB", "QB"]
    size = float(num_bytes)
    for unit in units:
        if size < 1024 or unit == units[-1]:
            return f"{size:.2f} {unit}"
        size /= 1024
    return f"{num_bytes:,} B"


def create_zero_file(output_path: Path, zero_count: int, progress_callback=None) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    chunk = "0" * CHUNK_SIZE
    remaining = zero_count
    written = 0

    with output_path.open("w", encoding="ascii") as f:
        while remaining > 0:
            write_size = min(remaining, CHUNK_SIZE)
            f.write(chunk[:write_size])
            remaining -= write_size
            written += write_size
            if progress_callback and written % (CHUNK_SIZE * 32) == 0:
                progress_callback(written, zero_count)

    if progress_callback:
        progress_callback(zero_count, zero_count)


class ZeroGeneratorApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Zero File Generator")
        self.root.resizable(False, False)

        self.target = Path("./generated_zeros/zeros_custom.txt").resolve()

        frame = ttk.Frame(root, padding=16)
        frame.grid(row=0, column=0, sticky="nsew")

        ttk.Label(
            frame,
            text="Number of '0' characters (1 to 80 nonillion):",
        ).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 6))

        self.count_var = tk.StringVar(value="8000000")
        self.count_var.trace_add("write", self.on_count_change)
        self.entry = ttk.Entry(frame, textvariable=self.count_var, width=38)
        self.entry.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 6))
        self.entry.focus()

        self.size_var = tk.StringVar()
        ttk.Label(frame, textvariable=self.size_var).grid(
            row=2, column=0, columnspan=2, sticky="w", pady=(0, 10)
        )

        self.progress = ttk.Progressbar(
            frame, orient="horizontal", length=290, mode="determinate"
        )
        self.progress.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(0, 6))

        self.status_var = tk.StringVar(value="Enter a count and click Generate.")
        ttk.Label(frame, textvariable=self.status_var).grid(
            row=4, column=0, columnspan=2, sticky="w", pady=(0, 12)
        )

        self.generate_btn = ttk.Button(frame, text="Generate", command=self.on_generate)
        self.generate_btn.grid(row=5, column=0, sticky="ew", padx=(0, 6))

        ttk.Button(frame, text="Cancel", command=self.root.destroy).grid(
            row=5, column=1, sticky="ew"
        )

        self.update_size_preview()

    def parse_count_quiet(self) -> Optional[int]:
        raw = self.count_var.get().replace(",", "").replace("_", "").strip()
        if not raw:
            return None
        try:
            count = int(raw)
        except ValueError:
            return None
        if count < MIN_ZEROS or count > MAX_ZEROS:
            return None
        return count

    def update_size_preview(self) -> None:
        raw = self.count_var.get().replace(",", "").replace("_", "").strip()
        if not raw:
            self.size_var.set("Space needed: —")
            return
        try:
            count = int(raw)
        except ValueError:
            self.size_var.set("Space needed: invalid number")
            return

        if count < MIN_ZEROS or count > MAX_ZEROS:
            self.size_var.set("Space needed: out of range (1 – 80 nonillion)")
            return

        approx = format_approx_size(count)
        self.size_var.set(f"Space needed: ~{approx} ({count:,} bytes)")

    def on_count_change(self, *_args) -> None:
        self.update_size_preview()

    def parse_count(self) -> Optional[int]:
        raw = self.count_var.get().replace(",", "").replace("_", "").strip()
        try:
            count = int(raw)
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid whole number.")
            return None

        if count < MIN_ZEROS or count > MAX_ZEROS:
            messagebox.showerror(
                "Out of Range",
                f"Enter a number between {MIN_ZEROS:,} and {MAX_ZEROS:,}.",
            )
            return None

        return count

    def update_progress(self, done: int, total: int) -> None:
        pct = (done / total) * 100
        self.progress["value"] = pct
        self.status_var.set(f"Writing... {pct:.1f}% ({done:,} / {total:,})")
        self.root.update_idletasks()

    def on_generate(self) -> None:
        count = self.parse_count()
        if count is None:
            return

        approx = format_approx_size(count)
        proceed = messagebox.askyesno(
            title="Warning: File Creation",
            message=(
                f"This will create a text file containing {count:,} zeros "
                f"(approx. {approx} / {count:,} bytes of disk space).\n\n"
                f"Target location:\n{self.target}\n\n"
                "Do you want to continue?"
            ),
            icon="warning",
        )

        if not proceed:
            self.status_var.set("Cancelled. No file was created.")
            messagebox.showinfo("Cancelled", "No files were created.")
            return

        self.generate_btn.state(["disabled"])
        self.progress["value"] = 0
        self.status_var.set("Starting...")
        self.root.update_idletasks()

        try:
            create_zero_file(self.target, count, self.update_progress)
            actual_size = self.target.stat().st_size
            self.status_var.set("Completed.")
            messagebox.showinfo(
                "Done",
                f"Created:\n{self.target}\nSize: {actual_size:,} bytes",
            )
        except OSError as exc:
            self.status_var.set("Error while writing file.")
            messagebox.showerror("File Error", f"Could not write file:\n{exc}")
        finally:
            self.generate_btn.state(["!disabled"])


def main() -> None:
    root = tk.Tk()
    ZeroGeneratorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
