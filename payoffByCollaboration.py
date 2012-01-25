from sim import initWorld, connectFully
from operator import add
from random import random

def mean(list):
    if len(list) == 0:
        return 0.0
    return reduce(add, list, 0.0)/float(len(list))

def stdev(list):
    from math import sqrt
    return sqrt(mean(map(lambda x: x**2, list)) - mean(list)**2)
        

def payoffForCollaboration(rate, agents, world,
                           timeLimit=3000):
    collaborators, t = [], 0
    for a in agents:
        if random() < rate:
            collaborators.append(a)
    connectFully(collaborators)
    while world.getNumberOfBoxes() > 0 and t < timeLimit:
        world.update()
        t += 1

    return t, mean([x.getPoints() for x in collaborators]), \
           mean([x.getPoints() for x in agents if x not in collaborators])

def main(argv):
    size = 15
    trials = 2
    nAgents = int(sys.argv[1])
    nGoals = int(sys.argv[2])
    
    print '#agents, goals, rate of collaboration, point for collab,'
    print '#points noncollaborators, weird payoff thing '
    print '#mean time'
    for rate in map(lambda x: .1*x, range(11)):
        meanPayoff, payoffPerTime, meanTime, nonCollab = 0.0, 0.0, 0.0, 0.0
        for trial in range(trials):
            world, agents = initWorld(nAgents, nGoals, size)
            t, collab, non = payoffForCollaboration(rate,
                                                    agents, world)
            payoffPerTime = collab/t
            meanPayoff += collab
            nonCollab += non
            meanTime += t
        meanPayoff /= float(trials)
        meanTime /= float(trials)
        payoffPerTime /= float(trials)
        nonCollab /= float(trials)
        
        print '%s %s %s %s %s %s %s' %(nAgents, nGoals, rate, meanPayoff,
                                 nonCollab, payoffPerTime,
                                 meanTime)
        sys.stdout.flush()
                
if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
