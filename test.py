from unittest import TestCase, TestSuite, makeSuite, main

from robot import Robot, World, RobotBrain, MovingToBoxState

class RobotTests(TestCase):
    def testInit(self):
        r = Robot('bob')
        self.assertEqual(r.name, 'bob')
        self.assertEqual(r.neighbors, [])
        self.assertEqual(r.position, (0, 0))

        r.addNeighbor(3)
        self.assert_(3 in r.neighbors)

        r.setWorld('boo')
        self.assertEqual(r.world, 'boo')

    def testLookAround(self):
        w = World(4, [], [(1, 1), (33, 2)], [(2, 0), (11, 11)])
        r = Robot('bob')
        r.setWorld(w)

        r.lookAround()
        r.act()
        self.assertEqual(r.brain.boxes.keys(), [(1, 1)])
        self.assertEqual(r.brain.holes.keys(), [(2, 0)])

    def testWanderingState(self):
        r = Robot('bob')
        w = World(4, [], [], [])
        r.setWorld(w)
        r.act()
        self.assertNotEqual(r.position, (0, 0))

        r = Robot('bob')
        w = World(4, [], [(1, 1)], [])
        r.setWorld(w)
        r.lookAround()
        r.act()
        self.assertEqual(r.brain.isBoxAssigned((1, 1)), True)
        self.assertEqual(isinstance(r.state, MovingToBoxState), True)
        
class WorldTests(TestCase):
    def testInit(self):
        w = World(4, [], [(1, 1)], [(2, 2)])
        self.assertEqual(w.boxes, [(1, 1)])
        self.assertEqual(w.holes, [(2, 2)])

    def testGetBoxesHoles(self):
        w = World(4, [], [(0, 0), (2, 1)], [(1, 3), (3, 1)])
        self.assertEqual(w.getBoxesNear((0, 0), 2),
                         ([(0, 0)],[(0, 1), (1, 0)]))
        self.assertEqual(w.getBoxesNear((0, 0), 4), ([(0, 0), (2, 1)], \
          [(0, 1), (0, 2), (0, 3), (1, 0), (1, 1), (1, 2), (2, 0), (3, 0)]))
        self.assertEqual(w.getBoxesNear((3, 3), 2),
                         ([], [(2, 3), (3, 2), (3, 3)]))
        self.assertEqual(w.getHolesNear((0, 0), 1), [])

class RobotBrainTests(TestCase):
    def testUpdateBoxesHoles(self):
        b = RobotBrain()
        b.updateBoxes([(0, 0), (1, 0)], [])
        b.updateCachedChanges()
        self.assertEqual(b.boxes, {(0, 0): None, (1, 0): None})

    def testUpdateBrain(self):
        r1 = RobotBrain()
        r2 = RobotBrain()
        boxes, holes = [(1, 1)], sorted([(2, 1), (2, 3)])
        r1.updateBoxes(boxes, [])
        r1.updateHoles(holes)
        r1.updateCachedChanges()
        r2.updateAssignments(r1)
        self.assertEqual(r2.boxes.keys(), boxes)
        self.assertEqual(sorted(r2.holes.keys()), holes)

        r1.assignBox(boxes[0], 'bob')
        self.assertEqual(r2.isBoxAssigned(boxes[0]), False)
        r2.updateAssignments(r1)
        self.assertEqual(r2.isBoxAssigned(boxes[0]), True)

    def testUnassignedItems(self):
        r1 = RobotBrain()
        r1.updateBoxes([(1, 1)], [])
        r1.updateHoles([(2, 2)])
        r1.updateCachedChanges()
        self.assertEqual(r1.getUnassignedBoxes(), [(1, 1)])
        self.assertEqual(r1.getUnassignedHoles(), [(2, 2)])
        
def suite(allTests=(RobotTests,
                    WorldTests,
                    RobotBrainTests)):
    suites = []
    for test in allTests:
        suite = makeSuite(test, 'test')
        suites.append(suite)
        
    return TestSuite(suites)

if __name__ == '__main__':
    main(defaultTest='suite')
