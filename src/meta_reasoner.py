
class Reasoner:

    #####################################################################
    def __init__(self, 
                 mapfile = '/home/szhang/projects/2015_meta_reasoning_pomdp/meta-reasoning/maps/4x3.95.map',
                 mapfile = '/home/szhang/projects/2015_meta_reasoning_pomdp/meta-reasoning/models/4x3.95.POMDP'
                 ):

        self.gridmap = []
        self.mapfile = mapfile
        self.gridmap = self.read_map(self.mapfile)

        # motion model
        self.motion = {'forward':0.9, 'stay':0.06, 'left':0.02, 'right':0.02}

        # observation model: left, front, right
        self.obs = {'ppp':0.91, \
                    'npp':0.02, 'pnp':0.02, 'ppn':0.02, \
                    'nnp':0.01, 'npn':0.01, 'pnn':0.01}
        
        self.model = self.create_model(self.gridmap, self.motion, self.obs)

        self.write_to_file(self.model, modelfile)

    #####################################################################
    def create_model(self, gridmap, motion, obs)

        

    #####################################################################
    def read_map(self, mapfile):
        
        f = open(mapfile, 'r')
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
    def get_map_size(self):

        return len(self.gridmap), len(self.gridmap[0])


#####################################################################
#####################################################################
if __name__ == "__main__":

    reasoner = Reasoner()

    return True
