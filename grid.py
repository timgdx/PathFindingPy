from tkinter import *

EMPTY = 0
START = 1
END = 2
BLOCKED = 3
DISCOVERED = 4
VISITED = 5
PATH = 6

class Cell:
    def __init__(self,id,parent,x,y,dummyImage,state = EMPTY,cellSize = 50):
        self.label = Label(parent,text=id,image=dummyImage,width=cellSize,height=cellSize,compound=CENTER,background="#cccccc",relief=FLAT)
        self.label.grid(row=x,column=y,padx=1,pady=1)
        self.state = state
        self.rawState = 0
        self.x = x
        self.y = y
        self.id = id
        if state != EMPTY:
            if state == START: self.label.configure(text="A")
            elif state == END: self.label.configure(text="B")
            self.update()

    def __str__(self) -> str:
        return str(self.label.cget("text")) 

    def __repr__(self) -> str:
        return str(self.label.cget("text")) #str(self.id)

    # blocks or unblocks the cell depending on its current state
    # doesn't do anything if START/END
    def block(self):
        if self.state == START or self.state == END:
            return
        if self.state == BLOCKED:
            self.state = EMPTY
        else:
            self.state = BLOCKED
        self.update()

    def discovered(self):
        self.state = DISCOVERED
        self.update()

    def visited(self):
        self.state = VISITED
        self.update()

    def path(self):
        self.state = PATH
        self.update()

    def saveState(self):
        self.rawState = self.state

    # cleans algorithm search data
    def clean(self):
        if self.state == DISCOVERED or self.state == VISITED or self.state == PATH:
            self.state = self.rawState
            self.rawState = EMPTY # not necessary
            self.update()

    def clear(self):
        if self.state == START or self.state == END:
            return
        if (self.state == DISCOVERED or self.state == VISITED or self.state == PATH) and (self.rawState == START or self.rawState == END):
            self.state = self.rawState
        else:
            self.state = EMPTY
        self.update()

    # updates the label graphic for the cell's state
    def update(self):
        if (self.state == EMPTY): # none
            self.label.configure(relief=FLAT,background="#cccccc")
        elif (self.state == START): # start
            self.label.configure(relief=RAISED,background="#778beb")
        elif (self.state == END): # end
            self.label.configure(relief=RAISED,background="#cf6a87")
        elif (self.state == BLOCKED): # blocked
            self.label.configure(relief=FLAT,background="#666666")
        elif (self.state == DISCOVERED): # discovered
            self.label.configure(relief=FLAT if (self.rawState != START and self.rawState != END) else RAISED,background="#f7d794")
        elif (self.state == VISITED): # visited
            self.label.configure(relief=FLAT if (self.rawState != START and self.rawState != END) else RAISED,background="#f3a683")
        elif (self.state == PATH): # path
            self.label.configure(relief=FLAT if (self.rawState != START and self.rawState != END) else RAISED,background="#e15f41")

    def getSaveState(self):
        if self.state == EMPTY or self.state == START or self.state == END or self.state == BLOCKED:
            return self.state
        elif self.rawState == EMPTY or self.rawState == START or self.rawState == END or self.rawState == BLOCKED:
            return self.rawState
        else:
            return EMPTY

class Grid:
    def __init__(self,parent,dummyImage,onCellClick,grid=None,cellSize=30,size=(8,8)):
        x,y = size
        self.dimensions = size
        self.state = {k:dict() for k in range(y)}
        if grid is None:
            grid = {str(k):dict() for k in range(y)} # [row][col]: cell.state
            grid['0']['0'] = START
            grid[str(y-1)][str(x-1)] = END
        for row in range(y): # rows
            for col in range(x): # columns
                id = row*x+col
                state = grid[str(row)].get(str(col)) or EMPTY # row and col need to be converted to str because of the JSON parser
                if state == START:
                    self.state[row][col] = Cell(id,parent,row,col,dummyImage,START,cellSize)
                    self.start = self.state[row][col]
                elif state == END:
                    self.state[row][col] = Cell(id,parent,row,col,dummyImage,END,cellSize)
                    self.end = self.state[row][col]
                else:
                    self.state[row][col] = Cell(id,parent,row,col,dummyImage,state,cellSize=cellSize)
                self.state[row][col].label.bind("<Button-1>",lambda f,cell=self.state[row][col]: onCellClick(cell,True))
                self.state[row][col].label.bind("<Button-3>",lambda f,cell=self.state[row][col]: onCellClick(cell))

    def get(self,x,y):
        return self.state[x][y] if self.state.get(x) and self.state[x].get(y) else None

    def clean(self):
        for v in self.state.values():
            for vv in v.values():
                vv.clean()

    def clear(self):
        for v in self.state.values():
            for vv in v.values():
                vv.clear() 

    def replaceStart(self,cell):
        if cell is self.end or cell is self.start:
            self.reverseStart()
        else:
            self.start.state = EMPTY
            self.start.label.configure(text=str(self.start.id))
            self.start.update()
            self.start = cell
            self.start.label.configure(text="A")
            cell.state = START
            self.start.update()

    def replaceEnd(self,cell):
        if cell is self.end or cell is self.start:
            self.reverseStart()
        else:
            self.end.state = EMPTY
            self.end.label.configure(text=str(self.end.id))
            self.end.update()
            self.end = cell
            self.end.label.configure(text="B")
            cell.state = END
            self.end.update()

    def reverseStart(self):
        end = self.end
        self.end = self.start
        self.start = end
        self.start.state = START
        self.end.state = END
        self.start.update()
        self.end.update()
        self.start.label.configure(text="A")
        self.end.label.configure(text="B")

    # used before running an algorithm
    # saves cells' state
    def saveState(self):
        for v in self.state.values():
            for vv in v.values():
                vv.saveState() 

    # grid start/end integrity check
    def integrityCheck(self):
        if not self.start:
            if self.state[0][0].state == END:
                self.state[self.dimensions[0]-1][self.dimensions[1]-1].state = START
                self.state[self.dimensions[0]-1][self.dimensions[1]-1].update()
            else:
                self.state[0][0].state = START
                self.state[0][0].update()
        if not self.end:
            if self.state[self.dimensions[0]-1][self.dimensions[1]-1].state == START:
                self.state[0][0].state = END
                self.state[0][0].update()
            else:
                self.state[self.dimensions[0]-1][self.dimensions[1]-1].state = END
                self.state[self.dimensions[0]-1][self.dimensions[1]-1].update()

    def getSaveDict(self):
        save = {k:dict() for k in range(self.dimensions[1])}
        for row in save.keys():
            for column in self.state[row].keys():
                save[row][column] = self.state[row][column].getSaveState()
        return save