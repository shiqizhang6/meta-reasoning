
class Reasoner:

    # -------------------------------------->>
    def __init__(self, 
                 mapfile = '/home/szhang/projects/2015_meta_reasoning_pomdp/meta-reasoning/maps/4x3.95.map'
                 ):

        self.gridmap = []
        self.mapfile = mapfile
        self.read_map()

        # as a result, probability to other nearby (three) positions is 0.02
        self.prob_motion_forward = 0.9
        self.prob_motion_stay = 0.04

        # TODO
        
    # -------------------------------------->>
    def read_map(self):
        
        mapfile = self.mapfile
        f = open(mapfile, 'r')

        while True:

            l = f.readline()

            if l == '':
                break;
            else:
                self.gridmap.append(l[1:-2])

        self.gridmap = self.gridmap[1:-1]



    # -------------------------------------->>
    def get_map_size(self):

        return len(self.gridmap), len(self.gridmap[0])



# -------------------------------------->>
# -------------------------------------->>

if __name__ == "__main__":

    reasoner = Reasoner()


