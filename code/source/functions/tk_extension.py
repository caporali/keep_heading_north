import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

def tk_sleep(time, window):
	"""
	description:
		Sleep for a tkinter window.
	syntax:
		tk_sleep(time, window)
	"""
	window.after(int(time * 1000), window.quit)
	window.mainloop()

def tk_plot(fig, window):
	"""
	description:
		Create a canvas on a tkinter window and display the figure (fig) on it.
	syntax:
		canvas = tk_plot(fig, window)
	"""
	canvas = FigureCanvasTkAgg(fig, master = window)  
	canvas.get_tk_widget().pack()
	canvas.draw()
	return(canvas)

def tk_clear(canvas):
	"""
	description:
		Delete a canvas from a window.
	syntax:
		tk_clear(canvas)
	"""
	canvas.get_tk_widget().pack_forget()
	
def tk_move(window):
	"""
	source:
		https://stackoverflow.com/questions/3352918/how-to-center-a-window-on-the-screen-in-tkinter
	description:
		Move a tkinter window.
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
	window.geometry("{}x{}+{}+{}".format(width, height, x + 751, y + 30))
	window.deiconify()

def tk_window_setup():
	"""
	description:
		Setup of a new tkinter window.
	syntax:
		window = tk_window_setup()
	"""
	window = tk.Tk()
	window.title("")
	window.geometry("800x800")
	window.attributes("-topmost", True)
	window.iconbitmap("..\\source\\functions\images\\tk_icon.ico")
	tk_move(window)
	return window