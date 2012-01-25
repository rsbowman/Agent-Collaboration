from sim import initWorld, connectFully
from payoffByCollaboration import mean

def timeToGoal(world, timeLimit=3000):
    t = 0
    while world.getNumberOfBoxes() > 0 and t < timeLimit:
        world.update()
        t += 1
    return t

def main(argv):
    print '# agents, agents/goals, delta t'
    nTrials, size = 500, 15
    agentsGoals = [(2, 12), (3, 11), (4, 10), (5, 9), (6, 8), (7, 7),
                   (8, 6), (9, 5), (10, 4), (11, 3), (12, 2)]
    
    for nAgents, nGoals in agentsGoals:
        deltaT = []
        for trial in range(nTrials):
            world, agents = initWorld(nAgents, nGoals, size)
            t_noncollab = timeToGoal(world)
            world, agents = initWorld(nAgents, nGoals, size)
            connectFully(agents)
            t_collab = timeToGoal(world)
            deltaT.append(t_noncollab - t_collab)
        print '%s %s %s' %(nAgents, nAgents/float(nGoals),
                           mean(deltaT))
        
if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
