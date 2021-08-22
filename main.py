from tkinter import *
import tkinter.ttk as ttk
from cell import *

CELL_SIZE = 30
GRID_SIZE = (8,8)

class App():
    def __init__(self):
        # create the window
        self.window = Tk()
        self.window.title("PathFindingPy")

        # create positional frames
        self.leftFrame = Frame(self.window)
        self.leftFrame.pack(side=LEFT,fill=BOTH)
        self.rightFrame = Frame(self.window)
        self.rightFrame.pack(side=RIGHT,fill=BOTH)

        # transparent image for cell sizing
        self.dummyImage = PhotoImage(width=1,height=1)

        # custom ttk style
        self.nStyle = ttk.Style()
        self.nStyle.theme_use("clam")
        self.nStyle.configure("NStyle.TRadiobutton",
            indicatorrelief=FLAT,
            indicatormargin=-10, # -1 for default
            indicatordiameter=-1,
            relief=RAISED,
            focusthickness=0, highlightthickness=0, padding=15, background="#aea4de")
        self.nStyle.map('NStyle.TRadiobutton',
            background=[('selected', '#574b90'), ('active', '#786fa6')])
        self.nStyle.configure("NStyle.TButton",
            padding=10, background="#aea4de")
        self.nStyle.map('NStyle.TButton',
            background=[('selected', '#574b90'), ('active', '#786fa6')])
        self.nStyle.configure("StopButton.TButton",
            padding=10, background="#e66767")
        self.nStyle.map('StopButton.TButton',
            background=[('selected', '#ea8685'), ('active', '#ea8685')])
        self.nStyle.configure("Horizontal.NStyle.TScale")

        # algorithm selection
        self.algorithm = IntVar()
        self.algorithmFunc = None # todo
        self.algFrame = LabelFrame(self.leftFrame,text="Algorithms",padx=10,pady=10,width=200)
        self.algFrame.pack(anchor=NW,padx=5)
        ttk.Radiobutton(self.algFrame,text="DepthFirstSearch",variable=self.algorithm, value=1,style="NStyle.TRadiobutton", command=self.onAlgorithmChanged).pack(fill=X,pady=[0,10])
        ttk.Radiobutton(self.algFrame,text="BreadthFirstSearch",variable=self.algorithm, value=2, style="NStyle.TRadiobutton", command=self.onAlgorithmChanged).pack(fill=X,pady=[0,10])
        ttk.Radiobutton(self.algFrame,text="Dijkstra",variable=self.algorithm, value=3, style="NStyle.TRadiobutton", command=self.onAlgorithmChanged).pack(fill=X,pady=[0,10])
        ttk.Radiobutton(self.algFrame,text="A*",variable=self.algorithm, value=4, style="NStyle.TRadiobutton", command=self.onAlgorithmChanged).pack(fill=X,pady=[0,0])

        # execution state
        self.state = 0 # 0 - idle, 1 - running, 2 - stopped, 3 - step, 4 - finished
        self.startEndFlip = False # used to determine whether placing a Start or End node (flips on click)
        self.speed = DoubleVar()

        self.runPauseButton = ttk.Button(self.leftFrame,text="Run",style="NStyle.TButton",width=20)
        self.runPauseButton.pack(anchor=NW,padx=[8,10],pady=[10,0])
        self.stepButton = ttk.Button(self.leftFrame,text="Step",style="NStyle.TButton",width=20)
        self.stepButton.pack(anchor=NW,padx=[8,10],pady=[5,0])
        self.stopButton = ttk.Button(self.leftFrame,text="Stop",style="StopButton.TButton",width=20)
        self.stopButton.pack(anchor=NW,padx=[8,10],pady=[5,0])
        self.speedFrame = LabelFrame(self.leftFrame,text="Speed",padx=22,pady=0)
        self.speedFrame.pack(anchor=NW,padx=5)
        self.speedScale = Scale(self.speedFrame,variable=self.speed,orient=HORIZONTAL,resolution=0.5,from_=0.5,to=2,tickinterval=0.5)
        self.speedScale.pack(fill=X,padx=0)
        self.speedScale.set(1)
        self.clearButton = ttk.Button(self.leftFrame,text="Clear",style="StopButton.TButton",width=20)
        self.clearButton.pack(anchor=NW,padx=[8,10],pady=[5,5])

        # set handlers
        self.runPauseButton.configure(command=self.onRunPauseClicked)
        self.stopButton.configure(command=self.onStopClicked)

        # grid frame
        self.gridFrame = Frame(self.rightFrame,padx=1,pady=1,background="#666666")
        self.gridFrame.pack(anchor=NE,padx=5, pady=5)

        # stats display
        self.stateLabel = Label(self.rightFrame,text="State: idle")
        self.stateLabel.pack(anchor=NW,padx=5)
        self.iterationsLabel = Label(self.rightFrame,text="Iterations: ")
        self.iterationsLabel.pack(anchor=NW,padx=5)

        # create the grid
        self.grid = Grid(self.gridFrame,self.dummyImage,self.onCellClick,cellSize=CELL_SIZE,size=GRID_SIZE)

    # event handlers
    def onAlgorithmChanged(self):
        print("Alg: ", self.algorithm.get())
        self.window.focus() # remove focus from the button

    # event handlers
    def onRunPauseClicked(self):
        if self.state == 0:
            # create the algorithm instance and run it
            self.state = 1
            self.runPauseButton.configure(text="Pause")
        elif self.state == 1:
            self.state = 2
            self.runPauseButton.configure(text="Resume")
        elif self.state == 2:
            self.state = 1
            self.runPauseButton.configure(text="Pause")
        elif self.state == 3:
            self.state = 1
            self.runPauseButton.configure(text="Pause")
        self.window.focus() # remove focus from the button

    def onStopClicked(self):
        self.state = 0
        self.runPauseButton.configure(text="Run")

    # click handler
    def onCellClick(self,cell,left=False):
        if self.state != 0:
            return
        if left: # block/unblock
            cell.block() # calls update
        else: # start/end
            self.startEndFlip = not self.startEndFlip
            if self.startEndFlip:
                self.grid.replaceStart(cell)
            else:
                self.grid.replaceEnd(cell)
        # check start/end integrity
        self.grid.integrityCheck()

# create app
app = App()
# run loop
app.window.mainloop()