#!/usr/bin/env python

import sys
import numpy
from numpy import matrix

class Policy(object):
  actions = None
  policy = None

  def __init__(self, num_states, num_actions, filename='policy/pomdp.policy'):
    try:
      f = open(filename, 'r')
    except:
      print('\nError: unable to open file: ' + filename + '\n')

    lines = f.readlines()

    # the first three and the last lines are not related to the actual policy
    lines = lines[3:-1]

    self.actions = -1 * numpy.ones((len(lines), 1, ))
    self.policy = numpy.zeros((len(lines), num_states, ))

    for i in range(len(lines)):
      l = lines[i].find('"')
      r = lines[i].find('"', l + 1)
      self.actions[i] = int(lines[i][l + 1 : r])

      ll = lines[i].find('>')
      rr = lines[i].find(' <')
      self.policy[i] = numpy.matrix(lines[i][ll + 1 : rr])
    
  def select_action(self, b):
    
    # sanity check if probabilities sum up to 1
    if sum(b) - 1.0 > 0.00001:
      print('Error: belief does not sum to 1, diff: ', sum(b) - 1.0)
      sys.exit()

    return self.actions[numpy.argmax(numpy.dot(self.policy, b)), 0]
    # return numpy.argmax(b) + 12
    # return numpy.random.randint(24, size=1)[0]

def main():
  p = Policy(24, 36)
  b = numpy.ones((24, 1, )) / 24
  print('best action: ' + str(p.select_action(b)))

if __name__ == '__main__':
  main()


