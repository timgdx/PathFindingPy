from tkinter import *

class Cell:
    def __init__(self,parent,x,y,dummyImage,state = 0,cellSize = 50):
        #btn = ttk.Button(gridFrame,text=x*10+y,image=gridCellImage,style="GStyle.TButton",compound=CENTER)
        #self.button = Button(parent,text=x*10+y,image=dummyImage,width=50,height=50,compound=CENTER,background="#cccccc",relief=SUNKEN)
        self.button = Label(parent,text=x*10+y,image=dummyImage,width=cellSize,height=cellSize,compound=CENTER,background="#cccccc",relief=FLAT)
        self.button.grid(row=x,column=y,padx=1,pady=1)
        self.state = state
        if state != 0:
            self.update()
        #btn.configure(command=onCellClick(gridState[x][y]))
        #self.button.bind("<Button-1>",lambda f: onCellClick(gridState[x][y],True))
        #self.button.bind("<Button-3>",lambda f: onCellClick(gridState[x][y]))

    # blocks or unblocks the cell depending on its current state
    def block(self):
        if self.state == 3:
            self.state = 0
        else:
            self.state = 3
        self.update()

    def clear(self):
        self.state = 0
        self.update()

    # updates the button graphic for the cell's state
    def update(self):
        if (self.state == 0): # none
            self.button.configure(relief=FLAT,background="#cccccc")
        elif (self.state == 1): # start
            self.button.configure(relief=RAISED,background="#778beb")
        elif (self.state == 2): # end
            self.button.configure(relief=RAISED,background="#cf6a87")
        elif (self.state == 3): # blocked
            self.button.configure(relief=FLAT,background="#666666")
        elif (self.state == 4): # path
            self.button.configure(relief=FLAT,background="#f19066")

class Grid:
    def __init__(self,parent,dummyImage,onCellClick,grid=None,cellSize=30,size=(8,8)):
        if grid is None:
            self.dimensions = size
            self.state = {k:dict() for k in range(self.dimensions[1])} # [row][col]: (button,state) - states: 0 - none; 1 - start; 2 - end; 3 - blocked
        x = self.dimensions[0]
        y = self.dimensions[1]
        for row in range(y): # rows
            for col in range(x): # columns
                #btn = ttk.Button(gridFrame,text=x*10+y,image=gridCellImage,style="GStyle.TButton",compound=CENTER)
                #btn = Button(gridFrame,text=x*10+y,image=dummyImage,width=50,height=50,compound=CENTER,background="#cccccc",relief=SUNKEN)
                #btn.grid(row=x,column=y)
                if self.state[row].get(col) == 2:
                    self.state[row][col] = Cell(parent,row,col,dummyImage,1,cellSize)
                    self.start = self.state[row][col]
                elif self.state[row].get(col) == 3:
                    self.state[row][col] = Cell(parent,row,col,dummyImage,2,cellSize)
                    self.end = self.state[row][col]
                else:
                    self.state[row][col] = Cell(parent,row,col,dummyImage,cellSize=cellSize)
                #btn.configure(command=onCellClick(gridState[x][y]))
                self.state[row][col].button.bind("<Button-1>",lambda f,cell=self.state[row][col]: onCellClick(cell,True))
                self.state[row][col].button.bind("<Button-3>",lambda f,cell=self.state[row][col]: onCellClick(cell))
        if grid is None: # set start/end nodes
            self.state[0][0].state = 1
            self.state[0][0].update()
            self.start = self.state[0][0]
            self.state[y-1][x-1].state = 2
            self.state[y-1][x-1].update()
            self.end = self.state[y-1][x-1]

    def replaceStart(self,cell):
        if cell is self.start:
            self.start = self.end
            self.end = cell
            self.start.state = 1
            self.end.state = 2
            self.start.update()
            self.end.update()
        elif cell is self.end:
            self.end = self.start
            self.start = cell
            self.start.state = 1
            self.end.state = 2
            self.start.update()
            self.end.update()
        else:
            self.start.state = 0
            self.start.update()
            self.start = cell
            cell.state = 1
            self.start.update()

    def replaceEnd(self,cell):
        if cell is self.end:
            self.end = self.start
            self.start = cell
            self.start.state = 1
            self.end.state = 2
            self.start.update()
            self.end.update()
        elif cell is self.start:
            self.start = self.end
            self.end = cell
            self.start.state = 1
            self.end.state = 2
            self.end.update()
            self.start.update()
        else:
            self.end.state = 0
            self.end.update()
            self.end = cell
            cell.state = 2
            self.end.update()

    # grid start/end integrity check
    def integrityCheck(self):
        """start = False
        end = False
        for vr in self.state.values():
            for vc in vr.values():
                if vc.state == 1:
                    if start:
                        vc.state = 0
                        vc.update()
                    else:
                        start = True
                elif vc.state == 2:
                    if end:
                        vc.state = 0
                        vc.update()
                    else:
                        end = True"""
        if not self.start:
            if self.state[0][0].state == 2:
                self.state[self.dimensions[0]-1][self.dimensions[1]-1].state = 1
                self.state[self.dimensions[0]-1][self.dimensions[1]-1].update()
            else:
                self.state[0][0].state = 1
                self.state[0][0].update()
        if not self.end:
            if self.state[self.dimensions[0]-1][self.dimensions[1]-1].state == 1:
                self.state[0][0].state = 2
                self.state[0][0].update()
            else:
                self.state[self.dimensions[0]-1][self.dimensions[1]-1].state = 2
                self.state[self.dimensions[0]-1][self.dimensions[1]-1].update()
