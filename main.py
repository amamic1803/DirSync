from tkinter import *
from tkinter import filedialog
from tkinter import messagebox
import _tkinter
import os
import sys
from dirsync import sync
import filecmp
from threading import Thread
import psutil


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

def syncing():
	global started

	source_dir = source_txt.get()
	target_dir = target_txt.get()

	not_existing = False
	if not os.path.exists(source_dir):
		not_existing = True
		source_txt.delete(0, END)
	if not os.path.exists(target_dir):
		not_existing = True
		target_txt.delete(0, END)
	if not_existing:
		messagebox.showerror(title="Error!", message="Invalid folder selected!", parent=root)
		return

	if not messagebox.askyesno(title="Mirror", message="Running this program will delete any files that are in destination, but not in source folder.\nAre you sure you want to proceed?"):
		return

	started = True
	syncing_lbl.config(text="Mirroring...")
	browse1_btn.config(background="grey80", activebackground="grey80", highlightthickness=2)
	browse2_btn.config(background="grey80", activebackground="grey80", highlightthickness=2)
	source_txt.config(state="disabled")
	target_txt.config(state="disabled")
	sync_btn.config(background="grey80", activebackground="grey80", highlightthickness=2)

	num = 0
	while num < 3:
		num += 1

		sync(source_dir, target_dir, 'sync', purge=True, force=True, create=True)

		if are_dir_trees_equal(source_dir, target_dir):
			loop_info = True
			break
		else:
			loop_info = False

	started = True
	syncing_lbl.config(text="")
	browse1_btn.config(background="grey95", activebackground="grey95", highlightthickness=2)
	browse2_btn.config(background="grey95", activebackground="grey95", highlightthickness=2)
	source_txt.config(state="normal")
	target_txt.config(state="normal")
	sync_btn.config(background="grey95", activebackground="grey95", highlightthickness=2)

	if loop_info:
		messagebox.showinfo("Completed!", "Folder was mirrored successfully!", parent=root)
	else:
		messagebox.showerror("Failed!", "Mirroring failed!", parent=root)

def sync_click(event):
	global sync_process, started
	if not started:
		started = True

		sync_process = Thread(target=syncing)
		sync_process.start()

def exit_click(event=None):
	global sync_process
	try:
		root.destroy()
	except _tkinter.TclError:
		pass
	psutil.Process(os.getpid()).kill()

def browse_click(event, ent):
	folder = filedialog.askdirectory(parent=root, initialdir=os.getcwd())
	if folder != "":
		ent.delete(0, END)
		ent.insert(0, folder)

def change_thickness(event, widget, typ, t_l, t_h, started):
	if not started:
		if typ:
			widget.config(highlightthickness=t_l)
		else:
			widget.config(highlightthickness=t_h)

def change_exit_thickness(event, widget, typ, t_l, t_h):
	if typ:
		widget.config(highlightthickness=t_l)
	else:
		widget.config(highlightthickness=t_h)

def resource_path(relative_path=""):
	""" Get absolute path to resource, works for dev and for PyInstaller """
	try:
		# PyInstaller creates a temp folder and stores path in _MEIPASS
		base_path = sys._MEIPASS
	except Exception:
		base_path = os.path.abspath(".")
	return os.path.join(base_path, relative_path)


if __name__ == '__main__':
	started = False
	sync_process = None

	root = Tk()
	root.title("DirSync")
	root.geometry(f"500x230+{root.winfo_screenwidth() // 2 - 250}+{root.winfo_screenheight() // 2 - 115}")
	root.resizable(False, False)
	root.iconbitmap(resource_path("DirSync - icon.ico"))
	root.config(background="#ffffff")

	title_lbl = Label(root, text="DirSync", font=("Times New Roman Bold", 35), anchor=CENTER, justify=CENTER, foreground="#000000", activeforeground="#000000", background="#ffffff", activebackground="#ffffff", highlightthickness=0, borderwidth=0)
	title_lbl.place(width=500, height=70, x=0, y=0)

	description_lbl = Label(root, text="Mirror source folder to destination folder", font=("Segoe UI", 9, "italic", "bold"), anchor=CENTER, justify=CENTER, foreground="#000000", activeforeground="#000000", background="#ffffff", activebackground="#ffffff", highlightthickness=0, borderwidth=0)
	description_lbl.place(height=20, width=500, x=0, y=80)

	source_lbl = Label(root, text="Source:", font=("Segoe UI", 10, "bold"), anchor=CENTER, justify=CENTER, foreground="#000000", activeforeground="#000000", background="#ffffff", activebackground="#ffffff", highlightthickness=0, borderwidth=0)
	source_lbl.place(width=90, height=25, x=0, y=105)

	destination_lbl = Label(root, text="Destination:", font=("Segoe UI", 10, "bold"), anchor=CENTER, justify=CENTER, foreground="#000000", activeforeground="#000000", background="#ffffff", activebackground="#ffffff", highlightthickness=0, borderwidth=0)
	destination_lbl.place(width=90, height=25, x=0, y=135)

	source_txt = Entry(root, font=("Segoe UI", 9), justify=LEFT, highlightthickness=1, highlightcolor="grey50", highlightbackground="grey50", disabledbackground="grey80", foreground="#000000", background="grey95", borderwidth=0)
	source_txt.place(width=320, height=25, x=90, y=105)

	target_txt = Entry(root, font=("Segoe UI", 9), justify=LEFT, highlightthickness=1, highlightcolor="grey50", highlightbackground="grey50", disabledbackground="grey80", foreground="#000000", background="grey95", borderwidth=0)
	target_txt.place(width=320, height=25, x=90, y=135)

	browse1_btn = Label(root, text="Browse", font=("Segoe UI", 9), anchor=CENTER, justify=CENTER, background="grey95", activeforeground="grey95", highlightthickness=2, highlightcolor="#000000", highlightbackground="#000000", borderwidth=0)
	browse1_btn.place(y=105, width=80, x=415, height=25)
	browse1_btn.bind("<ButtonRelease-1>", lambda event: browse_click(event, source_txt))
	browse1_btn.bind("<Enter>", lambda event: change_thickness(event, browse1_btn, False, 2, 4, started))
	browse1_btn.bind("<Leave>", lambda event: change_thickness(event, browse1_btn, True, 2, 4, started))

	browse2_btn = Label(root, text="Browse", font=("Segoe UI", 9), anchor=CENTER, justify=CENTER, background="grey95", activeforeground="grey95", highlightthickness=2, highlightcolor="#000000", highlightbackground="#000000", borderwidth=0)
	browse2_btn.place(y=135, width=80, x=415, height=25)
	browse2_btn.bind("<ButtonRelease-1>", lambda event: browse_click(event, target_txt))
	browse2_btn.bind("<Enter>", lambda event: change_thickness(event, browse2_btn, False, 2, 4, started))
	browse2_btn.bind("<Leave>", lambda event: change_thickness(event, browse2_btn, True, 2, 4, started))

	exit_btn = Label(root, text="Quit", font=("Segoe UI", 10, "bold"), anchor=CENTER, justify=CENTER, background="grey95", activeforeground="grey95", highlightthickness=2, highlightcolor="red", highlightbackground="red", borderwidth=0)
	exit_btn.place(y=180, width=100, x=40, height=30)
	exit_btn.bind("<ButtonRelease-1>", exit_click)
	exit_btn.bind("<Enter>", lambda event: change_exit_thickness(event, exit_btn, False, 2, 4))
	exit_btn.bind("<Leave>", lambda event: change_exit_thickness(event, exit_btn, True, 2, 4))

	sync_btn = Label(root, text="Mirror", font=("Segoe UI", 10, "bold"), anchor=CENTER, justify=CENTER, background="grey95", activeforeground="grey95", highlightthickness=2, highlightcolor="#000000", highlightbackground="#000000", borderwidth=0)
	sync_btn.place(y=180, width=100, x=360, height=30)
	sync_btn.bind("<ButtonRelease-1>", sync_click)
	sync_btn.bind("<Enter>", lambda event: change_thickness(event, sync_btn, False, 2, 4, started))
	sync_btn.bind("<Leave>", lambda event: change_thickness(event, sync_btn, True, 2, 4, started))

	syncing_lbl = Label(root, text="", font=("Segoe UI", 9, "italic", "bold"), anchor=CENTER, justify=CENTER, foreground="#000000", activeforeground="#000000", background="#ffffff", activebackground="#ffffff", highlightthickness=0, borderwidth=0)
	syncing_lbl.place(height=30, width=100, x=200, y=180)

	root.mainloop()

	exit_click()
