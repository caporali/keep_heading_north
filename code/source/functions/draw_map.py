import tkinter as tk
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)

def tk_plot(fig, window):
	canvas = FigureCanvasTkAgg(fig, master = window)  
	canvas.get_tk_widget().pack()
	canvas.draw()
	return(canvas)

def tk_sleep(time, window):
    """
	description:
		Sleep for tkinter.
	syntax:
		tk_sleep(time, window)
    """
    window.after(int(time * 1000), window.quit)
    window.mainloop()
	
# https://stackoverflow.com/questions/3352918/how-to-center-a-window-on-the-screen-in-tkinter
def tk_move(window):
	"""
	description:
		Centering of a tkinter window.
	syntax:
		tk_center(window)
    """
	window.update_idletasks()
	width = window.winfo_width()
	frm_width = window.winfo_rootx() - window.winfo_x()
	window_width = width + 2 * frm_width
	height = window.winfo_height()
	titlebar_height = window.winfo_rooty() - window.winfo_y()
	window_height = height + titlebar_height + frm_width
	x = window.winfo_screenwidth() // 2 - window_width // 2
	y = window.winfo_screenheight() // 2 - window_height // 2
	window.geometry("{}x{}+{}+{}".format(width, height, x + 751, y + 28))
	window.deiconify()

def tk_windows_setup():
	window = tk.Tk()
	window.title("")
	window.geometry("800x800")
	window.attributes("-topmost", True)
	window.iconbitmap("..\\images\\tk_icon.ico")
	tk_move(window)
	return window