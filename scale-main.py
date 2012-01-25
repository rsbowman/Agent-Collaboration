from sim import initUnconnectedWorld, initFullyConnectedWorld, \
     initStarWorld, averageNumberOfEdges, totalNumberOfEdges
from operator import add

def mean(list):
    return reduce(add, list)/float(len(list))

def stdev(list):
    from math import sqrt
    return sqrt(mean(map(lambda x: x**2, list)) - mean(list)**2)
        


def main(argv):
    inits = [(initUnconnectedWorld, 'unconnected-scale.dat')] #,
             #(initFullyConnectedWorld, 'fullyconnected-scale.dat'),
             #(initStarWorld, 'star-scale.dat')]
    size =  15
    nBoxes = 8
    nTrials = 1

    for init, filename in inits:
        scaleInfo = []
        for nRobots in range(2, 9):
            times = []
            for trial in range(nTrials):
                print '%d robots, trial %d of %d' %(nRobots, trial, nTrials)
                world, robots = init(nRobots, nBoxes, size)
                t = 0

                while world.getNumberOfHoles() > 0 and t < 3000:
                    world.update()
                    t += 1

                times.append(t)
            scaleInfo.append([nRobots, mean(times),
                              averageNumberOfEdges(robots),
                              totalNumberOfEdges(robots)])

        f = open(filename, 'w')
        f.write('# nrobots, mean time, mean edges, total edges\n')
        for i in scaleInfo:
            f.write('%d %.02f %.02f %d\n' %(i[0], i[1], i[2], i[3]))
        f.close()

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
