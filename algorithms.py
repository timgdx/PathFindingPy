import asyncio

class PathFindingAlgorithm:
    def __init__(self,app,grid,speed):
        self.init = False
        self.app = app
        self.grid = grid
        self.setSpeed(speed)
    async def runAsync(self,origin,destination,once=False):
        pass
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
    def __init__(self,app,grid,speed) -> None:
        super().__init__(app,grid,speed)
    async def runAsync(self,origin,destination,once=False):
        # first run initialization
        if not self.init:
            self.init = True
            self.finished = False
            self.origin = origin
            self.destination = destination
            self.nodes = [origin] # nodes in queue to be visited
            self.iterations = 0
        while self.nodes and not self.finished:
            self.__step()
            if not once:
                if self.app.isPaused():
                    return
                await asyncio.sleep(self.speed)
            else:
                return
        self.app.onSearchFinished(self.iterations,self.finished)

    def __step(self):
        self.iterations += 1
        node = self.nodes.pop()
        node.visited()
        if node == self.destination:
            self.finished = True
            return
        self.nodes += self.getNeighbours(node)
        print("step")

