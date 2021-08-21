from tkinter import *
import tkinter.ttk as ttk
from cell import *

# create the main window
window = Tk()
window.title("PathFindingPy")
#window.geometry("500x300")

# create positional frames
leftFrame = Frame(window)
leftFrame.pack(side=LEFT,fill=BOTH)
rightFrame = Frame(window)
rightFrame.pack(side=RIGHT,fill=BOTH)

# transparent image for cell sizing
cellSize = 40
dummyImage = PhotoImage(width=1,height=1)

# styles
nStyle = ttk.Style()
nStyle.theme_use("clam")
nStyle.configure("NStyle.TRadiobutton",
    indicatorrelief=FLAT,
    indicatormargin=-10, # -1 for default
    indicatordiameter=-1,
    relief=RAISED,
    focusthickness=0, highlightthickness=0, padding=15, background="#aea4de")
nStyle.map('NStyle.TRadiobutton',
    background=[('selected', '#574b90'), ('active', '#786fa6')])
nStyle.configure("NStyle.TButton",
    padding=10, background="#aea4de")
nStyle.map('NStyle.TButton',
    background=[('selected', '#574b90'), ('active', '#786fa6')])
nStyle.configure("StopButton.TButton",
    padding=10, background="#e66767")
nStyle.map('StopButton.TButton',
    background=[('selected', '#ea8685'), ('active', '#ea8685')])
nStyle.configure("Horizontal.NStyle.TScale")

# event handlers
def onAlgorithmChanged():
    print("Alg: ", algorithm.get())
    window.focus() # remove focus from the button

# algorithm selection
algorithm = IntVar()
algorithmFunc = None # todo
algFrame = LabelFrame(leftFrame,text="Algorithms",padx=10,pady=10,width=200)
algFrame.pack(anchor=NW,padx=5)
ttk.Radiobutton(algFrame,text="DepthFirstSearch",variable=algorithm, value=1,style="NStyle.TRadiobutton", command=onAlgorithmChanged).pack(fill=X,pady=[0,10])
ttk.Radiobutton(algFrame,text="BreadthFirstSearch",variable=algorithm, value=2, style="NStyle.TRadiobutton", command=onAlgorithmChanged).pack(fill=X,pady=[0,10])
ttk.Radiobutton(algFrame,text="Dijkstra",variable=algorithm, value=3, style="NStyle.TRadiobutton", command=onAlgorithmChanged).pack(fill=X,pady=[0,10])
ttk.Radiobutton(algFrame,text="A*",variable=algorithm, value=4, style="NStyle.TRadiobutton", command=onAlgorithmChanged).pack(fill=X,pady=[0,0])

# execution state
state = 0 # 0 - idle, 1 - running, 2 - stopped, 3 - step, 4 - finished
startEndFlip = False # used to determine whether placing a Start or End node (flips on click)
speed = DoubleVar()

runPauseButton = ttk.Button(leftFrame,text="Run",style="NStyle.TButton",width=20)
runPauseButton.pack(anchor=NW,padx=[8,10],pady=[10,0])
stepButton = ttk.Button(leftFrame,text="Step",style="NStyle.TButton",width=20)
stepButton.pack(anchor=NW,padx=[8,10],pady=[5,0])
stopButton = ttk.Button(leftFrame,text="Stop",style="StopButton.TButton",width=20)
stopButton.pack(anchor=NW,padx=[8,10],pady=[5,0])
speedFrame = LabelFrame(leftFrame,text="Speed",padx=22,pady=0)
speedFrame.pack(anchor=NW,padx=5)
speedScale = Scale(speedFrame,variable=speed,orient=HORIZONTAL,resolution=0.5,from_=0.5,to=2,tickinterval=0.5)
#speedScale = ttk.Scale(speedFrame,variable=speed,orient=HORIZONTAL,from_=0.5,to=2,style="Horizontal.NStyle.TScale")
speedScale.pack(fill=X,padx=0)
speedScale.set(1)
clearButton = ttk.Button(leftFrame,text="Clear",style="StopButton.TButton",width=20)
clearButton.pack(anchor=NW,padx=[8,10],pady=[5,5])

# event handlers
def onRunStopClicked():
    global state
    if state == 0:
        state = 1
        runPauseButton.configure(text="Pause")
    elif state == 1:
        state = 2
        runPauseButton.configure(text="Resume")
    elif state == 2:
        state = 1
        runPauseButton.configure(text="Pause")
    elif state == 3:
        state = 1
        runPauseButton.configure(text="Pause")
    window.focus() # remove focus from the button

# set handlers
runPauseButton.configure(command=onRunStopClicked)

# grid - this consists of a NxN button grid
gridSize = (8,8) # width,height
#gridState = {k:dict() for k in range(gridSize[1])} # [row][col]: (button,state) - states: 0 - none; 1 - start; 2 - end; 3 - blocked
gridFrame = Frame(rightFrame,padx=1,pady=1,background="#666666")
gridFrame.pack(anchor=NE,padx=5, pady=5)

# stats display
stateLabel = Label(rightFrame,text="State: idle")
stateLabel.pack(anchor=NW,padx=5)
iterationsLabel = Label(rightFrame,text="Iterations: ")
iterationsLabel.pack(anchor=NW,padx=5)

# click handler
def onCellClick(cell,left=False):
    if state != 0:
        return
    if left: # block/unblock
        cell.block() # calls update
    else: # start/end
        global startEndFlip
        startEndFlip = not startEndFlip
        if startEndFlip:
            grid.replaceStart(cell)
        else:
            grid.replaceEnd(cell)
    # check start/end integrity
    #grid.integrityCheck()

# generate grid
'''for x in range(gridSize[1]): # rows
    for y in range(gridSize[0]): # columns
        #btn = ttk.Button(gridFrame,text=x*10+y,image=gridCellImage,style="GStyle.TButton",compound=CENTER)
        #btn = Button(gridFrame,text=x*10+y,image=dummyImage,width=50,height=50,compound=CENTER,background="#cccccc",relief=SUNKEN)
        #btn.grid(row=x,column=y)
        gridState[x][y] = Cell(gridFrame,x,y,dummyImage,30)#(btn,0)
        #btn.configure(command=onCellClick(gridState[x][y]))
        gridState[x][y].button.bind("<Button-1>",lambda f,cell=gridState[x][y]: onCellClick(cell,True))
        gridState[x][y].button.bind("<Button-3>",lambda f,cell=gridState[x][y]: onCellClick(cell))'''

grid = Grid(gridFrame,dummyImage,onCellClick,cellSize=cellSize,x=gridSize[0],y=gridSize[1])

# run loop
window.mainloop()