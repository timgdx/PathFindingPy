import asyncio
from algorithms import DepthFirstSearch
from tkinter import *
import tkinter.ttk as ttk
from cell import *

# RUN - INIT ALGORITHM -> ALG.RUN()
# STEP - INIT ALGORITHM IF NOT RUNNING/STEPPING -> ALG.RUN(ONCE)

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
        self.createStyle()

        # algorithm selection
        self.algorithm = IntVar()
        self.algorithmFunc = None
        self.algorithmInstance = None
        self.algorithmTask = None
        self.algFrame = LabelFrame(self.leftFrame,text="Algorithms",padx=10,pady=10,width=200)
        self.algFrame.pack(anchor=NW,padx=5)
        dfs = ttk.Radiobutton(self.algFrame,text="DepthFirstSearch",variable=self.algorithm, value=1,takefocus=False,style="NStyle.TRadiobutton", command=self.onAlgorithmChanged)
        dfs.pack(fill=X,pady=[0,10])
        dfs.invoke()
        ttk.Radiobutton(self.algFrame,text="BreadthFirstSearch",variable=self.algorithm, value=2,takefocus=False,style="NStyle.TRadiobutton", command=self.onAlgorithmChanged).pack(fill=X,pady=[0,10])
        ttk.Radiobutton(self.algFrame,text="Dijkstra",variable=self.algorithm, value=3,takefocus=False,style="NStyle.TRadiobutton", command=self.onAlgorithmChanged).pack(fill=X,pady=[0,10])
        ttk.Radiobutton(self.algFrame,text="A*",variable=self.algorithm, value=4,takefocus=False,style="NStyle.TRadiobutton", command=self.onAlgorithmChanged).pack(fill=X,pady=[0,0])

        # execution state
        self.state = 0 # 0 - idle, 1 - running, 2 - paused, 3 - step, 4 - finished
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


    def isPaused(self):
        return self.state == 2

    # ttk style
    def createStyle(self):
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

    def setRadioButtonsState(self,val):
        for rb in self.algFrame.winfo_children():
            rb.configure(state = val)

    # event handlers
    def onAlgorithmChanged(self):
        print("Alg: ", self.algorithm.get())
        val = self.algorithm.get()
        if val == 1:
            self.algorithmFunc = DepthFirstSearch
        #self.window.focus() # remove focus from the button; takefocus=False does just that

    def initSearchAlgorithm(self):
        if not self.algorithmInstance:
            self.algorithmInstance = self.algorithmFunc(self,self.grid,self.speed.get())

    # event handlers
    def onRunPauseClicked(self):
        if self.state == 0 or self.state == 4:
            if self.state == 4:
                self.grid.clean()
            # create the algorithm instance and run it
            self.initSearchAlgorithm()
            self.state = 1
            self.runPauseButton.configure(text="Pause")
            self.setRadioButtonsState(DISABLED)
            self.stateLabel.configure(text="State: Running")
            self.algorithmTask = asyncio.run(self.algorithmInstance.runAsync(self.grid.start,self.grid.end))
        elif self.state == 1:
            self.state = 2
            self.runPauseButton.configure(text="Resume")
            self.stateLabel.configure(text="State: Paused")
        elif self.state == 2:
            self.state = 1
            self.runPauseButton.configure(text="Pause")
            self.stateLabel.configure(text="State: Running")
        elif self.state == 3:
            self.state = 1
            self.runPauseButton.configure(text="Pause")
            self.stateLabel.configure(text="State: Running")
        self.window.focus() # remove focus from the button

    def onStopClicked(self):
        self.algorithmTask.cancel()
        self.state = 0
        self.runPauseButton.configure(text="Run")
        self.setRadioButtonsState("enabled")
        self.stateLabel.configure(text="State: Idle")
        self.iterationsLabel.configure(text="Iterations: 0")
        self.grid.clean()
        self.algorithmInstance = None

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

    def onStepFinished(self,iter):
        self.iterationsLabel.configure(text="Iterations: " + str(iter))

    def onSearchFinished(self,iter,finished):
        print("I: ", iter)
        print("Success: " + "yes" if finished else "no")
        self.state = 4
        self.runPauseButton.configure(text="Run")
        self.stateLabel.configure(text="State: Finished")
        self.iterationsLabel.configure(text="Iterations: " + str(iter))
        self.algorithmInstance = None
        self.setRadioButtonsState("enabled")

# create app
app = App()
# run loop
app.window.mainloop()