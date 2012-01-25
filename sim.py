from robot import Robot, World
from random import choice

try:
    from random import sample
except ImportError:
    def sample(pop, k):
        ret = []
        p = pop[:]
        assert k <= len(pop)
        
        for i in range(k):
            item = choice(p)
            ret.append(item)
            p.remove(item)

        return ret
    

def initUnconnectedWorld(nRobots, nBoxes, size):
    places = [(0, 0), (size - 1, size - 1), (0, size - 1), (size - 1, 0),
              (0, size/2), (size - 1, size/2), (size/2, size - 1),
              (size/2, 0), (1, 1), (size-1, size-1)]
    assert nRobots <= len(places), 'too many robots for starting places'
    robots = []
    for i in range(nRobots):
        robots.append(Robot('%d' %(i+1,), places[i]))

    objects = sample([(x, y) for x in range(1, size - 1)
                             for y in range(1, size - 1)], 2*nBoxes)
    boxes = objects[:nBoxes]
    holes = objects[nBoxes:]
    
    world = World(size, robots, boxes, holes)

    for robot in robots:
        robot.setWorld(world)

    return world, robots

initWorld = initUnconnectedWorld

def connectFully(robots):
    for r1 in robots:
        for r2 in robots:
            if r1 != r2:
                r1.addNeighbor(r2)

def connectAsStar(robots):
    hub, others = robots[0], robots[1:]
    for other in others:
        hub.addNeighbor(other)
        other.addNeighbor(hub)
    return robots

def connectAsRing(robots):
    for i in range(len(robots) - 1):
        robots[i].addNeighbor(robots[i+1])
        robots[i+1].addNeighbor(robots[i])
    robots[0].addNeighbor(robots[-1])
    robots[-1].addNeighbor(robots[0])
    
def initFullyConnectedWorld(nRobots, nBoxes, size):
    world, robots = initUnconnectedWorld(nRobots, nBoxes, size)
    connectFully(robots)
    return world, robots

def initStarWorld(nRobots, nBoxes, size):
    world, robots = initUnconnectedWorld(nRobots, nBoxes, size)
    return world, connectAsStar(robots)

def initRingWorld(nRobots, nBoxes, size):
    world, robots = initUnconnectedWorld(nRobots, nBoxes, size)
    return world, connectAsRing(robots)

def averageNumberOfEdges(robots):
    return totalNumberOfEdges(robots)/float(len(robots))

def totalNumberOfEdges(robots):
    edges = 0
    for r in robots:
        edges += len(r.getPeers())
    return edges
