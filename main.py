from tkinter import *
from tkinter import Menu
from tkinter import filedialog
from tkinter import messagebox
import os
import os.path
import sys
from dirsync import sync
import filecmp
import threading


# start of main code - behind clicks

def exit_click():
	root.destroy()

# start main window clicks
def sync_click_starter():
	def sync_click():
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



	sync_thread = threading.Thread(target=sync_click)
	sync_thread.start()


def browse1_click():
	dir1 = filedialog.askdirectory()
	source_txt.delete(0, END)
	source_txt.insert(0, dir1)
def browse2_click():
	dir2 = filedialog.askdirectory()
	target_txt.delete(0, END)
	target_txt.insert(0, dir2)
# end of main window clicks

# end of main code - behind clicks

# start of icon location finder
def resource_path(relative_path):
	""" Get absolute path to resource, works for dev and for PyInstaller """
	try:
		# PyInstaller creates a temp folder and stores path in _MEIPASS
		base_path = sys._MEIPASS
	except Exception:
		base_path = os.path.abspath(".")
	return os.path.join(base_path, relative_path)
# end of icon location finder


# start of GUI
root = Tk()
root.title("DirSync")
root.geometry(f"500x300+{root.winfo_screenwidth() // 2 - 250}+{root.winfo_screenheight() // 2 - 150}")
root.resizable(False, False)
icon_path = resource_path("Dir Sync - icon.ico")
root.iconbitmap(icon_path)

# start of main window content
exit_btn = Button(root, text="Exit", font=("Segoe UI", 9), command=exit_click)
exit_btn.place(height=25, width=100, x=30, y=240)
sync_btn = Button(root, text="Synchronise", font=("Segoe UI Bold", 9), command=sync_click_starter,)
sync_btn.place(height=25, width=100, x=370, y=240)
name_lbl = Label(root, text="Dir Sync", font=("Times New Roman Bold", 35))
name_lbl.place(width=175, height=60, x=162.5, y=10)
description_lbl = Label(root, text="This program synchronises two folders", font=("Segoe UI", 9))
description_lbl.place(height=15, x=125, y=80)
description2_lbl = Label(root, text="Source >>> Destination", font=("Segoe UI", 9))
description2_lbl.place(height=15, x=125, y=100)
source_lbl = Label(root, text="Source: ", font=("Segoe UI", 9))
source_lbl.place(width=42.5, x=25, y=149)
destination_lbl = Label(root, text="Destination: ", font=("Segoe UI", 9))
destination_lbl.place(width=62.5, x=15, y=179)
working_lbl = Label(root, text="Syncing...", font=("Segoe UI", 9))
working_lbl.place_forget()
source_txt = Entry(root, font=("Segoe UI", 9))
source_txt.place(width=300, x=90, y=150)
target_txt = Entry(root, font=("Segoe UI", 9))
target_txt.place(width=300, x=90, y=180)
browse1_btn = Button(root, text="Browse", font=("Segoe UI", 9), command=browse1_click)
browse1_btn.place(y=148, width=80, x=405, height=22)
browse2_btn = Button(root, text="Browse", font=("Segoe UI", 9), command=browse2_click)
browse2_btn.place(y=178, width=80, x=405, height=22)
# end of main window content

root.mainloop()
# end of GUI

sys.exit()
