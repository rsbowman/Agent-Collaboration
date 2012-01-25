from math import sqrt
from random import choice
from operator import add
import sys

def dist(p1, p2):
    """ manhattan distance """
    return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])

def log(s):
    pass

class Robot:
    sightRadius = 3
    def __init__(self, name, position=(0, 0)):
        self.name = name
        self.neighbors = []
        self.world = None
        self.position = position
        self.brain = RobotBrain()
        self.state = WanderingState()
        self.points = 0 # robot gets a point if it pushes box into hole
        
    def addNeighbor(self, neighbor):
        self.neighbors.append(neighbor)

    def getPeers(self):
        return self.neighbors

    def getPoints(self):
        return self.points
    
    def setWorld(self, world):
        self.world = world

    def lookAround(self):
        boxes, noboxes = self.world.getBoxesNear(self.position,
                                                 self.sightRadius)
        holes = self.world.getHolesNear(self.position, self.sightRadius)
        self.brain.updateHoles(holes)
        self.brain.updateBoxes(boxes, noboxes)
        self.exchangeInfo()

    def exchangeInfo(self):
        for neighbor in self.neighbors:
            neighbor.updateBrain(self.brain)

    def updateBrain(self, otherBrain):
        self.brain.updateAssignments(otherBrain)

    def wander(self):
        size = self.world.size
        x, y = self.position
        dx, dy = choice([(0, 1), (1, 0), (0, -1), (-1, 0)])
        newx, newy = x + dx, y + dy
        while not (0 <= newx < size and 0 <= newy < size):
            dx, dy = choice([(0, 1), (1, 0), (0, -1), (-1, 0)])
            newx, newy = x + dx, y + dy
        self.moveTo(newx, newy)

    def moveTo(self, x, y):
        size = self.world.size
        if 0 <= x < size and 0 <= y < size:
            self.position = (x, y)
        else:
            assert False, '%s tried to move to (%d, %d)' %(self.name, x, y)
            
    def act(self):
        self.brain.updateCachedChanges()
        self.state.act(self)
        
    def printBeliefs(self, stream=sys.stdout):
        boxes = self.brain.boxes
        holes = self.brain.holes
        stream.write('robot %s\nboxes\n' %(self.name,))
        for box, agent in boxes.items():
            stream.write('\t%s assigned to %s\n' %(
                box, agent is None and 'nobody' or agent.name))
        stream.write('holes\n')
        for hole, agent in holes.items():
            stream.write('\t%s assigned to %s\n' %(
                hole, agent is None and 'nobody' or agent.name))
        stream.flush()

class MovingToBoxState:
    def __init__(self, box):
        self.destination = box

    def act(self, robot):
        x, y = robot.position
        xdest, ydest = self.destination
        if abs(x - xdest) == 0 and abs(y - ydest) == 0:
            if robot.world.isBoxAt(x, y):
                log('%s in MovingBoxState' %(robot.name,))
                robot.state = MovingBoxState()
            else:
                log('%s in WanderingState' %(robot.name,))
                robot.state = WanderingState()
        elif abs(x - xdest) == 0:
            dy = y > ydest and -1 or 1
            robot.moveTo(x, y + dy)
        else:
            dx = x > xdest and -1 or 1
            robot.moveTo(x + dx, y)

class MovingBoxState:
    def __init__(self):
        self.hole = None

    def act(self, robot):
        if not robot.world.isBoxAt(robot.position):
            log('%s in WanderingState' %(robot.name,))
            robot.state = WanderingState()
            return
        if self.hole is None: # find closest unassigned hole
            holes = [ (hole, dist(robot.position, hole))
                      for hole in robot.brain.getUnassignedHoles() ]
            if not holes:
                oldbox = robot.position
                robot.wander()
                robot.points += robot.world.moveBox(oldbox, robot.position)
                return
            holes.sort(lambda x, y: cmp(x[1], y[1]))
            myHole = holes[0][0]
            self.hole = myHole
            robot.brain.assignHole(myHole, robot)
            robot.exchangeInfo()
        else: # move box towards hole
            x, y = robot.position
            xdest, ydest = self.hole
            if abs(x - xdest) == 0 and abs(y - ydest) == 0:
                log('%s in WanderingState' %(robot.name,))
                robot.state = WanderingState()
                return
            elif abs(x - xdest) == 0:
                dy = y > ydest and -1 or 1
                dx = 0
            else:
                dy = 0
                dx = x > xdest and -1 or 1
            robot.moveTo(x + dx, y + dy)
            robot.points += robot.world.moveBox((x, y), robot.position)

    
class WanderingState:
    def act(self, robot):
        # select closest unassigned box
        boxes = [ (box, dist(robot.position, box))
                  for box in robot.brain.getUnassignedBoxes() ]
        if not boxes:
            robot.wander()
            return
        boxes.sort(lambda x, y: cmp(x[1], y[1]))
        myBox, distance = boxes[0][0], boxes[0][1]
        robot.brain.assignBox(myBox, robot)
        if distance == 0:
            log('%s in MovingBoxState' %(robot.name,))
            robot.state = MovingBoxState()
        else:
            log('%s in MovingToBoxState' %(robot.name,))
            robot.state = MovingToBoxState(myBox)
        robot.exchangeInfo()
            
            

            
    
class RobotBrain:
    def __init__(self):
        self.boxes = {} # map boxes -> assigned robots
        self.holes = {}
        self.newHoles = {}
        self.newBoxes = {}
        self.boxesToDelete = []
        
    def getUpdatedItems(self, existingItems, newItems):
        toUpdate = {}
        for item in newItems:
            if item not in existingItems.keys():
                toUpdate[item] = None
        return toUpdate

    def updateBoxes(self, boxes, noboxes):
        newBoxes = self.getUpdatedItems(self.boxes, boxes)
        self.newBoxes = newBoxes
        # delete moved boxes
        boxesToDelete = []
        for nobox in noboxes:
            if self.boxes.has_key(nobox):
                boxesToDelete.append(nobox)
        self.boxesToDelete = boxesToDelete
        
    def updateHoles(self, holes):
        self.newHoles = self.getUpdatedItems(self.holes, holes)

    def updateCachedChanges(self):
        self.boxes.update(self.newBoxes)
        self.holes.update(self.newHoles)
        for box in self.boxesToDelete:
            del self.boxes[box]
            
    def updateAssignments(self, brain):
        for box, robot in brain.boxes.items():
            if not self.boxes.has_key(box) or self.boxes[box] is None:
                self.boxes[box] = robot
        for hole, robot in brain.holes.items():
            if not self.holes.has_key(hole) or self.holes[hole] is None:
                self.holes[hole] = robot

    def isBoxAssigned(self, box):
        return self.boxes[box] is not None

    def isHoleAssigned(self, hole):
        return self.holes[hole] is not None

    def assignHole(self, hole, robot):
        self.holes[hole] = robot

    def assignBox(self, box, robot):
        self.boxes[box] = robot

    def getUnassignedBoxes(self):
        return [box for box in self.boxes.keys()
                if not self.isBoxAssigned(box) ]

    def getUnassignedHoles(self):
        return [hole for hole in self.holes.keys()
                if not self.isHoleAssigned(hole) ]

class Dummy:
    pass
_marker = Dummy()

class World:
    def __init__(self, size, robots, boxes, holes):
        self.size = size
        self.robots = robots
        self.boxes = boxes
        self.holes = holes
        
    def update(self):
        robots = self.robots
        for robot in robots:
            robot.lookAround()

        for robot in robots:
            robot.act()

    def getItemsNear(self, isItemAt, position, radius):
        x_robot, y_robot = position
        size = self.size
        items, empty = [], []
        # figure bounds for looking at stuff (rectangular universe)
        x1, x2 = (x_robot - radius), (x_robot + radius)
        y1, y2 = (y_robot - radius), (y_robot + radius)
        xmax, ymax = min(max(x1, x2), size - 1), min(max(y1, y2), size - 1)
        xmin, ymin = max(min(x1, x2), 0), max(min(y1, y2), 0)

        for x in range(xmin, xmax + 1):
            for y in range(ymin, ymax + 1):
                if dist(position, (x,y)) < radius:
                    if isItemAt(x, y):
                        items.append((x, y))
                    else:
                        empty.append((x, y))
        return items, empty

    def isBoxAt(self, x, y=_marker):
        if y is _marker:
            return x in self.boxes
        else:
            return (x, y) in self.boxes

    def isHoleAt(self, x, y=_marker):
        if y is _marker:
            return x in self.holes
        else:
            return (x, y) in self.holes

    def getHolesNear(self, position, radius):
        return self.getItemsNear(self.isHoleAt, position, radius)[0]

    def getBoxesNear(self, position, radius):
        # boxes move, so return empty squares too
        return self.getItemsNear(self.isBoxAt, position, radius)

    def moveBox(self, old, new):
        """ return 1 if a box was pushed into a hole"""
        self.boxes.remove(old)
        if new in self.holes:
            self.holes.remove(new)
            return 1
        else:
            self.boxes.append(new)
            return 0

    def getNumberOfHoles(self):
        return len(self.holes)

    def getNumberOfBoxes(self):
        return len(self.boxes)
    
    def printGrid(self):
        robotPositions = {}
        for r in self.robots:
            robotPositions[r.position] = (r, r.name[0])
            
        for i in range(self.size):
            for j in range(self.size):
                if (i, j) in self.boxes:
                    print '*',
                elif (i, j) in self.holes:
                    print '0',
                elif (i, j) in robotPositions.keys():
                    robot, initial = robotPositions[(i, j)]
                    if isinstance(robot.state, WanderingState):
                        initial = initial.lower()
                    else:
                        initial = initial.upper()
                    print '%s' %(initial,),
                else:
                    print '.',
            print ''

def mean(list):
    return reduce(add, list)/float(len(list))

def stdev(list):
    from math import sqrt
    return sqrt(mean(map(lambda x: x**2, list)) - mean(list)**2)
        

                

if __name__ == '__main__':
    import sys
    
    #sys.exit(main(sys.argv))
    
    nRobots, size = 4, 15
    #world, robots = initFullyConnectedWorld(nRobots, size)
    robots = [Robot('1', (0, 0)), Robot('2',  (9, 9))]
    world = World(10, robots, [(3, 6), (7, 4)], [(8, 1), (4, 9)])
    robots[0].setWorld(world)
    robots[1].setWorld(world)
    robots[0].addNeighbor(robots[1])
    robots[1].addNeighbor(robots[0])
    while world.getNumberOfHoles() > 0:
        world.printGrid()
        world.update()
        for robot in robots:
            robot.printBeliefs()
        print '-'*size*2
        raw_input()
    world.printGrid()
