#!/usr/bin/env python

import sys
from numpy import matrix
from numpy import ones
from numpy import zeros

class Reasoner(object):

    #####################################################################
    def __init__(self, 
                 mapfile = '../maps/4x3.95.map',
                 writetofile = False):

        self.gridmap = []
        self.mapfile = mapfile
        self.gridmap = self.read_map(self.mapfile)

        # motion model
        self.motion_linear = {'forward':0.9, 'stay':0.1}
        self.motion_angular = {'forward':0.9, 'stay':0.1}

        # observation model: left, front, right
        self.obs = {'correct':0.94, 'partially':0.02}

        # reward
        self.reward = {'success': 20, 'failure': -50, 'others': -1}
        
        self.model = {'discount':None, 'states':None, 'actions':None,
                      'observations':None, 'trans_mat':None, 'obs_mat':None, 
                      'reward_mat':None}
        self.model = self.create_model(self.model, self.gridmap, 
                                       self.motion_linear, self.motion_angular, 
                                       self.obs, self.reward)
        if writetofile:
            modelfile = mapfile.replace('.map', '.pomdp')
            modelfile = mapfile.replace('maps', 'models')
            self.write_to_file(self.model, modelfile)
            print('WROTE TO: ' + modelfile + '\n')


    #####################################################################
    def get_model(self):
        return self.model

    #####################################################################
    def write_to_file(self, model, modelfile):

        s = ''
        s += 'discount: ' + str(model['discount']) + '\n'
        s += 'values: reward\n'
        s += 'states: ' + ' '.join(model['states']) + '\n'
        s += 'actions: ' + ' '.join(model['actions']) + '\n'
        s += 'observations: ' + ' '.join(model['observations']) + '\n'

        for i in range(len(model['actions'])):
            s += '\nT: ' + model['actions'][i] + '\n'
            for j in range(len(model['states'])):
                for k in range(len(model['states'])):
                    s += str(model['trans_mat'][i, j, k]) + ' '
                s += '\n'

        for i in range(len(model['actions'])):
            s += '\nO: ' + model['actions'][i] + '\n'
            for j in range(len(model['states'])):
                for k in range(len(model['observations'])):
                    s += str(model['obs_mat'][i, j, k]) + ' '
                s += '\n'
            
        s += '\nR: * : * : * : * ' + str(self.reward['others']) + '\n'
        for i in range(len(model['states'])):
            r, c, o = self.state_to_rco(i, self.gridmap)
            if self.gridmap[r][c] == '#' or self.gridmap[r][c] == ' ':
                pass
            elif self.gridmap[r][c] == '+':
                s += 'R: * : * : ' + model['states'][i] + ' : * ' + \
                     str(self.reward['success']) + '\n'
            elif self.gridmap[r][c] == '-':
                s += 'R: * : * : ' + model['states'][i] + ' : * ' + \
                     str(self.reward['failure']) + '\n'
        print(s)

        s += '\n'
        f = open(modelfile, 'w+')
        f.write(s)
        f.close()

    #####################################################################
    def create_model(self, model, gridmap, motion_linear, motion_angular, \
                     obs, reward):

        ori = ['e', 's', 'w', 'n']

        num_rows, num_cols = self.get_map_size(gridmap)

        model['discount'] = 0.95

        states = []
        for i in range(num_rows):
            for j in range(num_cols):
                for o in ori:
                    states.append('r'+str(i)+'c'+str(j)+o)

        model['states'] = states

        actions = ['moveforward', 'turnleft', 'turnright']
        model['actions'] = actions

        # left, front, right
        observations = ['nnn', 'nnp', 'npn', 'npp', 'pnn', 'pnp', 'ppn', 'ppp']
        model['observations'] = observations

        # specify the matrix dimensions
        model['trans_mat'] = zeros((len(actions), len(states), len(states)))
        model['obs_mat'] = zeros((len(actions), len(states), len(observations)))
        model['reward_mat'] = zeros((len(actions), len(states)))

        # transition model: to fill trans_mat
        for i in range(len(actions)):

            if actions[i] == 'moveforward':

                for j in range(len(states)):

                    r, c, o = self.state_to_rco(j, gridmap)
                    new_r = r
                    new_c = c

                    if ori[o] == 'e':
                        new_c = c + 1
                    elif ori[o] == 's':
                        new_r = r + 1
                    elif ori[o] == 'w':
                        new_c = c - 1
                    elif ori[o] == 'n':
                        new_r = r - 1
                    else:
                        sys.stderr.write('ORIENTATION ERROR\n')

                    model['trans_mat'][i, j, j] = motion_linear['stay']

                    # if trying to move to an impossible position
                    if new_r < 0 or new_r >= num_rows or new_c < 0 \
                            or new_c >= num_cols:
                        model['trans_mat'][i, j, j] += motion_linear['forward']
                    elif gridmap[new_r][new_c] == '#':
                        model['trans_mat'][i, j, j] += motion_linear['forward']
                    else:
                        goal_s = self.rco_to_state(new_r, new_c, o, gridmap)
                        model['trans_mat'][i, j, goal_s] = motion_linear['forward']
                
            elif actions[i] == 'turnleft':

                for j in range(len(states)):

                    r, c, o = self.state_to_rco(j, gridmap)
                    new_o = (o + 1) % 4

                    model['trans_mat'][i, j, j] = motion_angular['stay']

                    goal_s = self.rco_to_state(r, c, new_o, gridmap)
                    model['trans_mat'][i, j, goal_s] = motion_angular['forward']

            elif actions[i] == 'turnright':

                for j in range(len(states)):

                    r, c, o = self.state_to_rco(j, gridmap)
                    new_o = (o - 1) % 4

                    model['trans_mat'][i, j, j] = motion_angular['stay']

                    goal_s = self.rco_to_state(r, c, new_o, gridmap)
                    model['trans_mat'][i, j, goal_s] = motion_angular['forward']

            else:
                sys.stderr.write('ACTION NOT FOUND\n')

        # observation model: to fill obs_mat
        # self.obs = {'correct':0.94, 'partially':0.02}

        for i in range(len(actions)):

            if actions[i] == 'moveforward':

                for j in range(len(states)):

                    r, c, o = self.state_to_rco(j, gridmap)

                    # to have the state index of the left, front, right cells
                    if o == 0: #'e'
                        state_le = self.rco_to_state(r-1, c, o, gridmap)
                        state_fr = self.rco_to_state(r, c+1, o, gridmap)
                        state_ri = self.rco_to_state(r+1, c, o, gridmap)
                    elif o == 1: #'s'
                        state_le = self.rco_to_state(r, c+1, o, gridmap)
                        state_fr = self.rco_to_state(r+1, c, o, gridmap)
                        state_ri = self.rco_to_state(r, c-1, o, gridmap)
                    elif o == 2: #'w'
                        state_le = self.rco_to_state(r+1, c, o, gridmap)
                        state_fr = self.rco_to_state(r, c-1, o, gridmap)
                        state_ri = self.rco_to_state(r-1, c, o, gridmap)
                    elif o == 3: #'n'
                        state_le = self.rco_to_state(r, c-1, o, gridmap)
                        state_fr = self.rco_to_state(r-1, c, o, gridmap)
                        state_ri = self.rco_to_state(r, c+1, o, gridmap)
                    else:
                        sys.stderr.write('ERROR ORIENTATION: ' + o + '\n')
                    
                    obs_code = 0

                    # to see if the left, front, and right cells are occupied
                    # and assign to each bit of the obs_code
                    r_le, c_le, o_le = self.state_to_rco(state_le, gridmap)
                    if state_le < 0:
                        obs_code += 0b100
                    elif gridmap[r_le][c_le] == '#':
                        obs_code += 0b100

                    r_fr, c_fr, o_fr = self.state_to_rco(state_fr, gridmap)
                    if state_fr < 0:
                        obs_code += 0b010
                    elif gridmap[r_fr][c_fr] == '#':
                        obs_code += 0b010

                    r_ri, c_ri, o_ri = self.state_to_rco(state_ri, gridmap)
                    if state_ri < 0:
                        obs_code += 0b001
                    elif gridmap[r_ri][c_ri] == '#':
                        obs_code += 0b001

                    # add noise to observations
                    model['obs_mat'][i, j, obs_code] = obs['correct']

                    model['obs_mat']\
                         [i, j, (obs_code | 0b100) - (obs_code & 0b100)] \
                         = obs['partially']

                    model['obs_mat']\
                         [i, j, (obs_code | 0b010) - (obs_code & 0b010)] \
                         = obs['partially']

                    model['obs_mat']\
                         [i, j, (obs_code | 0b001) - (obs_code & 0b001)] \
                         = obs['partially']

            elif actions[i] == 'turnleft':
                # assuming 'moveforward' to be the 1st action
                model['obs_mat'][i] = model['obs_mat'][0]             

            elif actions[i] == 'turnright':
                # assuming 'moveforward' to be the 1st action
                model['obs_mat'][i] = model['obs_mat'][0]             

            else:
                sys.stderr.write('OBSERVATION NOT FOUND\n')

        # reward function
        states_reward = []
        states_penalty = []
        row_num, col_num = self.get_map_size(gridmap)
        for i in range(row_num):
            for j in range(col_num):

                if gridmap[i][j] == '+':
                    states_reward.append(self.rco_to_state(i, j, 0, gridmap))
                    states_reward.append(self.rco_to_state(i, j, 1, gridmap))
                    states_reward.append(self.rco_to_state(i, j, 2, gridmap))
                    states_reward.append(self.rco_to_state(i, j, 3, gridmap))

                    state_east = self.rco_to_state(i, j, 0, gridmap)
                    model['reward_mat'][:, state_east : state_east+4] = \
                            reward['success']

                elif gridmap[i][j] == '-':
                    states_penalty.append(self.rco_to_state(i, j, 0, gridmap))
                    states_penalty.append(self.rco_to_state(i, j, 1, gridmap))
                    states_penalty.append(self.rco_to_state(i, j, 2, gridmap))
                    states_penalty.append(self.rco_to_state(i, j, 3, gridmap))

                    state_east = self.rco_to_state(i, j, 0, gridmap)
                    model['reward_mat'][:, state_east : state_east+4] = \
                            reward['failure']

                else:

                    state_east = self.rco_to_state(i, j, 0, gridmap)
                    model['reward_mat'][:, state_east : state_east+4] = \
                            reward['others']

        return model
        
    #####################################################################
    def rco_to_state(self, r, c, o, gridmap):

        num_rows, num_cols = self.get_map_size(gridmap)

        if r < 0 or r >= num_rows:
            return -1

        if c < 0 or c >= num_cols:
            return -1

        if o < 0 or o >= 4:
            sys.stderr.write('RCO_TO_STATE ERROR\n')

        s = ((num_cols * r) + c) * 4 + o

        return s

    #####################################################################
    def state_to_rco(self, s, gridmap):

        num_rows, num_cols = self.get_map_size(gridmap)
        o = s % 4
        s = s / 4
        c = s % num_cols
        r = s / num_cols

        return r, c, o

    #####################################################################
    def read_map(self, mapfile):
        
        try: 
            f = open(mapfile, 'r')
        except:
            sys.stderr.write('FILE NOT FOUND: ' + mapfile + '\n')

        gridmap = []

        while True:

            l = f.readline()

            if l == '':
                break;
            else:
                gridmap.append(l[1:-2])

        gridmap = gridmap[1:-1]

        return gridmap

    #####################################################################
    def get_map_size(self, gridmap):

        return len(gridmap), len(gridmap[0])


#####################################################################
#####################################################################
if __name__ == "__main__":

    reasoner = Reasoner()

