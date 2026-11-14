"""DHMS Desktop presentation layer; all Tk access stays on the main thread."""
from __future__ import annotations

from datetime import datetime
from pathlib import Path
import queue
import math
import sys
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from .core import DataError, ImportCancelled, backtest, export_analysis, load_csv, summarize
from .storage import load_settings, save_settings

VERSION = "1.0.0"
BG = "#0d1117"
PANEL = "#151d29"
TEXT = "#e6edf3"
MUTED = "#94a3b8"
BLUE = "#79c0ff"


def resource_samples() -> Path:
    """Resolve the same synthetic resources in source and PyInstaller bundles."""
    return Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parents[1])) / "samples"


def sample_file() -> Path:
    choices = sorted(resource_samples().glob("*.csv"))
    if not choices:
        raise DataError("The bundled sample is missing. Download a complete application archive.")
    return choices[0]


def display_points(points, limit=1000):
    """Keep endpoints and bucket extrema in time order for bounded canvas work."""
    if len(points) <= limit:
        return list(points)
    result = [points[0]]
    buckets = max(1, (limit - 2) // 2)
    for bucket in range(buckets):
        first = 1 + (len(points) - 2) * bucket // buckets
        last = 1 + (len(points) - 2) * (bucket + 1) // buckets
        indexes = range(first, max(first + 1, last))
        low = min(indexes, key=lambda i: points[i][1])
        high = max(indexes, key=lambda i: points[i][1])
        result.extend(points[i] for i in sorted({low, high}))
    result.append(points[-1])
    return result


def chart_bounds(values):
    """Return finite normalized axis limits even for opposite large values."""
    if not values or not all(math.isfinite(value) for value in values):
        raise DataError("Chart measurements must be finite and nonempty.")
    scale = max(abs(value) for value in values) or 1.0
    low, high = min(values) / scale, max(values) / scale
    padding = (high - low) * 0.08 if high != low else 0.05
    representable = min(sys.float_info.max / scale, 2.0)
    return scale, max(low - padding, -representable), min(high + padding, representable)


class Application:
    """One bounded worker, queue-based delivery, and atomic dataset replacement."""

    def __init__(self, root: tk.Tk, *, persist_settings=True):
        self.root = root
        self.persist_settings = persist_settings
        preferences = load_settings() if persist_settings else {}
        self.dataset = None
        self.analysis = None
        self.series = ()
        self.busy = False
        self.closed = False
        self.cancel_event = threading.Event()
        self.messages = queue.Queue(maxsize=8)
        self.token = 0
        self.after_id = None
        self.redraw_id = None
        self.cow = tk.StringVar(value="All cows")
        self.cow_lookup = {"All cows": None}
        preferred_metric = preferences.get("metric")
        self.metric = tk.StringVar(value=preferred_metric if preferred_metric in ("activity", "temperature") else "activity")
        preferred_format = preferences.get("import_format")
        formats = ("Canonical long CSV", "Legacy activity wide", "Legacy temperature wide")
        self.import_format = tk.StringVar(value=preferred_format if preferred_format in formats else formats[0])
        preferred_window = preferences.get("window")
        valid_window = type(preferred_window) is int and 1 <= preferred_window <= 10000
        self.window = tk.StringVar(value=str(preferred_window) if valid_window else "5")
        self.status = tk.StringVar(value="Open your CSV, or load the synthetic sample to explore the application.")
        self.source = tk.StringVar(value="No data loaded")
        self.summary = tk.StringVar(value="Observations —    Mean —    Range —")
        self.baseline = tk.StringVar(value="Chronological holdout baseline · no analysis yet")
        self.controls = []
        self._build()
        root.protocol("WM_DELETE_WINDOW", self.close)
        root.bind("<Control-o>", lambda _event: self.open_file())
        root.bind("<Control-e>", lambda _event: self.export_file())
        root.bind("<Control-q>", lambda _event: self.close())
        self.after_id = root.after(75, self._poll)

    def _build(self):
        self.root.title(f"DHMS Desktop {VERSION} — Dairy Herd Monitoring Research")
        self.root.geometry("1180x790")
        self.root.minsize(960, 660)
        self.root.configure(bg=BG)
        style = ttk.Style(self.root)
        if "clam" in style.theme_names():
            style.theme_use("clam")
        style.configure("TFrame", background=BG)
        style.configure("TLabel", background=BG, foreground=TEXT, font=("TkDefaultFont", 11))
        style.configure("Muted.TLabel", foreground=MUTED)
        style.configure("Title.TLabel", font=("TkDefaultFont", 23, "bold"))
        style.configure("TButton", padding=(13, 8), background="#203552", foreground=TEXT)
        style.map("TButton", background=[("active", "#2b4a72"), ("disabled", "#19212e")], foreground=[("disabled", "#758399")])
        style.configure("TCombobox", fieldbackground=PANEL, foreground=TEXT, padding=6)
        style.map("TCombobox", fieldbackground=[("readonly", PANEL)], foreground=[("readonly", TEXT)])
        style.configure("TEntry", fieldbackground=PANEL, foreground=TEXT, padding=6)
        style.configure("Horizontal.TProgressbar", background=BLUE, troughcolor=PANEL)
        self.root.option_add("*TCombobox*Listbox.background", PANEL)
        self.root.option_add("*TCombobox*Listbox.foreground", TEXT)
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(3, weight=1)
        menu = tk.Menu(self.root)
        file_menu = tk.Menu(menu, tearoff=False)
        file_menu.add_command(label="Open CSV…", accelerator="Ctrl+O", command=self.open_file)
        file_menu.add_command(label="Load synthetic sample", command=self.load_sample)
        file_menu.add_command(label="Export analysis…", accelerator="Ctrl+E", command=self.export_file)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", accelerator="Ctrl+Q", command=self.close)
        menu.add_cascade(label="File", menu=file_menu)
        help_menu = tk.Menu(menu, tearoff=False)
        help_menu.add_command(label="CSV format and research limits", command=self.help)
        menu.add_cascade(label="Help", menu=help_menu)
        self.root.config(menu=menu)

        header = ttk.Frame(self.root, padding=(24, 20, 24, 12))
        header.grid(row=0, column=0, sticky="ew")
        ttk.Label(header, text="DHMS Desktop", style="Title.TLabel").pack(anchor="w")
        ttk.Label(header, text="Dairy herd time-series explorer  /  activity & temperature", style="Muted.TLabel").pack(anchor="w", pady=(6, 0))
        tools = ttk.Frame(self.root, padding=(24, 0, 24, 12))
        tools.grid(row=1, column=0, sticky="ew")
        self.open_button = ttk.Button(tools, text="Open CSV", command=self.open_file)
        self.open_button.pack(side="left")
        self.sample_button = ttk.Button(tools, text="Load synthetic sample", command=self.load_sample)
        self.sample_button.pack(side="left", padx=8)
        self.format_box = ttk.Combobox(tools, textvariable=self.import_format, values=("Canonical long CSV", "Legacy activity wide", "Legacy temperature wide"), state="readonly", width=25)
        self.format_box.pack(side="left", padx=(10, 8))
        self.cancel_button = ttk.Button(tools, text="Cancel import", command=self.cancel, state="disabled")
        self.cancel_button.pack(side="right")
        self.export_button = ttk.Button(tools, text="Export analysis", command=self.export_file)
        self.export_button.pack(side="right", padx=8)
        self.controls.extend((self.open_button, self.sample_button, self.format_box, self.export_button))

        selectors = ttk.Frame(self.root, padding=(24, 0, 24, 12))
        selectors.grid(row=2, column=0, sticky="ew")
        for column in (0, 1):
            selectors.columnconfigure(column, weight=1)
        ttk.Label(selectors, text="Animal / herd").grid(row=0, column=0, sticky="w")
        ttk.Label(selectors, text="Measurement").grid(row=0, column=1, sticky="w", padx=(16, 0))
        ttk.Label(selectors, text="Baseline window").grid(row=0, column=2, sticky="w", padx=(16, 0))
        self.cow_box = ttk.Combobox(selectors, textvariable=self.cow, values=("All cows",), state="readonly")
        self.cow_box.grid(row=1, column=0, sticky="ew", pady=(5, 0))
        self.metric_box = ttk.Combobox(selectors, textvariable=self.metric, values=("activity", "temperature"), state="readonly", width=21)
        self.metric_box.grid(row=1, column=1, sticky="ew", padx=(16, 0), pady=(5, 0))
        self.window_entry = ttk.Entry(selectors, textvariable=self.window, width=9)
        self.window_entry.grid(row=1, column=2, padx=(16, 0), pady=(5, 0))
        self.apply_button = ttk.Button(selectors, text="Update view", command=self.refresh)
        self.apply_button.grid(row=1, column=3, padx=(16, 0), pady=(5, 0))
        self.controls.extend((self.cow_box, self.metric_box, self.window_entry, self.apply_button))
        self.cow_box.bind("<<ComboboxSelected>>", lambda _event: self.refresh())
        self.metric_box.bind("<<ComboboxSelected>>", lambda _event: self.refresh())
        self.window_entry.bind("<Return>", lambda _event: self.refresh())

        body = ttk.Frame(self.root, padding=(24, 0, 24, 0))
        body.grid(row=3, column=0, sticky="nsew")
        body.columnconfigure(0, weight=1)
        body.rowconfigure(2, weight=1)
        ttk.Label(body, textvariable=self.source, style="Muted.TLabel", wraplength=1080).grid(row=0, column=0, sticky="w", pady=(0, 9))
        ttk.Label(body, textvariable=self.summary).grid(row=1, column=0, sticky="w", pady=(0, 10))
        self.canvas = tk.Canvas(body, bg=PANEL, highlightthickness=1, highlightbackground="#2a384b", height=310)
        self.canvas.grid(row=2, column=0, sticky="nsew")
        self.canvas.bind("<Configure>", self._schedule_draw)
        ttk.Label(body, textvariable=self.baseline, style="Muted.TLabel", wraplength=1080).grid(row=3, column=0, sticky="w", pady=(10, 0))
        footer = ttk.Frame(self.root, padding=(24, 12, 24, 16))
        footer.grid(row=4, column=0, sticky="ew")
        ttk.Label(footer, text="Observed data + trailing-mean baseline. Research exploration only; not a veterinary diagnostic tool.", style="Muted.TLabel").pack(anchor="w")
        self.progress = ttk.Progressbar(footer, mode="indeterminate")
        self.progress.pack(fill="x", pady=(10, 7))
        ttk.Label(footer, textvariable=self.status, style="Muted.TLabel", wraplength=1080).pack(anchor="w")
        self._draw()

    def _set_busy(self, value, operation=""):
        self.busy = value
        for control in self.controls:
            if value:
                control.configure(state="disabled")
            else:
                control.configure(state="readonly" if isinstance(control, ttk.Combobox) else "normal")
        self.cancel_button.configure(state="normal" if value and operation == "load" else "disabled")
        if value:
            self.progress.start(12)
        else:
            self.progress.stop()

    def _start(self, operation, work, success):
        if self.busy or self.closed:
            return
        self.token += 1
        token = self.token
        self.cancel_event = threading.Event()
        cancel_event = self.cancel_event
        self._set_busy(True, operation)

        def run():
            try:
                result = work(cancel_event)
                message = (token, "ok", result, success)
            except ImportCancelled:
                message = (token, "cancelled", None, success)
            except Exception as error:
                message = (token, "error", str(error), success)
            try:
                self.messages.put_nowait(message)
            except queue.Full:
                pass

        threading.Thread(target=run, name=f"dhms-{operation}", daemon=True).start()

    def _poll(self):
        if self.closed:
            return
        try:
            token, kind, result, success = self.messages.get_nowait()
        except queue.Empty:
            pass
        else:
            if token == self.token:
                self._set_busy(False)
                if kind == "ok":
                    success(result)
                elif kind == "cancelled":
                    self.status.set("Import cancelled. Previously loaded data is unchanged.")
                else:
                    self.status.set("Operation failed. Previously loaded data is unchanged.")
                    messagebox.showerror("DHMS — operation could not complete", result, parent=self.root)
        self.after_id = self.root.after(75, self._poll)

    def open_file(self):
        if self.busy or self.closed:
            return
        path = filedialog.askopenfilename(parent=self.root, title="Open herd observations CSV", filetypes=(("CSV files", "*.csv"), ("All files", "*.*")))
        if path:
            self.load_path(Path(path))

    def load_sample(self):
        if self.busy:
            return
        try:
            self.import_format.set("Canonical long CSV")
            self.load_path(sample_file(), synthetic=True)
        except DataError as error:
            messagebox.showerror("Sample unavailable", str(error), parent=self.root)

    def load_path(self, path, synthetic=False):
        choice = self.import_format.get()
        legacy = "activity" if choice == "Legacy activity wide" else "temperature" if choice == "Legacy temperature wide" else None
        self.status.set("Reading and validating CSV…")

        def success(dataset):
            self.dataset = dataset
            self.cow_lookup = {"All cows": None, **{f"Animal: {animal}": animal for animal in dataset.cow_ids}}
            self.cow_box.configure(values=tuple(self.cow_lookup))
            self.cow.set("All cows")
            self.metric_box.configure(values=dataset.metrics)
            self.metric.set(self.metric.get() if self.metric.get() in dataset.metrics else dataset.metrics[0])
            prefix = "SYNTHETIC SAMPLE · " if synthetic else ""
            clock = "UTC timestamps" if dataset.timezone_aware else "naive timestamps (source local time)"
            self.source.set(f"{prefix}{dataset.source_name} · {len(dataset.observations):,} rows · {len(dataset.cow_ids):,} animals · {clock}")
            self.refresh()

        self._start("load", lambda cancel: load_csv(path, cancel=cancel.is_set, legacy_metric=legacy), success)

    def cancel(self):
        if self.busy:
            self.cancel_event.set()
            self.status.set("Cancelling import…")

    def _selection(self):
        try:
            window = int(self.window.get())
        except ValueError as error:
            raise DataError("Baseline window must be a positive whole number.") from error
        if not 1 <= window <= 10000:
            raise DataError("Baseline window must be between 1 and 10,000 observations.")
        if self.cow.get() not in self.cow_lookup:
            raise DataError("Select an animal from the list.")
        return self.cow_lookup[self.cow.get()], self.metric.get(), window

    def refresh(self):
        if self.busy or self.dataset is None:
            return
        try:
            cow, metric, window = self._selection()
        except DataError as error:
            messagebox.showerror("Invalid baseline window", str(error), parent=self.root)
            return
        dataset = self.dataset
        self.series = ()
        self.analysis = None
        self.summary.set("Preparing selection…")
        self.baseline.set("Preparing chronological baseline…")
        self._draw()
        self.status.set("Preparing time series and chronological baseline…")

        def work(_cancel):
            summary = summarize(dataset, cow, metric)
            series = dataset.series(cow, metric)
            try:
                result = backtest(dataset, cow, metric, window=window, test_fraction=0.2)
                note = ""
            except DataError as error:
                result, note = None, str(error)
            return summary, series, result, note

        def success(result):
            summary, self.series, self.analysis, note = result
            self.summary.set(f"Observations {summary.count:,}     Mean {summary.mean:.4g}     Minimum {summary.minimum:.4g}     Maximum {summary.maximum:.4g}")
            if self.analysis is not None:
                analysis = self.analysis
                self.baseline.set(f"Trailing mean · window {analysis.window} · chronological final 20% holdout · {len(analysis.points):,} predictions · MAE {analysis.mae:.4g} · training prefix {analysis.training_count:,} observations")
            else:
                self.baseline.set(f"Baseline unavailable: {note}")
            self.status.set("Ready. Imported observations remain in memory; original CSV is unchanged.")
            self._draw()

        self._start("analysis", work, success)

    def export_file(self):
        if self.busy or self.dataset is None:
            if self.dataset is None and not self.busy:
                messagebox.showinfo("Load data first", "Open a CSV or load the synthetic sample before exporting.", parent=self.root)
            return
        try:
            cow, metric, window = self._selection()
        except DataError as error:
            messagebox.showerror("Invalid baseline window", str(error), parent=self.root)
            return
        path = filedialog.asksaveasfilename(parent=self.root, title="Export chronological baseline analysis", defaultextension=".csv", initialfile="dhms-analysis.csv", filetypes=(("CSV file", "*.csv"),))
        if path:
            dataset = self.dataset
            self.status.set("Writing analysis atomically…")
            self._start("export", lambda _cancel: export_analysis(path, dataset, cow, metric, window=window, test_fraction=0.2), lambda _result: self.status.set(f"Export saved to {path}"))

    def _schedule_draw(self, _event=None):
        if self.redraw_id is not None:
            self.root.after_cancel(self.redraw_id)
        self.redraw_id = self.root.after(80, self._draw)

    def _draw(self):
        self.redraw_id = None
        canvas = self.canvas
        canvas.delete("all")
        width, height = max(canvas.winfo_width(), 400), max(canvas.winfo_height(), 250)
        if not self.series:
            headline = "Your herd data, clearly plotted." if self.dataset is None else "Select an animal and measurement."
            detail = "Open a CSV or load the synthetic sample. No account or network connection required." if self.dataset is None else "If a selection has no observations, choose another metric or animal."
            canvas.create_text(width / 2, height / 2 - 18, text=headline, fill=TEXT, font=("TkDefaultFont", 20, "bold"))
            canvas.create_text(width / 2, height / 2 + 24, text=detail, fill=MUTED, font=("TkDefaultFont", 11), width=width - 80)
            return
        left, right, top, bottom = 75, width - 28, 37, height - 56
        baseline = [(p.timestamp, p.predicted) for p in self.analysis.points] if self.analysis else []
        values = [value for _time, value in self.series] + [value for _time, value in baseline]
        scale, minimum, maximum = chart_bounds(values)
        first, last = self.series[0][0], self.series[-1][0]
        span = max((last - first).total_seconds(), 1)

        def xy(timestamp, value):
            return left + (timestamp - first).total_seconds() / span * (right - left), bottom - (value / scale - minimum) / (maximum - minimum) * (bottom - top)

        for i in range(5):
            fraction = i / 4
            yy = top + fraction * (bottom - top)
            value = (maximum - fraction * (maximum - minimum)) * scale
            value = max(-sys.float_info.max, min(sys.float_info.max, value))
            canvas.create_line(left, yy, right, yy, fill="#2a3547")
            canvas.create_text(left - 10, yy, text=f"{value:.4g}", fill=MUTED, anchor="e", font=("TkDefaultFont", 10))
        for i in range(4):
            fraction = i / 3
            xx = left + fraction * (right - left)
            timestamp = first + (last - first) * fraction
            canvas.create_text(xx, bottom + 23, text=timestamp.strftime("%Y-%m-%d\n%H:%M"), fill=MUTED, font=("TkDefaultFont", 9))
        observed = display_points(self.series)
        coords = [coordinate for time, value in observed for coordinate in xy(time, value)]
        if len(observed) == 1:
            xx, yy = coords
            canvas.create_oval(xx - 3, yy - 3, xx + 3, yy + 3, fill=BLUE, outline="")
        elif coords:
            canvas.create_line(*coords, fill=BLUE, width=2)
        if len(baseline) > 1:
            canvas.create_line(*[coordinate for time, value in display_points(baseline) for coordinate in xy(time, value)], fill="#e3b86c", width=2, dash=(5, 4))
        metric = self.metric.get()
        label = "Temperature (assumed °C)" if metric == "temperature" else "Activity (source interval units)"
        canvas.create_text(left, 17, text=f"{label} · observed", fill=BLUE, anchor="w", font=("TkDefaultFont", 10, "bold"))
        canvas.create_text(right, 17, text="Dashed gold: holdout baseline", fill="#e3b86c", anchor="e", font=("TkDefaultFont", 10))

    def help(self):
        messagebox.showinfo("DHMS Desktop — data and limits", "Canonical CSV: timestamp,cow_id,activity,temperature\nAt least one measurement column is required. Use ISO timestamps.\n\nFor historical wide data, select Legacy activity wide or Legacy temperature wide before opening. The first column is Date or Unnamed: 0; remaining cow columns are numeric. Group mean is recomputed.\n\nAll cows means the mean of available animal values at each timestamp. A changing animal set can change that mean. The final 20% of the selected time series forms a chronological holdout. Each trailing-mean prediction uses preceding observations, including earlier actual holdout observations. It is a descriptive baseline, not a health model.\n\nData remains local. Source files are never modified. Do not interpret activity or temperature variation as a veterinary diagnosis.", parent=self.root)

    def close(self):
        if self.closed:
            return
        self.closed = True
        self.cancel_event.set()
        self.token += 1
        if self.persist_settings:
            try:
                selected_window = int(self.window.get())
                save_settings({"window": selected_window if 1 <= selected_window <= 10000 else 5,
                               "metric": self.metric.get(), "import_format": self.import_format.get()})
            except (DataError, ValueError, OSError):
                # An unwritable preference folder must never prevent shutdown.
                pass
        for callback in (self.after_id, self.redraw_id):
            if callback is not None:
                try:
                    self.root.after_cancel(callback)
                except tk.TclError:
                    pass
        self.root.destroy()


def main():
    root = tk.Tk()
    Application(root)
    root.mainloop()


def smoke_test():
    """Exercise real Tcl/Tk, bundled sample and worker delivery, then close."""
    import time

    root = tk.Tk()
    root.withdraw()
    app = Application(root, persist_settings=False)
    try:
        app.load_sample()
        deadline = time.monotonic() + 15
        while (app.busy or app.dataset is None or not app.series) and time.monotonic() < deadline:
            root.update()
            time.sleep(0.01)
        assert app.dataset is not None and app.series and app.analysis is not None and not app.busy
        for cow in ("Animal: " + app.dataset.cow_ids[0], "All cows"):
            app.cow.set(cow)
            app.refresh()
            while app.busy and time.monotonic() < deadline:
                root.update()
                time.sleep(0.01)
            assert not app.busy and app.analysis is not None
            app._draw()
            assert app.canvas.find_all()
    finally:
        app.close()
    if sys.stdout is not None:
        print("Tk construction, async sample loading, analysis, cow selection, drawing and shutdown passed.")


if __name__ == "__main__":
    main()
