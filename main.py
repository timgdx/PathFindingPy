from tkinter import *
import tkinter.ttk as ttk

# create the main window
window = Tk()
window.title("PathFindingPy")
window.geometry("500x300")

# styles
radioStyle = ttk.Style()
radioStyle.theme_use("default")
radioStyle.configure("NStyle.TRadiobutton",
    indicatorrelief=FLAT,
    indicatormargin=-1,
    indicatordiameter=-1,
    relief=RAISED,
    focusthickness=0, highlightthickness=0, padding=15, background="#aea4de")
radioStyle.map('NStyle.TRadiobutton',
    background=[('selected', '#574b90'), ('active', '#786fa6')])

# event handlers
def onAlgorithmChanged():
    print("Alg: ", algorithm.get())
    window.focus() # to remove focus from the button

# algorithm selection
algorithm = IntVar()
algorithmFunc = None # todo
algFrame = LabelFrame(window,text="Algorithms",padx=10,pady=10,width=200)
algFrame.pack(anchor=NW,padx=5)
ttk.Radiobutton(algFrame,text="DepthFirstSearch",variable=algorithm, value=1,style="NStyle.TRadiobutton", command=onAlgorithmChanged).pack(fill=X,pady=[0,10])
ttk.Radiobutton(algFrame,text="BreadthFirstSearch",variable=algorithm, value=2, style="NStyle.TRadiobutton", command=onAlgorithmChanged).pack(fill=X,pady=[0,10])
ttk.Radiobutton(algFrame,text="Dijkstra",variable=algorithm, value=3, style="NStyle.TRadiobutton", command=onAlgorithmChanged).pack(fill=X,pady=[0,10])
ttk.Radiobutton(algFrame,text="A*",variable=algorithm, value=4, style="NStyle.TRadiobutton", command=onAlgorithmChanged).pack(fill=X,pady=[0,0])

# run loop
window.mainloop()