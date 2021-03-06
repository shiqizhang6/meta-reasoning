#!/usr/bin/env python

import numpy
import sys
import matplotlib
import matplotlib.pyplot
import time

import meta_reasoner
import policy_parser

######################################################################
# There is only one world, maintained by this simulator
# Multiple planners will be using this simulator
######################################################################

delta = 0.00001

class Simulator(object):

    ##################################################################
    def __init__(self, gridmap = None, reasoner = None, agents = None, \
                 position = None):

        f = open(gridmap, 'r')
        self.gridmap = f.read().splitlines()
        self.reasoner = reasoner
        self.agents = agents
        self.pos = position # [r, c, o]
        self.prior = None # a distribution over all agents

        self.action = 0 # assigning an initial position
        self.obs = None
        self.decision_maker = 0 # agent 0 makes the decision

        num_states = len(self.agents[0].model['states'])
        for a in self.agents:
            a.belief = numpy.ones( (num_states) ) / num_states

        self.run(self.decision_maker)

    ##################################################################
    def run(self, n):

        self.action = 0
        num_states = len(self.agents[0].model['states'])

        print('number of states: ' + str(num_states))

        self.visualize(self.gridmap, self.agents[n].belief, self.pos)

        while True:

            self.obs = self.observe(self.reasoner, self.action, self.pos)
            print('observation: ' + str(self.obs))

            self.action = self.agents[n].select_action(self.agents[n].belief)
            print('action: ' + str(self.action))

            post = []
            for a in self.agents:

                p, a.belief = a.update_belief(a.belief, self.obs, self.action, 
                                              a.model)
                curr_state = self.rco_to_state(self.pos[0], self.pos[1], self.pos[2],
                                          self.gridmap)

                next_state_2d_mat = numpy.random.multinomial(1, a.model['trans_mat'][self.action][curr_state], 1)
                next_state = numpy.argmax(next_state_2d_mat[0])
                print('next state: ' + str(next_state))

                self.pos = self.state_to_rco(next_state, self.gridmap)

                self.visualize(self.gridmap, self.agents[n].belief, self.pos)

                post.append(p) # need normalization

        return True

    ##################################################################
    def visualize(self, gridmap, belief, pos):

        print(str(gridmap[0]))
        print(str(len(gridmap)))
        print(str(len(gridmap[0])))
        print(str(len(belief)))
        # the third dimensional identifies the orientations
        belief_3d = numpy.reshape(belief, (len(gridmap)-2, len(gridmap[0])-2, 4))
        # accumulate the values for orientations
        belief_2d = numpy.add.accumulate(belief_3d, 2)[:,:,3]
        
        print(belief_2d)
        img = matplotlib.pyplot.imshow(belief_2d, cmap=matplotlib.pyplot.gray(), interpolation='nearest')
        matplotlib.pyplot.show()


    ##################################################################
    def observe(self, reasoner, action, pos):
        
        gridmap = reasoner.gridmap
        model = reasoner.model

        rand = numpy.random.random_sample()
        acc = 0.0
        state = self.rco_to_state(pos[0], pos[1], pos[2], gridmap)
        for i in range(len(model['observations'])):
            acc += model['obs_mat'][action, state, i]
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

    global delta

    ##################################################################
    def __init__(self, gridmap = None, model = None, policy = None):

        self.belief = None
        self.obs = None
        self.action = None
        self.model = model
        self.policy = policy
        self.gridmap = gridmap

    ##################################################################
    def select_action(self, belief):
        
        # print('belief: ' + str(belief))

        if sum(belief) - 1.0 > delta:
            print('BELIEF DOES NOT SUM TO ONE')
            sys.exit()
    
        self.action = self.policy.select_action(belief)
        return self.action

    ##################################################################
    def update_belief(self, b, obs, action, model):

        new_b = numpy.dot(b, model['trans_mat'][action])

        for i in range(len(model['states'])):

            new_b[i] *= model['obs_mat'][action,i,obs]

        b = (new_b / sum(new_b.T)).T

        ################## TODO TODO ####################
        posterior = 1

        return posterior, b


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


