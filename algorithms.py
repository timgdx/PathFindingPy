from queue import Queue, Empty
import time
import threading
from cell import *
from messages import *

SLEEP_TIME = 1/60 # thread sleep time in seconds

STATE_RUNNING = 0
STATE_PAUSED = 1
STATE_STEP = 2

'''class PathFindingAlgorithm:
    def __init__(self,queue,app,grid,speed):
        self.init = False
        self.queue = queue
        self.app = app
        self.grid = grid
        self.setSpeed(speed)
    def run (self,origin,destination,once=False):
        if once:
            self.runAsync(origin,destination,once=False)
        else:
            self.thread = threading.Thread(target=self.runAsync,args=(origin,destination,once),daemon=True)
            self.thread.start()
            #self.thread.join()
    def runAsync(self,origin,destination,once):
        return
    # process queue message
    def __processQueue(self) -> bool:
        try:
            message = self.queue.get(block=False)
            print("Message: ", message)
            if message is None: # stop
                return False
            elif message[0] == 1: # update speed
                self.__setSpeed(message[1])
            elif message[0] == 2: # paused
                self.__setSpeed(message[1])
            return True
        except Empty:
            return True
    def setSpeed(self,speed):
        # convert speed to seconds
        if speed == 0.5:
            self.speed = 1
        elif speed == 1:
            self.speed = 0.5
        elif speed == 1.5:
            self.speed = 0.25
        else:
            self.speed = 0.05
    def getNeighbours(self,cell):
        neighbours = list()
        x = cell.x
        y = cell.y
        # north
        node = self.grid.get(x,y-1)
        if node:
            if node.state == 0 or node.state == 2:
                neighbours.append(node)
        # east
        node = self.grid.get(x+1,y)
        if node:
            if node.state == 0 or node.state == 2:
                neighbours.append(node)
        # south
        node = self.grid.get(x,y+1)
        if node:
            if node.state == 0 or node.state == 2:
                neighbours.append(node)
        # west
        node = self.grid.get(x-1,y)
        if node:
            if node.state == 0 or node.state == 2:
                neighbours.append(node)
        return neighbours

class DepthFirstSearch(PathFindingAlgorithm):
    def __init__(self,queue,app,grid,speed) -> None:
        super().__init__(queue,app,grid,speed)

    def runAsync(self,origin,destination,once):
        # first run initialization
        if not self.init:
            self.init = True
            self.finished = False
            self.origin = origin
            self.destination = destination
            self.nodes = [origin] # nodes in queue to be visited
            self.iterations = 0
        while self.nodes and not self.finished:
            # thread
            if not once:
                # process queue
                if not self.__processQueue(): # exit signal
                    return
            # step
            self.__step()
            if not once:
                time.sleep(self.speed)
            else:
                return
        self.app.onSearchFinished(self.iterations,self.finished)
        return

    def __step(self):
        self.iterations += 1
        node = self.nodes.pop()
        node.visited()
        if node == self.destination:
            self.finished = True
            return
        self.nodes += self.getNeighbours(node)
'''

# extend thread class
class PathFindingAlgorithm(threading.Thread):
    def __init__(self,queue: Queue, app, grid: Grid, speed, stepOnce: bool):
        threading.Thread.__init__(self,daemon=True)
        self.queue = queue
        self.app = app
        self.grid = grid
        self.__setSpeed(speed)
        # search state
        self.origin = self.grid.start
        self.destination = self.grid.end
        self.nodes = [self.origin] # nodes in queue to be visited
        self.iterations = 0
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
                    finished = self.step()
                    if not self.nodes or finished:
                        self.app.onSearchComplete(self.iterations,finished)
                        break
            elif self.state == STATE_STEP: # STEPPING
                finished = self.step()
                if not self.nodes or finished:
                    self.app.onSearchComplete(self.iterations,finished)
                    break
                self.state = STATE_PAUSED
            # sleep
            time.sleep(SLEEP_TIME)
        print("EXIT")
        return

    # process queue message
    def __processQueue(self) -> bool:
        try:
            message = self.queue.get(block=False)
            print("Message: ", message)
            if message is None: # stop
                return False
            elif message[0] == MSG_SPEED: # update speed
                self.__setSpeed(message[1])
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
        #print("STEP - ", self.iterations)

    def __setSpeed(self,speed):
        # convert speed to seconds
        if speed == 0.5:
            self.speed = 1
        elif speed == 1:
            self.speed = 0.5
        elif speed == 1.5:
            self.speed = 0.25
        else:
            self.speed = 0.05

    def getNeighbours(self,cell: Cell):
        neighbours = list()
        x = cell.x
        y = cell.y
        # north
        node = self.grid.get(x,y-1)
        if node:
            if node.state == 0 or node.state == 2:
                neighbours.append(node)
        # east
        node = self.grid.get(x+1,y)
        if node:
            if node.state == 0 or node.state == 2:
                neighbours.append(node)
        # south
        node = self.grid.get(x,y+1)
        if node:
            if node.state == 0 or node.state == 2:
                neighbours.append(node)
        # west
        node = self.grid.get(x-1,y)
        if node:
            if node.state == 0 or node.state == 2:
                neighbours.append(node)
        return neighbours

class DepthFirstSearch(PathFindingAlgorithm):

    def step(self) -> bool:
        #print(DepthFirstSearch.__mro__)
        super().step()
        node = self.nodes.pop()
        node.visited()
        if node == self.destination:
            return True
        # get neigbhours
        neighbours = super().getNeighbours(node)
        # remove older duplicates
        self.nodes = [n for n in self.nodes if n not in neighbours]
        # merge queue
        self.nodes += neighbours
        #self.nodes += super().getNeighbours(node)
        self.app.onStepFinished(self.iterations)
        return False