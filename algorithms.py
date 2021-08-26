from queue import Queue, Empty
import time
import threading
from grid import *
from messages import *
from math import isclose

SLEEP_TIME = 1/60 # thread sleep time in seconds

STATE_RUNNING = 0
STATE_PAUSED = 1
STATE_STEP = 2

# order in which getNeighbours(cell) returns 
#NEIGHBOURS_ORDER = [(0,-1),(0,1),(-1,0),(1,0)] # NORTH, SOUTH, WEST, EAST
NEIGHBOURS_ORDER = [(-1,0),(1,0),(0,-1),(0,1)] # WEST, EAST, NORTH, SOUTH

# extend thread class
class PathFindingAlgorithm(threading.Thread):

    info = None # information about the algorithm (string)

    def __init__(self,queue: Queue, app, grid: Grid, speed, stepOnce: bool):
        threading.Thread.__init__(self,daemon=True)
        self.queue = queue
        self.app = app
        self.grid = grid
        self.__setSpeed(speed)
        # search state
        self.origin = self.grid.start
        self.destination = self.grid.end
        #self.nodes = [self.origin] # nodes in the stack to be visited
        self.iterations = 0
        self.visited = 0
        self.path = dict() # for path search
        #self.origin.discovered()
        # execution state
        self.state = STATE_STEP if stepOnce else STATE_RUNNING

    def run(self):
        self.startTime = time.time()
        self.previousStep = 0
        self.nextStep = 0
        # run loop
        while True:
            #print("THREAD: ", time.time()-self.startTime)
            # process queue
            if not self.__processQueue():
                break
            # check state
            if self.state == STATE_RUNNING: # RUNNING
                # check if it's time to execute step
                if time.time() >= self.nextStep:
                    self.previousStep = time.time()
                    self.nextStep = self.previousStep+self.speed
                    if self.isEmpty() or self.step():
                        #self.dfsCheck(self.getPath())
                        self.app.onSearchComplete(self.iterations,self.visited,self.getPath())
                        break
            elif self.state == STATE_STEP: # STEPPING
                if self.isEmpty() or self.step():
                    self.app.onSearchComplete(self.iterations,self.visited,self.getPath())
                    break
                self.state = STATE_PAUSED
            # sleep
            time.sleep(SLEEP_TIME)
        print("EXIT")
        return

    def isEmpty(self) -> bool:
        return False

    def getPath(self) -> list:
        path = list()
        node = self.path.get(self.destination)
        while(node):
            path.append(node)
            node.path()
            node = self.path.get(node)
        if path:
            path.reverse()
            path.append(self.destination)
            self.destination.path()
        return path

    # process queue message
    def __processQueue(self) -> bool:
        try:
            message = self.queue.get(block=False)
            #print("Message: ", message)
            if message is None: # stop
                return False
            elif message[0] == MSG_SPEED: # update speed
                self.__setSpeed(float(message[1]))
                self.nextStep = self.previousStep+self.speed
            elif message[0] == MSG_PAUSE: # pause/resume
                if self.state == 1: # resume
                    self.nextStep = 0
                    self.previousStep = 0
                    self.state = 0
                else:
                    self.state = 1 # pause
            elif message[0] == MSG_STEP: # step
                self.state = 2
            return True
        except Empty:
            return True

    # returns True if finished
    def step(self) -> bool:
        self.iterations += 1
        self.app.onStep(self.iterations,self.visited)
        #print("STEP - ", self.iterations)

    def __setSpeed(self,speed):
        # convert speed to seconds
        if isclose(speed,0.5):
            self.speed = 0.75
        elif isclose(speed,1):
            self.speed = 0.25
        elif isclose(speed,1.5):
            self.speed = 0.05
        else:
            self.speed = 0.025

    # returns a list of unblocked neighbours
    def getNeighbours(self,cell: Cell):
        neighbours = list()
        x,y = cell.x, cell.y
        for dir in NEIGHBOURS_ORDER:
            node = self.grid.get(x+dir[0],y+dir[1])
            if node:
                if node.state != BLOCKED:
                    neighbours.append(node)
        return neighbours

# STACK DFS
class DepthFirstSearchStack(PathFindingAlgorithm):

    info = '''This is a stack based implementation of DFS (rather than recursive) and, as such,
    more steps have to be performed to respect node discovery order.
    This results in 'ghost' steps, where the popped node has already been visited.'''

    def __init__(self, queue: Queue, app, grid: Grid, speed, stepOnce: bool):
        super().__init__(queue, app, grid, speed, stepOnce)
        self.stack = [self.origin]

    def isEmpty(self) -> bool:
        return not self.stack

    def step(self) -> bool:
        node = self.stack.pop()
        if node.state != VISITED:
            self.visited += 1
        super().step()
        if node.state == VISITED:
            return False
        node.visited()
        if node == self.destination:
            return True
        # get neigbhours
        neighbours = self.getNeighbours(node)
        neighbours.reverse() # for order consistency
        selectedNeighbours = []
        # add path
        for n in neighbours:
            if n.state != VISITED:
                selectedNeighbours.append(n)
                self.path[n] = node
        # push to stack
        self.stack += selectedNeighbours
        return False

    # check recursive result against a path
    # for result integrity check
    def dfsCheck(self,path):
        self.dfsDiscovered = set()
        self.dfsPath = dict()
        self.__dfcCheckRecursive(self.origin)
        # get path
        recPath = list()
        node = self.dfsPath.get(self.destination)
        while(node):
            recPath.append(node)
            node = self.dfsPath.get(node)
        if recPath:
            recPath.reverse()
            recPath.append(self.destination)
        print("PATH: ", recPath)
        print("EQUAL: ", set(path) == set(recPath))
        print("DISTANCE: ", str(len(recPath)), " = ", str(len(path)))

    def __dfcCheckRecursive(self,node):
        self.dfsDiscovered.add(node)
        for n in self.getNeighbours(node):
            if n not in self.dfsDiscovered:
                self.dfsPath[n] = node
                self.__dfcCheckRecursive(n)

# STACK DFS ALT - less efficient version (more 'ghost' steps)
class DepthFirstSearchStackAlt(PathFindingAlgorithm):

    def __init__(self, queue: Queue, app, grid: Grid, speed, stepOnce: bool):
        super().__init__(queue, app, grid, speed, stepOnce)
        self.stack = [self.origin]

    def isEmpty(self) -> bool:
        return not self.stack

    def step(self) -> bool:
        #print(DepthFirstSearch.__mro__)
        node = self.stack.pop()
        if node.state != VISITED:
            self.visited += 1
        super().step()
        if node.state == VISITED:
            return False
        node.visited()
        if node == self.destination:
            return True
        # get neigbhours
        neighbours = self.getNeighbours(node)
        # add path
        for n in neighbours:
            if n.state != VISITED:
                self.path[n] = node
        # push to stack
        self.stack += neighbours
        return False

class BreadthFirstSearch(PathFindingAlgorithm):

    def __init__(self, queue: Queue, app, grid: Grid, speed, stepOnce: bool):
        super().__init__(queue, app, grid, speed, stepOnce)
        self.searchQueue = Queue()
        self.searchQueue.put(self.origin)

    def isEmpty(self) -> bool:
        return self.searchQueue.qsize() == 0

    def step(self) -> bool:
        self.visited += 1
        super().step()
        node = self.searchQueue.get()
        node.visited()
        if node == self.destination:
            return True
        # get neigbhours
        neighbours = self.getNeighbours(node)
        # add to queue and path
        for n in neighbours:
            if n.state != DISCOVERED and n.state != VISITED:
                self.searchQueue.put(n)
                n.discovered()
                self.path[n] = node
        return False