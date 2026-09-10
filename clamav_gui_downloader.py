from datetime import datetime
import os
import shutil
import tempfile

import threading
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from pathlib import Path
import traceback

from cvdupdate.cvdupdate import CVDUpdate

databases = [
    main_db := "main.cvd",
    daily_db := "daily.cvd",
    base_db := "bytecode.cvd",
]


class ClamAVDownloaderGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("ClamAV Definition Downloader")
        self.root.geometry("520x280")
        self.root.resizable(False, False)

        style = ttk.Style()
        style.theme_use("clam")

        # Main Layout Frame
        frame = ttk.Frame(root, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)

        title_label = ttk.Label(
            frame, text="ClamAV Virus Definition Fetcher", font=("Segoe UI", 12, "bold")
        )
        title_label.pack(anchor=tk.W, pady=(0, 5))

        desc_label = ttk.Label(
            frame,
            text="Downloads official Cisco/Talos virus definitions and packages them into a ZIP file.",
            font=("Segoe UI", 9),
        )
        desc_label.pack(anchor=tk.W, pady=(0, 15))
        folder_frame = ttk.Frame(frame)
        folder_frame.pack(fill=tk.X, pady=(0, 15))

        self.selected_dir = tk.StringVar(value="")

        # load last selected directory if it exists
        last_dir_file = Path("last_selected_dir.txt")
        if last_dir_file.exists():
            try:
                with open(last_dir_file, "r") as f:
                    last_dir = f.read().strip()
                    if last_dir and Path(last_dir).exists():
                        self.selected_dir = tk.StringVar(value=last_dir)
                    else:
                        self.selected_dir = tk.StringVar(value="")
            except Exception as e:
                print(f"Error reading last selected directory: {e}")
                self.selected_dir = tk.StringVar(value="")

        folder_label = ttk.Label(
            folder_frame, text="Save Destination Folder:", font=("Segoe UI", 9, "bold")
        )
        folder_label.pack(anchor=tk.W)

        path_entry = ttk.Entry(
            folder_frame, textvariable=self.selected_dir, state="readonly"
        )
        path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5), pady=(5, 0))

        btn_browse = ttk.Button(
            folder_frame, text="Browse...", command=self.browse_folder
        )
        btn_browse.pack(side=tk.RIGHT, pady=(5, 0))

        self.status_var = tk.StringVar(value="Ready to download.")
        self.status_label = ttk.Label(
            frame, textvariable=self.status_var, font=("Segoe UI", 9, "italic")
        )
        self.status_label.pack(anchor=tk.W, pady=(0, 5))

        self.progress = ttk.Progressbar(frame, mode="indeterminate")
        self.progress.pack(fill=tk.X, pady=(0, 15))

        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill=tk.X)

        self.btn_download = ttk.Button(
            btn_frame, text="Start Download", command=self.start_download_thread
        )
        self.btn_download.pack(side=tk.RIGHT)

    def browse_folder(self):
        chosen_dir = filedialog.askdirectory(
            title="Select Folder to Save Definitions ZIP",
            initialdir=self.selected_dir.get(),
        )
        if chosen_dir:
            self.selected_dir.set(chosen_dir)
            # persist dir for next time
            try:
                with open("last_selected_dir.txt", "w") as f:
                    f.write(chosen_dir)
            except Exception as e:
                print(f"Error saving last selected directory: {e}")

    def start_download_thread(self):
        target_dir = Path(self.selected_dir.get())
        if not target_dir.exists():
            messagebox.showerror(
                "Invalid Directory",
                "The selected destination directory does not exist.",
            )
            return

        self.btn_download.config(state=tk.DISABLED)
        self.progress.start(10)
        self.status_var.set("Connecting to Cisco/Talos servers...")
        threading.Thread(
            target=self.run_download, args=(target_dir,), daemon=True
        ).start()

    def run_download(self, target_dir):
        # datetime stamp for the download session
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Work within target_dir
        work_dir = target_dir / "clamav_tmp_workspace"
        zip_output_base = target_dir / f"clamav_definitions_{timestamp}"

        try:
            # Clean workspace
            if work_dir.exists():
                shutil.rmtree(work_dir, ignore_errors=True)
            work_dir.mkdir(parents=True, exist_ok=True)

            print(f"work_dir = {work_dir}")

            cvd = CVDUpdate(db_dir=str(work_dir))
            print("CVDUpdate instantiated")

            for db in databases:
                self.root.after(
                    0, lambda db=db: self.status_var.set(f"Downloading {db}...")
                )
                print(f"Downloading {db}...")
                cvd.db_update(db)
                print(f"{db} downloaded")

            # Check if downloads exist inside the databases folder
            if not work_dir.exists() or not os.listdir(work_dir):
                raise RuntimeError(
                    "Download completed, but no database files were found."
                )

            self.root.after(
                0, lambda: self.status_var.set("Compressing files into ZIP archive...")
            )

            shutil.make_archive(str(zip_output_base), "zip", str(work_dir))

            self.root.after(0, lambda: self.status_var.set("Complete!"))
            self.root.after(
                0,
                lambda: messagebox.showinfo(
                    "Success",
                    f"Successfully created:\n\n{zip_output_base}.zip\n\nUpload this file to your air-gapped system.",
                ),
            )

        except Exception as e:
            print(traceback.format_exc())

            err_msg = str(e)
            self.root.after(0, lambda: self.status_var.set("Download failed."))
            self.root.after(
                0,
                lambda err=err_msg: messagebox.showerror(
                    "Download Error", f"An error occurred:\n\n{err}"
                ),
            )
            print(f"Error during download: {err_msg}")

            print(traceback.format_exc())

        finally:
            # Clean up workspace folder
            if work_dir.exists():
                shutil.rmtree(work_dir, ignore_errors=True)
            self.root.after(0, self.reset_ui)

    def reset_ui(self):
        self.progress.stop()
        self.btn_download.config(state=tk.NORMAL)


if __name__ == "__main__":
    root = tk.Tk()
    app = ClamAVDownloaderGUI(root)
    root.mainloop()
