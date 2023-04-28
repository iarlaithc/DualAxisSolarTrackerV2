import tkinter as tk
import sys

from SolarTracker import SolarTracker, SolarTrackerGUI

def quit():
	root.destroy()
	sys.exit()

root = tk.Tk()
root.geometry("1100x800")
gui = SolarTrackerGUI(root)
root.protocol("WM_DELETE_WINDOW", quit)
root.mainloop()
