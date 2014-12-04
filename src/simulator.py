#!/usr/bin/env python

import numpy
import sys

import meta_reasoner
import policy_parser


######################################################################
# There is only one world, maintained by this simulator
# Multiple planners will be using this simulator
######################################################################
class Simulator(object):

    ##################################################################
    def __init__(self, gridmap = None, reasoner = None, agents = None, \
                 position = None):

        self.gridmap = gridmap
        self.reasoner = reasoner
        self.agents = agents
        self.pos = position # [r, c, o]
        self.prior = None # a distribution over all agents

        self.action = None
        self.obs = None
        self.decision_maker = 0 # agent 0 makes the decision

        self.run(self.decision_maker)

    ##################################################################
    def run(self, n):

        while True:

            self.obs = self.observe(self.reasoner, self.action, self.pos)
            self.action = self.agents[n].select_action(self.agents[n].belief, \
                                                       self.agents[n].policy)
            post = []
            for a in self.agents:
                p, a.belief = a.update_belief(a.obs, a.action, a.model)
                post.append(p) # need normalization

        return True

    ##################################################################
    def observe(self, reasoner, action, pos):
        gridmap = reasoner.gridmap
        model = reasoner.model

        rand = numpy.random.random_sample()
        acc = 0.0
        state = self.rco_to_state(pos[0], pos[1], pos[2], gridmap)
        for i in range(len(model['observations'])):
            acc += model['obs_mat'][action, state, i]
            print(acc)
            print(rand)
            if acc > rand:
                obs = i
                break
        else:
            print('ERROR IN MAKING OBSERVATION')

        return obs

    ##################################################################
    def move(self, reasoner, action, pos):

        gridmap = reasoner.gridmap
        model = reasoner.model
        state = self.rco_to_state(pos[r], pos[c], pos[o], gridmap)
        
        rand = numpy.random.random_sample()
        acc = 0.0
        for i in range(len(model['states'])):
            acc += model['trans_mat'][action, state, i]
            if acc > rand:
                next_state = i
                break
        else:
            print('ERROR IN MOVING TO NEXT POSITION')

        return reasoner.state_to_rco(next_state, gridmap)

    ##################################################################
    def state_to_rco(self, state, gridmap):
        return self.reasoner.state_to_rco(state, gridmap)

    ##################################################################
    def rco_to_state(self, r, c, o, gridmap):
        return self.reasoner.rco_to_state(r, c, o, gridmap)


######################################################################
# Every POMDP model corresponds to an agent
######################################################################
class Agent(object):

    delta = 0.00001

    ##################################################################
    def __init__(self, gridmap = None, model = None, policy = None):

        self.belief = None
        self.obs = None
        self.action = None
        self.model = model
        self.policy = policy
        self.gridmap = gridmap

    ##################################################################
    def select_action(self):

        if sum(self.belief) - 1.0 > delta:
            print('BELIEF DOES NOT SUM TO ONE')
            sys.exit()
    
        self.action = numpy.argmax(numpy.dot(self.policy.policy, self.belief))
        return self.action

    ##################################################################
    def update_belief(self):

        new_b = numpy.dot(self.belief, self.model)

        for i in range(len(self.model['states'])):
            new_b[0, i] *= self.model['obs_mat'][self.action, i, self.obs]

        self.b = (new_b / sum(new_b.T)).T

        return posterior, belief


######################################################################
# Entry of the program
######################################################################
if __name__ == '__main__':
   
    map0 = '../maps/test0.map'
    map1 = '../maps/test1.map'
    map2 = '../maps/test2.map'

    r0 = meta_reasoner.Reasoner(mapfile = map0)
    r1 = meta_reasoner.Reasoner(mapfile = map1)
    r2 = meta_reasoner.Reasoner(mapfile = map2)

    print('created resoners')

    policy0 = policy_parser.Policy(len(r0.model['states']), \
            len(r0.model['actions']), filename = '../policies/test0.policy')
    policy1 = policy_parser.Policy(len(r1.model['states']), \
            len(r1.model['actions']), filename = '../policies/test1.policy')
    policy2 = policy_parser.Policy(len(r2.model['states']), \
            len(r2.model['actions']), filename = '../policies/test2.policy')

    print('created policies')

    a0 = Agent(gridmap = map0, model = r0.get_model(), policy = policy0)
    a1 = Agent(gridmap = map1, model = r1.get_model(), policy = policy1)
    a2 = Agent(gridmap = map2, model = r2.get_model(), policy = policy2)

    print('created agents')

    pos = [0, 0, 0]

    # this identifies the underlying domain, that is actually used
    r = r0
    s = Simulator(gridmap = map0, reasoner = r, agents = [a0, a1, a2], \
                  position = pos)


