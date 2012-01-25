from robot import mean, stdev
from sim import initUnconnectedWorld, initFullyConnectedWorld, \
     initStarWorld, initRingWorld

def averageBoxesLeft(listOfLists, default):
    """ take a list of lists, each representing # of boxes left
    at time t, return a list w/ average # of boxes left at time t"""
    boxesAtTime = map(None, *listOfLists)
    def noneToZero(lst):
        def h(x):
            if x is None:
                return default
            else:
                return x
        return map(h, lst)
    boxesAtTime = map(noneToZero, boxesAtTime)
    averageBoxes, stdevBoxes = [], []
    for boxes in boxesAtTime:
        averageBoxes.append(mean(boxes))
        stdevBoxes.append(stdev(boxes))

    return averageBoxes, stdevBoxes

def main(argv):
    inits = [(initUnconnectedWorld, 'unconnected.dat'),
             (initFullyConnectedWorld, 'fullyconnected.dat'),
             (initStarWorld, 'star.dat'),
             (initRingWorld, 'ring.dat')]
    nRobots, size = 6, 15
    nBoxes = 6
    nTrials = 10
    
    for init, filename in inits:
        boxesList = []
        timeToGoal = []
        
        for trial in range(nTrials):
            #print 'trial %d' %(trial,)
            world, robots = init(nRobots, nBoxes, size)
            boxesLeft, t = [], 0
            
            while world.getNumberOfHoles() > 0 and t < 3000:
                world.update()
                t += 1
                boxesLeft.append(nRobots - world.getNumberOfBoxes())

            timeToGoal.append(t)
            boxesList.append(boxesLeft)
        boxesLeft, stdev = averageBoxesLeft(boxesList, nRobots)

        f = open(filename, 'w')
        print >>f, '# nRobots = %d, nBoxes = %d, size = %d, nTrials = %d' %(
            nRobots, nBoxes, size, nTrials)
        print >>f, '# average time to goal %.02f' %(mean(timeToGoal),)
        for i in range(len(boxesLeft)):
            print >>f, i, boxesLeft[i], boxesLeft[i] + stdev[i], \
                  boxesLeft[i] - stdev[i]
        f.close()

    return 0

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
