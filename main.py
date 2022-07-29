from tkinter import *
from tkinter import filedialog
from tkinter import messagebox
import _tkinter
import os
import sys
from dirsync import sync
import filecmp
from multiprocessing import Process


def syncing():
	exit_btn.config(state="disabled")
	sync_btn.config(state="disabled")
	source_txt.config(state="disabled")
	target_txt.config(state="disabled")
	browse1_btn.config(state="disabled")
	browse2_btn.config(state="disabled")

	source_dir = source_txt.get()
	target_dir = target_txt.get()

	if not os.path.exists(source_dir) and not os.path.exists(target_dir):
		source_txt.delete(0, END)
		target_txt.delete(0, END)
		messagebox.showerror("Existence", "The Source and Destination folders don't exist!")
		return
	else:
		if os.path.exists(source_dir):
			pass
		else:
			source_txt.delete(0, END)
			messagebox.showerror("Existence", "The Source folder doesn't exist!")
			return
		if os.path.exists(target_dir):
			pass
		else:
			target_txt.delete(0, END)
			messagebox.showerror("Existence", "The Destination folder doesn't exist!")
			return

	quest = messagebox.askyesno("Files",
	                            "Running this program will delete any aditional files that are in Destination folder and not in Source folder.\nAre you sure you want to proceed?")
	if quest:
		pass
	else:
		return

	working_lbl.place(width=100, height=25, x=200, y=240)

	loop = True
	num = 0
	loop_info = None
	while loop and num <= 3:
		num = num + 1
		sync(source_dir, target_dir, 'sync', purge=True)

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
			if len(dirs_cmp.left_only) > 0 or len(dirs_cmp.right_only) > 0 or \
					len(dirs_cmp.funny_files) > 0:
				return False
			(_, mismatch, errors) = filecmp.cmpfiles(
				dir1, dir2, dirs_cmp.common_files, shallow=False)
			if len(mismatch) > 0 or len(errors) > 0:
				return False
			for common_dir in dirs_cmp.common_dirs:
				new_dir1 = os.path.join(dir1, common_dir)
				new_dir2 = os.path.join(dir2, common_dir)
				if not are_dir_trees_equal(new_dir1, new_dir2):
					return False
			return True

		var = are_dir_trees_equal(source_dir, target_dir)
		if var:
			loop = False
			loop_info = True
		else:
			loop_info = False

	working_lbl.place_forget()

	if loop_info:
		messagebox.showinfo("Completed", "Folders were synchronised successfully!")
	else:
		messagebox.showerror("Failed",
		                     "Synchronising folders failed, check folder and file attributes and try again!")

	exit_btn.config(state="normal")
	sync_btn.config(state="normal")
	source_txt.config(state="normal")
	target_txt.config(state="normal")
	browse1_btn.config(state="normal")
	browse2_btn.config(state="normal")

def sync_click(event):
	global sync_process, started
	if not started:
		started = True

		sync_process = Process(target=syncing)
		sync_process.start()

def exit_click(event=None):
	global sync_process
	try:
		root.destroy()
	except _tkinter.TclError:
		pass
	try:
		sync_process.kill()
		sync_process.join()
		sync_process.close()
	except AttributeError:
		pass
	sys.exit()

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

	exit_btn = Label(root, text="Quit", font=("Segoe UI", 10, "bold"), anchor=CENTER, justify=CENTER, background="grey95", activeforeground="grey95", highlightthickness=2, highlightcolor="#000000", highlightbackground="#000000", borderwidth=0)
	exit_btn.place(y=180, width=100, x=40, height=30)
	exit_btn.bind("<ButtonRelease-1>", exit_click)
	exit_btn.bind("<Enter>", lambda event: change_thickness(event, exit_btn, False, 2, 4, started))
	exit_btn.bind("<Leave>", lambda event: change_thickness(event, exit_btn, True, 2, 4, started))

	sync_btn = Label(root, text="Mirror", font=("Segoe UI", 10, "bold"), anchor=CENTER, justify=CENTER, background="grey95", activeforeground="grey95", highlightthickness=2, highlightcolor="#000000", highlightbackground="#000000", borderwidth=0)
	sync_btn.place(y=180, width=100, x=360, height=30)
	sync_btn.bind("<ButtonRelease-1>", sync_click)
	sync_btn.bind("<Enter>", lambda event: change_thickness(event, sync_btn, False, 2, 4, started))
	sync_btn.bind("<Leave>", lambda event: change_thickness(event, sync_btn, True, 2, 4, started))

	root.mainloop()

	exit_click()
