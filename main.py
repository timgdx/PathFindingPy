from algorithms import *
from tkinter import *
import tkinter.ttk as ttk
from grid import *
from queue import Queue
from messages import *
from os import listdir, mkdir, path
import json

CELL_SIZE = 30
GRID_SIZE = (9,9)

STATE_IDLE = 0
STATE_RUNNING = 1
STATE_PAUSED = 2
STATE_STEP = 3
STATE_FINISHED = 4

threadQueue = Queue() # message queue

ALGORITHMS = [DepthFirstSearchStack,BreadthFirstSearch,Dijkstra,A_Star]
SAVED_GRIDS_PATH = path.abspath(path.dirname(__file__)) + "/grids"

class App():
    def __init__(self):
        # create the window
        self.window = Tk()
        self.window.title("PathFindingPy")
        self.window.resizable(False,False)

        # create positional frames
        self.leftFrame = Frame(self.window)
        self.leftFrame.pack(side=LEFT,fill=BOTH)
        self.rightFrame = Frame(self.window)
        self.rightFrame.pack(side=RIGHT,fill=BOTH,padx=5,pady=[0,5])

        # transparent image for cell sizing
        self.dummyImage = PhotoImage(width=1,height=1)

        # create ttk style
        self.createStyle()

        # menu
        self.createMenu()

        # algorithm selection
        self.algorithmThread = None
        self.createAlgorithmsSection()

        # execution state
        self.state = STATE_IDLE # 0 - idle, 1 - running, 2 - paused, 3 - step, 4 - finished
        self.startEndFlip = False # used to determine whether placing a Start or End node (flips on click)
        self.createControlsSection()

        # grid frame
        self.createGridSection()

        # create the grid
        self.grid = Grid(self.gridFrame,self.dummyImage,self.onCellClick,cellSize=CELL_SIZE,size=GRID_SIZE)

        # stats display
        self.createStatsSection()

        # select 1st algorithm
        self.algFrame.winfo_children()[0].invoke()

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

    def createMenu(self):
        self.menu = Menu(self.window)
        self.window.config(menu=self.menu)
        # grid menu
        self.gridMenu = Menu(self.menu,tearoff=0)
        self.gridMenu.add_command(label="Resize..", command=self.resizeGrid)
        # nested load menu
        self.loadMenu = Menu(self.gridMenu,tearoff=0)
        # load saved grids
        self.getAvailableGrids()
        self.gridMenu.add_cascade(label="Load",menu=self.loadMenu)
        # .. grid menu
        self.gridMenu.add_separator()
        self.gridMenu.add_command(label="Save as..", command=self.onSaveAs)
        # add cascade to menu
        self.menu.add_cascade(label="Grid",menu=self.gridMenu)

    def createAlgorithmsSection(self):
        self.algFrame = LabelFrame(self.leftFrame,text="Algorithms",padx=10,pady=10,width=200)
        self.algFrame.pack(anchor=NW,padx=5)
        self.algorithm = IntVar()
        for algN in range(len(ALGORITHMS)):
            ttk.Radiobutton(self.algFrame,text=ALGORITHMS[algN].name or ALGORITHMS[algN].__name__,variable=self.algorithm, value=algN,command=self.__onAlgorithmChanged,takefocus=False,style="NStyle.TRadiobutton").pack(fill=X,pady=[0,5])
        #self.algFrame.winfo_children()[0].invoke()

    def createControlsSection(self):
        self.speed = DoubleVar()
        self.runPauseButton = ttk.Button(self.leftFrame,text="Run",style="NStyle.TButton")
        self.runPauseButton.pack(anchor=NW,padx=[8,10],pady=[10,0],fill=X)
        self.stepButton = ttk.Button(self.leftFrame,text="Step",style="NStyle.TButton")
        self.stepButton.pack(anchor=NW,padx=[8,10],pady=[5,0],fill=X)
        self.stopButton = ttk.Button(self.leftFrame,text="Stop",style="StopButton.TButton")
        self.stopButton.pack(anchor=NW,padx=[8,10],pady=[5,0],fill=X)
        self.speedFrame = LabelFrame(self.leftFrame,text="Speed",padx=22,pady=0)
        self.speedFrame.pack(anchor=NW,padx=5,fill=X)
        self.speedScale = Scale(self.speedFrame,variable=self.speed,orient=HORIZONTAL,resolution=0.5,from_=0.5,to=2,tickinterval=0.5)
        self.speedScale.pack(fill=X,padx=0)
        self.speedScale.set(2)
        self.clearButton = ttk.Button(self.leftFrame,text="Clear",style="StopButton.TButton")
        self.clearButton.pack(anchor=NW,padx=[8,10],pady=[5,5],fill=X)
        self.diagonalValue = BooleanVar()
        self.diagonalSearchCheckbox = Checkbutton(self.leftFrame,text="Diagonal Search",variable=self.diagonalValue)
        self.diagonalSearchCheckbox.pack(anchor=NW,padx=8,pady=[0,5])
        # set handlers
        self.runPauseButton.configure(command=self.onRunPauseClicked)
        self.stepButton.configure(command=self.onStepClicked)
        self.stopButton.configure(command=self.onStopClicked)
        self.clearButton.configure(command=self.onClearClicked)
        self.speedScale.configure(command=self.onSpeedChanged)

    def createGridSection(self):
        self.gridFrame = Frame(self.rightFrame,padx=1,pady=1,background="#666666")
        self.gridFrame.pack(anchor=N,padx=5, pady=5)

    def createStatsSection(self):
        self.stateLabel = Label(self.rightFrame,text="State: Idle")
        self.stateLabel.pack(anchor=NW,padx=2)
        self.iterationsLabel = Label(self.rightFrame,text="Iterations: ")
        self.iterationsLabel.pack(anchor=NW,padx=2)
        self.visitedLabel = Label(self.rightFrame,text="Visited: ") # expanded nodes
        self.visitedLabel.pack(anchor=NW,padx=2)
        self.distanceLabel = Label(self.rightFrame,text="Distance: ")
        self.distanceLabel.pack(anchor=NW,padx=2)
        self.pathLabel = Label(self.rightFrame,text="Path: ",justify=LEFT,wraplength=300)
        self.pathLabel.pack(anchor=NW,padx=2)
        self.notesFrame = LabelFrame(self.rightFrame,text="Note")
        #self.notesFrame.pack(anchor=NW,padx=2)
        self.notesLabel = Label(self.notesFrame,text="")
        self.notesLabel.pack()

    def getAvailableGrids(self):
        # remove current list
        for n in self.loadMenu.winfo_children():
            n.destroy()
        # add default grid
        self.loadMenu.add_radiobutton(label="Default")
        self.loadMenu.invoke(0)
        self.loadMenu.entryconfigure(0,command=self.onSavedGridSelected)
        # create dir if necessary
        if not path.isdir(SAVED_GRIDS_PATH):
            print("Creating grids directory..")
            try:
                mkdir(SAVED_GRIDS_PATH)
            except:
                print("Failed to create grids directory..")
        # load list
        try:
            for file in listdir(SAVED_GRIDS_PATH):
                if file.endswith(".grd"):
                    strippedName = file.rstrip(".grd")
                    self.loadMenu.add_radiobutton(label=strippedName,command=lambda x=strippedName: self.onSavedGridSelected(x))
        except:
            print("Failed to load saved grids..")

    def onSavedGridSelected(self,name = 0):
        # destroy current grid
        for n in self.gridFrame.winfo_children():
            n.destroy()
        grid = self.loadGrid(name) if name != 0 else None
        if grid:
            self.grid = Grid(self.gridFrame,self.dummyImage,self.onCellClick,grid=grid["grid"],cellSize=grid["cellSize"],size=grid["dimensions"])
        else:
            self.grid = Grid(self.gridFrame,self.dummyImage,self.onCellClick,None,CELL_SIZE,GRID_SIZE)

    def resizeGrid(self):
        window = Toplevel(self.window,padx=20,pady=10)
        window.grab_set()
        window.title("Resize..")
        topFrame = Frame(window)
        topFrame.pack(fill=X)
        validate = (window.register(self.__validateGridSize),'%d', '%i', '%P')
        rowsField = Entry(topFrame, font="TkDefaultFont 16",width=3, validate='key', validatecommand=validate)
        rowsField.insert(0,str(self.grid.dimensions[0]))
        rowsField.grid(row=0,column=0,sticky=N+W+E)
        label = Label(topFrame,text="X",justify="center",width=1).grid(row=0,column=1,sticky=N+W+E)
        topFrame.grid_columnconfigure(0,weight=1)
        topFrame.grid_columnconfigure(1,weight=1)
        topFrame.grid_columnconfigure(2,weight=1)
        columnsField = Entry(topFrame, font="TkDefaultFont 16",width=3, validate='key', validatecommand=validate)
        columnsField.grid(row=0,column=2,sticky=N+W+E)
        columnsField.insert(0,str(self.grid.dimensions[1]))
        resizeButton = ttk.Button(window,text="Resize",style="NStyle.TButton",command=lambda : self.onGridResize(window,rowsField,columnsField), width=15)
        resizeButton.pack(anchor=NW,pady=[10,5])

    def __validateGridSize(self,action,index,value):
        if value:
            try:
                x = int(value)
                if x == 0: return False
                return True
            except:
                return False
        return value == ''

    def onGridResize(self,window,rowsField,columnsField):
        try:
            x = min(int(rowsField.get()),16)
            y = min(int(columnsField.get()),16)
            # destroy current grid
            for n in self.gridFrame.winfo_children():
                n.destroy()
            # create default with new size
            self.grid = Grid(self.gridFrame,self.dummyImage,self.onCellClick,None,CELL_SIZE,(x,y))
        except: pass
        window.destroy()
        
    # file -> filename without extension
    def loadGrid(self,file):
        try:
            f = open(SAVED_GRIDS_PATH+"/"+file+".grd","r")
            gridData = f.read()
            grid = json.loads(gridData)
            f.close()
            return grid
        except:
            print("Failed to read file: ", SAVED_GRIDS_PATH+"/"+file)
        return None

    def onSaveAs(self):
        window = Toplevel(self.window,padx=20,pady=10)
        window.grab_set()
        window.title("Save as..")
        field = Entry(window,font="TkDefaultFont 16")
        field.insert(0,"mygrid")
        field.pack()
        saveButton = ttk.Button(window,text="Save",style="NStyle.TButton",command=lambda : self.saveGrid(window,field))
        saveButton.pack(pady=[10,0])

    def saveGrid(self,window,field):
        try:
            filename = field.get() or "mygrid"
            filename = filename.replace(" ", "_")
            filepath = SAVED_GRIDS_PATH+"/"+filename+".grd"
            f = open(filepath,"w")
            f.write(json.dumps({"cellSize": CELL_SIZE, "dimensions": self.grid.dimensions, "grid": self.grid.getSaveDict()}))
            f.close()
            print("Saved grid to:", filename)
        except Exception: print("Failed to save grid..")
        #window.grab_release()
        window.destroy()

    # enables/disables buttons that shouldn't be clickable in runtime
    def setButtonsState(self,val):
        for rb in self.algFrame.winfo_children():
            rb.configure(state = val)
        self.clearButton.configure(state = val)
        if val == "enabled":
            self.menu.entryconfigure(1,state ="normal")
            self.diagonalSearchCheckbox.configure(state = "normal")
        else:
            self.menu.entryconfigure(1,state = val)
            self.diagonalSearchCheckbox.configure(state = val)

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
            self.algorithmThread = ALGORITHMS[self.algorithm.get()](threadQueue,self,self.grid,self.speed.get(),self.diagonalValue.get(),step)

    # event handlers
    def __onAlgorithmChanged(self):
        id = self.algorithm.get()
        if ALGORITHMS[id].info is None:
            self.notesFrame.pack_forget()
        else:
            self.notesFrame.pack(anchor=NW,padx=2)
            self.notesLabel.configure(text=ALGORITHMS[id].info)

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
            self.setButtonsState(DISABLED)
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
        #self.window.focus() # remove focus from the button

    def onStepClicked(self):
        if self.state != STATE_STEP:
            if self.state == STATE_FINISHED:
                self.grid.clean()
            self.state = STATE_STEP
            self.runPauseButton.configure(text="Run")
            self.setButtonsState(DISABLED)
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
        if self.algorithmThread:
            # send message
            threadQueue.put(None)
        self.algorithmThread = None
        self.state = STATE_IDLE
        self.runPauseButton.configure(text="Run")
        self.setButtonsState("enabled")
        self.stateLabel.configure(text="State: Idle")
        self.iterationsLabel.configure(text="Iterations: 0")
        self.visitedLabel.configure(text="Visited: 0")
        self.distanceLabel.configure(text="Distance: 0")
        self.pathLabel.configure(text="Path: ")
        self.grid.clean()

    def onSpeedChanged(self,val):
        if self.algorithmThread:
            # send message
            threadQueue.put((MSG_SPEED,val))

    def onClearClicked(self):
        if self.state != STATE_IDLE and self.state != STATE_FINISHED:
            return
        self.grid.clear()

    def onStep(self,iter,visited):
        self.iterationsLabel.configure(text="Iterations: " + str(iter))
        self.visitedLabel.configure(text="Visited: " + str(visited))

    def onSearchComplete(self,iter,visited,path):
        self.state = STATE_FINISHED
        self.runPauseButton.configure(text="Run")
        self.stateLabel.configure(text="State: Finished")
        self.iterationsLabel.configure(text="Iterations: " + str(iter))
        self.visitedLabel.configure(text="Visited: " + str(visited))
        self.distanceLabel.configure(text="Distance: " + str(len(path)))
        self.pathLabel.configure(text="Path: " + str(path))
        self.algorithmThread = None
        self.setButtonsState("enabled")

# create app
app = App()
# run loop
app.window.mainloop()