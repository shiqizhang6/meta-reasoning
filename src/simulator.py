#!/usr/bin/env python

import meta_reasoner
import policy_parser

######################################################################
# There is only one world, maintained by this simulator
# Multiple planners will be using this simulator
######################################################################
class Simulator(object):

    def __init__(gridmap = None, model = None, planners = None, \
                 position = None):

        self.gridmap = gridmap
        self.planners = planners
        self.pos = position

    def get_observation(self):

        pass

    def get_next_pos(self):

        pass

######################################################################
# Every POMDP model corresponds to a planner
######################################################################
class Planner(object)

    def __init__(self, gridmap = None, model = None, policy = None):

        self.belief = None
        self.obs = None
        self.action = None
        self.model = model
        self.policy = policy
        self.gridmap = gridmap

    def select_action(self, belief, policy)

        return action

    def update_belief(self, obs, action, model):

        return belief

######################################################################
# Entry of the program
######################################################################
if __name__ == '__main__':
   
    map0 = '../maps/test0.map'
    map1 = '../maps/test1.map'
    map2 = '../maps/test2.map'

    r0 = meta_reasoner(mapfile = map0)
    r1 = meta_reasoner(mapfile = map1)
    r2 = meta_reasoner(mapfile = map2)

    policy0 = policy_parser(len(r0.get_model().states), \
            len(r0.get_model().actions), filename = '../policies/test0.policy')
    policy1 = policy_parser(len(r1.get_model().states), \
            len(r1.get_model().actions), filename = '../policies/test1.policy')
    policy2 = policy_parser(len(r2.get_model().states), \
            len(r2.get_model().actions), filename = '../policies/test2.policy')

    p0 = Planner(gridmap = map0, model = r0.get_model(), policy = policy0)
    p1 = Planner(gridmap = map1, model = r1.get_model(), policy = policy1)
    p2 = Planner(gridmap = map2, model = r2.get_model(), policy = policy2)

    pos = [0, 0, 0]

    # this identifies the underlying domain, that is actually used
    r = r0
    s = Simulator(gridmap = map0, model = r.model, planners = [p0, p1, p2], \
                  position = pos)






