import random


from common.Particle import Particle
from common.ToolBox import distance_to_obstacle,update_coord_according_scale
import math

class Particle_Filter:

    NB_PARTICLES=200
    FIXED_PLANE_Y = 100
    increment = 0
    DISTANCE_ERROR = 2

    width=0
    height=0

    SCALE_FACTOR=10

    obs_grid=[]
    particle_list=[]


    def __init__(self,width,height,obs_grid):
        self.width=width
        self.height=height
        self.obs_grid=obs_grid
        self.particle_list=self.getRandParticle(self.NB_PARTICLES,0,width,self.FIXED_PLANE_Y,self.FIXED_PLANE_Y)

    def resetParticle(self):
        self.particle_list = self.getRandParticle(self.NB_PARTICLES, 0, self.width, self.FIXED_PLANE_Y, self.FIXED_PLANE_Y)

        # ----------------------------------------------------------------------------------------------------------------
        # ----------------------------------------- COMPUTED RANDOM PARTICLES--------------------------------------------
        # ----------------------------------------------------------------------------------------------------------------
    def getRandParticle(self,nbr, start_x, max_x, start_y, max_y):
        particle_list = []
        ###################################
        ##### TODO
        ##   nbr: number fo particles
        ##   start_x: min x possible coordinate
        ##   max_x: max x possible coordinate
        ##   start_y: min y possible coordinate
        ##   max_y: max y possible coordinate
        #####
        ## Use the Particle object to fill the list particle_list
        ##
        for i in range(nbr):
            x = random.randint(start_x,max_x)
            y = random.randint(start_y,max_y)
            particle_list.append(Particle(x,y,1,1/nbr))
        return particle_list

        # ----------------------------------------------------------------------------------------------------------------
        # ----------------------------------- UPDATE PARTICLE ACCORDING NEX POSE-----------------------------------------
        # ----------------------------------------------------------------------------------------------------------------
    def updateParticle(self,plane_pose):
        # process particle according motion planning
        self.particle_list = self.motion_prediction()

        current_distance_to_obstacle = distance_to_obstacle(plane_pose['x'], plane_pose['y'], self.obs_grid,self.width,self.height,self.SCALE_FACTOR)

        self.weightingParticle_list( current_distance_to_obstacle)


        # ----------------------------------------------------------------------------------------------------------------
        # -------------------------------------- MOTION PREDICTION AND RESAMPLING   --------------------------------------
        # ----------------------------------------------------------------------------------------------------------------
    def motion_prediction(self):
        
        new_particle_list = []
        choices = {}
        for i in range(len(self.particle_list)):
            choices[self.particle_list[i].id()] = self.particle_list[i].w

        ###################################
        ##### TODO
        ##   self.particle_list: list of available particles
        ##
        #####
        ## Use the function self.weighted_random_choice(choices) returning
        #  coordinate from a particle according a
        #  roulette wheel algorithm
        #  Note that weighted_random_choice return a string containing coodinate x and y of the selected particle
        #   coord = self.weighted_random_choice(choices)
        #   x_coord = int(coord.split('_')[0])
        #   y_coord = int(coord.split('_')[1])
        for i in range(self.NB_PARTICLES) :
            coord = self.weighted_random_choice(choices)
            x_coord = int(coord.split('_')[0])
            y_coord = int(coord.split('_')[1])
            # First Motion calculus simple random
            #deplacement  = random.randint(0,2+self.increment)
            # Second Motion calculus with a gaussian
            mu = 0
            sigma = 1
            deplacement = 1+ self.increment + int(random.gauss(mu, sigma))
            new_particle_list.append(Particle(x_coord+deplacement,y_coord,1,1/self.NB_PARTICLES))
        
        test = random.randint(0,100)
        if test < 20 : 
            x = random.randint(0,self.width)
            y = random.randint(self.FIXED_PLANE_Y,self.FIXED_PLANE_Y)
            new_particle_list.append(Particle(x,y,1,1/self.NB_PARTICLES))
           

        return new_particle_list

        # -------------------------------------------------------
        # ----------- SELECT PARTICLE  -----------
        # -------------------------------------------------------
    def weighted_random_choice(self,choices):
        ###################################
        ##### TODO
        ##   choices: dictionary holding particle coordination as key
        ##  and weight as value
        ##  return the selected particle key
        #####
        wheel = []
        for id, w in choices.items():
            for i in range(int(w)+1):
                wheel.append(id)
        particle = random.randint(0,len(wheel)-1) 
        choice_str = wheel[particle]
        return choice_str

    # ----------------------------------------------------------------------------------------------------------------
    # --------------------------------------------- EVALUATE PARTICLE (proba) ---------------------------------------
    # ----------------------------------------------------------------------------------------------------------------
    def weightingParticle_list(self,observed_distance):
        sum_weights = 0
        for i in range(len(self.particle_list)):
            #Compute individual particle weight
            current_weight = self.weightingParticle(self.particle_list[i].x,  self.FIXED_PLANE_Y+50, observed_distance)
            self.particle_list[i].w = current_weight
            sum_weights += current_weight
        for i in range(len(self.particle_list)):
            if sum_weights != 0:
                #compute proba sucha as weight is normalized
                self.particle_list[i].proba = self.particle_list[i].w / float(sum_weights)
            else:
                self.particle_list[i].proba = 0


    # -----------------------------------------------------
    #  ----------- EVALUATE PARTICLE (Weight)  -----------
    # -----------------------------------------------------
    def weightingParticle(self,p_x, p_y, observed_distance):
        ###################################
        ##### TODO
        ##   p_x: x coordinate of the particle p
        ##  p_y: y coordinate of the particle p
        ##  observed_distance: distance to the ground
        ##  measure by the probe
        ##
        ## return weight corresponding to the given particle
        ## according observation
        ##
        ## Note use the function distance_to_obstacle to get the
        ## estimate particle to the ground distance
        
        weight = 0

        mu = 0
        observation_error = int(random.gauss(mu, self.DISTANCE_ERROR))
        distance_particle = distance_to_obstacle(p_x,p_y,self.obs_grid,self.width,self.height,self.SCALE_FACTOR) + observation_error
        print(observation_error)
        diff_distance = abs(distance_particle-observed_distance)
        # First calculus method 
        # mu = 0
        # sigma = 4
        # weight = 10*math.exp(-((diff_distance - mu) ** 2) / (2 * sigma ** 2))
        # Second calculus method
        weight = 10/(math.exp(0.15*diff_distance))
        return weight
