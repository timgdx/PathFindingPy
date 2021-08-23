from algorithms import *
from tkinter import *
import tkinter.ttk as ttk
from cell import *
from queue import Queue
from messages import *

CELL_SIZE = 30
GRID_SIZE = (8,8)

STATE_IDLE = 0
STATE_RUNNING = 1
STATE_PAUSED = 2
STATE_STEP = 3
STATE_FINISHED = 4

threadQueue = Queue()

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
        self.algorithmThread = None

        self.algFrame = LabelFrame(self.leftFrame,text="Algorithms",padx=10,pady=10,width=200)
        self.algFrame.pack(anchor=NW,padx=5)
        dfs = ttk.Radiobutton(self.algFrame,text="DepthFirstSearch",variable=self.algorithm, value=1,takefocus=False,style="NStyle.TRadiobutton", command=self.onAlgorithmChanged)
        dfs.pack(fill=X,pady=[0,10])
        dfs.invoke()
        ttk.Radiobutton(self.algFrame,text="BreadthFirstSearch",variable=self.algorithm, value=2,takefocus=False,style="NStyle.TRadiobutton", command=self.onAlgorithmChanged).pack(fill=X,pady=[0,10])
        ttk.Radiobutton(self.algFrame,text="Dijkstra",variable=self.algorithm, value=3,takefocus=False,style="NStyle.TRadiobutton", command=self.onAlgorithmChanged).pack(fill=X,pady=[0,10])
        ttk.Radiobutton(self.algFrame,text="A*",variable=self.algorithm, value=4,takefocus=False,style="NStyle.TRadiobutton", command=self.onAlgorithmChanged).pack(fill=X,pady=[0,0])

        # execution state
        self.state = STATE_IDLE # 0 - idle, 1 - running, 2 - paused, 3 - step, 4 - finished
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
        self.speedScale.set(2)
        self.clearButton = ttk.Button(self.leftFrame,text="Clear",style="StopButton.TButton",width=20)
        self.clearButton.pack(anchor=NW,padx=[8,10],pady=[5,5])

        # set handlers
        self.runPauseButton.configure(command=self.onRunPauseClicked)
        self.stepButton.configure(command=self.onStepClicked)
        self.stopButton.configure(command=self.onStopClicked)
        self.clearButton.configure(command=self.onClearClicked)
        self.speedScale.configure(command=self.onSpeedChanged)

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
        return self.state == STATE_PAUSED

    def isStopped(self):
        return self.state == STATE_IDLE

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
        val = self.algorithm.get()
        if val == 1:
            self.algorithmFunc = DepthFirstSearch
        #self.window.focus() # remove focus from the button; takefocus=False does just that

    # on grid click
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

    # creates a thread for the chosen algorithm
    def initSearchAlgorithm(self,step=False):
        # threadQueue.get() -> to clear queue?
        if not self.algorithmThread: # create thread
            self.algorithmThread = self.algorithmFunc(threadQueue,self,self.grid,self.speed.get(),step)

    # event handlers
    def onRunPauseClicked(self):
        if self.state == STATE_IDLE or self.state == STATE_FINISHED:
            if self.state == STATE_FINISHED:
                self.grid.clean()
            # create the algorithm thread
            self.initSearchAlgorithm()
            # change state
            self.state = STATE_RUNNING
            # update UI
            self.runPauseButton.configure(text="Pause")
            self.setRadioButtonsState(DISABLED)
            self.stateLabel.configure(text="State: Running")
            # run algorithm thread
            self.algorithmThread.start()
        elif self.state == STATE_RUNNING:
            self.state = STATE_PAUSED
            self.runPauseButton.configure(text="Resume")
            self.stateLabel.configure(text="State: Paused")
            # send message
            threadQueue.put((MSG_PAUSE,))
        elif self.state == STATE_PAUSED or self.state == STATE_STEP:
            self.state = STATE_RUNNING
            self.runPauseButton.configure(text="Pause")
            self.stateLabel.configure(text="State: Running")
            # send message
            threadQueue.put((MSG_PAUSE,))
        self.window.focus() # remove focus from the button

    def onStepClicked(self):
        if self.state != STATE_STEP:
            self.state = STATE_STEP
            self.runPauseButton.configure(text="Run")
            self.setRadioButtonsState(DISABLED)
            self.stateLabel.configure(text="State: Step")
        if not self.algorithmThread:
            # create the algorithm thread
            self.initSearchAlgorithm(True)
            # run
            self.algorithmThread.start()
        else: # assume thread is running
            # send message
            threadQueue.put((MSG_STEP,))

    def onStopClicked(self):
        self.state = STATE_IDLE
        self.runPauseButton.configure(text="Run")
        self.setRadioButtonsState("enabled")
        self.stateLabel.configure(text="State: Idle")
        self.iterationsLabel.configure(text="Iterations: 0")
        self.grid.clean()
        self.algorithmThread = None

    def onSpeedChanged(self,val):
        if self.algorithmThread:
            # send message
            threadQueue.put((MSG_SPEED,val))

    def onClearClicked(self):
        if self.state != STATE_IDLE and self.state != STATE_FINISHED:
            return
        self.grid.clear()

    def onStepFinished(self,iter):
        self.iterationsLabel.configure(text="Iterations: " + str(iter))

    def onSearchComplete(self,iter,finished):
        print("Success: " + "yes" if finished else "no")
        self.state = STATE_FINISHED
        self.runPauseButton.configure(text="Run")
        self.stateLabel.configure(text="State: Finished")
        self.iterationsLabel.configure(text="Iterations: " + str(iter))
        self.algorithmThread = None
        self.setRadioButtonsState("enabled")

# create app
app = App()
# run loop
app.window.mainloop()