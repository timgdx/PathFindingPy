# Import Module
from tkinter import *
import time
from threading import *

# Create Object
root = Tk()

# Set geometry
root.geometry("400x400")

# use threading

def threading():
	# Call work function
	t1=Thread(target=work,daemon=True)
	t1.start()

# work function
def work():

	print("sleep time start")

	for i in range(10):
		print(i)
		time.sleep(1)

	print("sleep time stop")

# Create Button
Button(root,text="Click Me",command = threading).pack()

# Execute Tkinter
root.mainloop()
