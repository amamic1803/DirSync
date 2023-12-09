import filecmp
import os
import sys
import tkinter as tk
from logging import Logger
from threading import Thread
from tkinter import filedialog
from tkinter import messagebox

import _tkinter
from dirsync import sync


def resource_path(relative_path=""):
	""" Get absolute path to resource, works for dev and for PyInstaller """
	try:
		# PyInstaller creates a temp folder and stores path in _MEIPASS
		base_path = sys._MEIPASS
	except Exception:
		base_path = os.path.abspath(".")
	return os.path.join(base_path, relative_path)

def are_dir_trees_equal(dir1, dir2):
	"""
	Compare two directories recursively. Files in each directory are
	assumed to be equal if their names and contents are equal.

	@param dir1: First directory path
	@param dir2: Second directory path

	@return: True if the directory trees are the same and
		there were no errors while accessing the directories or files,
		False otherwise.
	"""

	dirs_cmp = filecmp.dircmp(dir1, dir2)
	if len(dirs_cmp.left_only) > 0 or len(dirs_cmp.right_only) > 0 or len(dirs_cmp.funny_files) > 0:
		return False
	(_, mismatch, errors) = filecmp.cmpfiles(dir1, dir2, dirs_cmp.common_files, shallow=False)
	if len(mismatch) > 0 or len(errors) > 0:
		return False
	for common_dir in dirs_cmp.common_dirs:
		new_dir1 = os.path.join(dir1, common_dir)
		new_dir2 = os.path.join(dir2, common_dir)
		if not are_dir_trees_equal(new_dir1, new_dir2):
			return False
	return True


class App:
	def __init__(self):
		self.started = False
		self.sync_thread = None

		self.root = tk.Tk()
		self.root.title("DirSync")
		self.root.geometry(f"500x230"
		                   f"+{self.root.winfo_screenwidth() // 2 - 250}"
		                   f"+{self.root.winfo_screenheight() // 2 - 115}")
		self.root.resizable(False, False)
		self.root.iconbitmap(resource_path("resources/dir-icon.ico"))
		self.root.config(background="#ffffff")

		self.title_lbl = tk.Label(self.root, text="DirSync", font=("Times New Roman Bold", 35),
		                          anchor=tk.CENTER, justify=tk.CENTER,
		                          foreground="#000000", activeforeground="#000000",
		                          background="#ffffff", activebackground="#ffffff",
		                          highlightthickness=0, borderwidth=0)
		self.title_lbl.place(width=500, height=70, x=0, y=0)

		self.description_lbl = tk.Label(self.root, text="Mirror source folder to destination folder",
		                                font=("Segoe UI", 9, "italic", "bold"), anchor=tk.CENTER, justify=tk.CENTER,
		                                foreground="#000000", activeforeground="#000000", background="#ffffff",
		                                activebackground="#ffffff", highlightthickness=0, borderwidth=0)
		self.description_lbl.place(height=20, width=500, x=0, y=80)

		self.source_lbl = tk.Label(self.root, text="Source:", font=("Segoe UI", 10, "bold"),
		                           anchor=tk.CENTER, justify=tk.CENTER,
		                           foreground="#000000", activeforeground="#000000",
		                           background="#ffffff", activebackground="#ffffff",
		                           highlightthickness=0, borderwidth=0)
		self.source_lbl.place(width=90, height=25, x=0, y=105)

		self.destination_lbl = tk.Label(self.root, text="Destination:", font=("Segoe UI", 10, "bold"),
		                                anchor=tk.CENTER, justify=tk.CENTER,
		                                foreground="#000000", activeforeground="#000000",
		                                background="#ffffff", activebackground="#ffffff",
		                                highlightthickness=0, borderwidth=0)
		self.destination_lbl.place(width=90, height=25, x=0, y=135)

		self.source_txt = tk.Entry(self.root, font=("Segoe UI", 9), justify=tk.LEFT,
		                           highlightthickness=1, highlightcolor="grey50",
		                           highlightbackground="grey50", disabledbackground="grey80",
		                           foreground="#000000", background="grey95", borderwidth=0)
		self.source_txt.place(width=320, height=25, x=90, y=105)

		self.target_txt = tk.Entry(self.root, font=("Segoe UI", 9), justify=tk.LEFT,
		                           highlightthickness=1, highlightcolor="grey50",
		                           highlightbackground="grey50", disabledbackground="grey80",
		                           foreground="#000000", background="grey95", borderwidth=0)
		self.target_txt.place(width=320, height=25, x=90, y=135)

		self.browse1_btn = tk.Label(self.root, text="Browse", font=("Segoe UI", 9), cursor="hand2",
		                            anchor=tk.CENTER, justify=tk.CENTER,
		                            background="grey95", activeforeground="grey95", highlightthickness=2,
		                            highlightcolor="#000000", highlightbackground="#000000", borderwidth=0)
		self.browse1_btn.place(y=105, width=80, x=415, height=25)
		self.browse1_btn.bind("<ButtonRelease-1>", lambda event: self.browse_click(self.source_txt))
		self.browse1_btn.bind("<Enter>", lambda event: self.browse1_btn.config(highlightthickness=4) if not self.started else None)
		self.browse1_btn.bind("<Leave>", lambda event: self.browse1_btn.config(highlightthickness=2) if not self.started else None)

		self.browse2_btn = tk.Label(self.root, text="Browse", font=("Segoe UI", 9), cursor="hand2",
		                            anchor=tk.CENTER, justify=tk.CENTER,
		                            background="grey95", activeforeground="grey95", highlightthickness=2,
		                            highlightcolor="#000000", highlightbackground="#000000", borderwidth=0)
		self.browse2_btn.place(y=135, width=80, x=415, height=25)
		self.browse2_btn.bind("<ButtonRelease-1>", lambda event: self.browse_click(self.target_txt))
		self.browse2_btn.bind("<Enter>", lambda event: self.browse2_btn.config(highlightthickness=4) if not self.started else None)
		self.browse2_btn.bind("<Leave>", lambda event: self.browse2_btn.config(highlightthickness=2) if not self.started else None)

		self.exit_btn = tk.Label(self.root, text="Quit", font=("Segoe UI", 10, "bold"), cursor="hand2",
		                         anchor=tk.CENTER, justify=tk.CENTER,
		                         background="grey95", activeforeground="grey95", highlightthickness=2,
		                         highlightcolor="red", highlightbackground="red", borderwidth=0)
		self.exit_btn.place(y=180, width=100, x=40, height=30)
		self.exit_btn.bind("<ButtonRelease-1>", lambda event: self.quit())
		self.exit_btn.bind("<Enter>", lambda event: self.exit_btn.config(highlightthickness=4))
		self.exit_btn.bind("<Leave>", lambda event: self.exit_btn.config(highlightthickness=2))

		self.sync_btn = tk.Label(self.root, text="Mirror", font=("Segoe UI", 10, "bold"), cursor="hand2",
		                         anchor=tk.CENTER, justify=tk.CENTER,
		                         background="grey95", activeforeground="grey95", highlightthickness=2,
		                         highlightcolor="#000000", highlightbackground="#000000", borderwidth=0)
		self.sync_btn.place(y=180, width=100, x=360, height=30)
		self.sync_btn.bind("<ButtonRelease-1>", lambda event: self.sync_click())
		self.sync_btn.bind("<Enter>", lambda event: self.sync_btn.config(highlightthickness=4) if not self.started else None)
		self.sync_btn.bind("<Leave>", lambda event: self.sync_btn.config(highlightthickness=2) if not self.started else None)

		self.syncing_lbl = tk.Label(self.root, text="", font=("Segoe UI", 9, "italic", "bold"),
		                            anchor=tk.CENTER, justify=tk.CENTER,
		                            foreground="#000000", activeforeground="#000000", background="#ffffff",
		                            activebackground="#ffffff", highlightthickness=0, borderwidth=0)
		self.syncing_lbl.place(height=30, width=100, x=200, y=180)

		self.root.mainloop()

		self.quit()

	def browse_click(self, entry):
		if not self.started:
			initial_dir = os.path.dirname(entry.get())
			if not os.path.isdir(initial_dir):
				initial_dir = os.path.dirname(sys.executable)
			if not os.path.isdir(initial_dir):
				initial_dir = os.path.join(os.path.expanduser('~'), 'Desktop')

			folder = filedialog.askdirectory(parent=self.root, initialdir=initial_dir)

			if folder != "":
				entry.delete(0, tk.END)
				entry.insert(0, folder)
				entry.xview_moveto(1)

	def sync_click(self):
		if not self.started:
			source_dir = self.source_txt.get()
			target_dir = self.target_txt.get()

			not_existing = False
			if not os.path.exists(source_dir):
				not_existing = True
				self.source_txt.delete(0, tk.END)
			if not os.path.exists(target_dir):
				not_existing = True
				self.target_txt.delete(0, tk.END)
			if not_existing:
				messagebox.showerror(title="Error!", message="Invalid folder selected!", parent=self.root)
				return

			if not messagebox.askyesno(title="Mirror",
			                           message="Running this program will mirror source folder to destination folder. "
			                                   "Any other files in the destination folder will be deleted.\n"
			                                   "Are you sure you want to proceed?"):
				return

			self.started = True
			self.syncing_lbl.config(text="Mirroring...")
			self.browse1_btn.config(cursor="arrow", background="grey80",
			                        activebackground="grey80", highlightthickness=2)
			self.browse2_btn.config(cursor="arrow", background="grey80",
			                        activebackground="grey80", highlightthickness=2)
			self.source_txt.config(state="disabled")
			self.target_txt.config(state="disabled")
			self.sync_btn.config(cursor="arrow", background="grey80", activebackground="grey80", highlightthickness=2)

			self.sync_thread = Thread(target=self.syncing, args=(source_dir, target_dir), daemon=True)
			self.sync_thread.start()

	def syncing(self, source_dir, target_dir):
		equal_dirs = False

		for _ in range(3):
			sync(source_dir, target_dir, 'sync', logger=Logger(name="capture-stdout"),
			     purge=True, force=True, create=True)
			if are_dir_trees_equal(source_dir, target_dir):
				equal_dirs = True
				break

		self.started = False
		self.syncing_lbl.config(text="")
		self.browse1_btn.config(cursor="hand2", background="grey95", activebackground="grey95", highlightthickness=2)
		self.browse2_btn.config(cursor="hand2", background="grey95", activebackground="grey95", highlightthickness=2)
		self.source_txt.config(state="normal")
		self.target_txt.config(state="normal")
		self.sync_btn.config(cursor="hand2", background="grey95", activebackground="grey95", highlightthickness=2)

		if equal_dirs:
			messagebox.showinfo("Completed!", "Folder was mirrored successfully!", parent=self.root)
		else:
			messagebox.showerror("Failed!", "Mirroring failed!", parent=self.root)

	def quit(self):
		try:
			self.root.destroy()
		except _tkinter.TclError:
			pass


def main():
	App()


if __name__ == '__main__':
	main()
