import math
import random

from mesa.experimental.continuous_space.continuous_space_agents import ContinuousSpace, ContinuousSpaceAgent

EAST = 0
WEST = 180

DIST_FROM_EDGE = 1

LITTER_SEEK_RADIUS = 3

PERSONAL_SPACE_RADIUS = 2.5
TIME_TO_PRODUCE_TRASH = 20

MEDIUM_TRASH = 4
BIG_TRASH = 10


# Robot agent that moves along the street and sweeps trash
class Robot(ContinuousSpaceAgent):
    """Initialize the robot

    Args:
        model: Mesa model
        space: Continue space that the robot is part of
        max_energy: Maximum energy that the robot can get
        max_speed: Maximum speed that the robot can attain in meters per decisecond (0.1 second)
        capacity: Number of trash units that the robot can fit
    """
    def __init__(self, model,
                 space: ContinuousSpace,
                 max_energy = 100,
                 max_speed = 10,
                 capacity = 100,
                 robot_enabled = True):
        super().__init__(space, model)

        # Initial position of the robot
        self.position[0] = 0
        self.position[1] = space.height / 2

        # Initial and maximum energy of the robot
        self.energy = max_energy
        self.max_energy = max_energy
        # Maximum speed of the robot
        self.max_speed = max_speed
        # Maximum speed of the robot when it is sweeping
        self.max_sweep_speed = 0.2 * max_speed
        # Initial fullness and capacity of the robot
        self.fullness = 0
        self.capacity = capacity
        # Direction that robot faces counting from rightwards direction counterclockwise in degrees and
        # maximum rotation of the robot per 100 steps
        self.direction = 90
        self.max_rotation = 360

        # Time passed since the start of a cleaning loop in seconds
        self.time_passed = 0
        # Expected time it should take to finish a cleaning loop in seconds
        self.expected_time = (1 + 0.05 * model.nr_of_people) * space.width / max_speed

    # Actions of the robot on each step of the model
    def step(self):
        self.time_passed += 1

    """One step of robot movement. The robot turns up to maximum allowed rotation towards target position and moves
    forward with given speed.
    
    Args:
        speed: Speed with which the robot moves
        position: Position towards which robot rotates and moves 
    """
    def move(self, speed, position):
        print("Robot is moving")

    """Remove all the trash one step behind the robot considering that robot was moving with given speed.
    If robot was moving with the speed more than the max_sweep_speed, sweeping doesn't occur and an error
    message is printed.

    Args:
        speed: Speed with which the robot moved in current step
    """
    def sweep(self, speed):
        sweeping_radius = self.max_sweep_speed

        agents_nearby = None


    def charge(self):
        print("Robot is charging")

# Human agent that walks on the street and litters
class Human(ContinuousSpaceAgent):
    """Initialize a human agent.

    Args:
        model: A mesa model
        space: Continuous space that the human is part of
        speed: The human speed in distance covered per 100 steps
        littering_rate: Rate with which a human litters in number of trash units thrown per 1000 steps
    """
    def __init__(self, model,
                 space: ContinuousSpace,
                 x_coord=None,
                 speed = 5,
                 littering_rate = 1,
                 ):
        super().__init__(space, model)
        self.X_COORD_OFFSET = self.space.width // 5

        # Initial position of the human
        self.position[0] = random.uniform(0, self.space.width) if x_coord is None else x_coord
        self.position[1] = random.uniform(0, self.space.height)

        # Walking speed of the human
        self.speed = speed
        # Littering rate of the human
        self.littering_rate = littering_rate

        # Direction that the human faces counting from rightwards direction clockwise in degrees
        direction_for_given_x_coord = 0 if x_coord == -self.X_COORD_OFFSET else 180
        self.initial_direction = random.randint(0, 1) * 180 if x_coord is None else direction_for_given_x_coord
        self.direction = self.initial_direction

        # Destination of the human depending on direction
        if self.initial_direction == EAST:
            self.destination = self.space.width
        else:
            self.destination = 0

        # average rotation of the human per step
        self.average_rotation = 1

        # Does not immediately want to litter
        self.wants_to_litter = False
        self.nearest_trash: Trash | None = None
        self.wait = 0

    def step(self):
        self.wait -= 1
        self.move(self.speed)

        # Litter
        if random.uniform(0, 1) < self.littering_rate:
            self.wants_to_litter = True
            self.nearest_trash = self.get_nearest_trash(LITTER_SEEK_RADIUS)

            if self.nearest_trash is None:
                self.litter()
                self.wants_to_litter = False


        
        # If the human is out of bounds of street, remove it and generate a new human
        if not -self.X_COORD_OFFSET < self.position[0] < self.space.width + self.X_COORD_OFFSET:
            random_x_coord = (self.space.width + 2 * self.X_COORD_OFFSET) * random.randint(0, 1) - self.X_COORD_OFFSET

            Human.create_agents(
                    self.model,
                    1,
                    space=self.space,
                    speed=self.speed,
                    littering_rate=self.littering_rate,
                    x_coord=random_x_coord
                )
            self.remove()

    def move(self, speed):
        # There are 2 types of movement: If human wants to litter and sees trash spot nearby, human will go in a straight line towards
        # trash until they litter, else human will move towards self.destination whilst avoiding other humans and street edge.

        if self.wait > 0:
            return
        

        if not self.wants_to_litter:

            # Minimally change direction to make walking seem less automated
            self.direction = (self.initial_direction + random.uniform(-5*self.average_rotation, 5*self.average_rotation)) % 360


            # Update direction if human gets too close to street edge 
            if (self.position[1] < DIST_FROM_EDGE and self.destination == 0 or
                self.position[1] > self.space.height - DIST_FROM_EDGE and self.destination == self.space.width):
                self.direction = (self.initial_direction - 30) % 360

            if (self.position[1] > self.space.height - DIST_FROM_EDGE and self.destination == 0 or
                self.position[1] < DIST_FROM_EDGE and self.destination == self.space.width):
                self.direction = (self.initial_direction + 30) % 360
            

            # Update direction if there is a human nearby, angle of new direction also depends on human's destination
            # (takes priority over moving away from the edge)
            nearest_neighbor = self.get_nearest_human_in_front(PERSONAL_SPACE_RADIUS)
            if nearest_neighbor:
                
                # Depending on position of nearest human relative to self, move 30 degrees away from neighbor
                if self.destination == self.space.width:
                    x = self.position[1] - nearest_neighbor.position[1]
                    self.direction = (self.initial_direction + math.copysign(30, x)) % 360
                elif self.destination == 0:
                    x = nearest_neighbor.position[1] - self.position[1]
                    self.direction = (self.initial_direction + math.copysign(30, x)) % 360


            # Define human direction in radians and displacement coefficient in x and y directions
            radian_direction = 2*math.pi * (self.direction/360)
            x_disp = math.cos(radian_direction)
            y_disp = math.sin(radian_direction)

            # Update x coordinate
            new_x = self.position[0] + x_disp * speed
            self.position[0] = new_x

            # Update y coordinate
            new_y = self.position[1] + y_disp * speed
            if new_y < 0:
                new_y = 0
                self.direction = - self.direction
            if new_y > self.space.height:
                new_y = self.space.height
                self.direction = - self.direction
            self.position[1] = new_y

        else: # Human wants to litter
            
            if isinstance(self.nearest_trash, Trash):

                # Calculate angle to trash
                dx_trash = self.nearest_trash.position[0] - self.position[0]
                dy_trash = self.nearest_trash.position[1] - self.position[1]
                radian_direction = math.atan2(dy_trash, dx_trash)
                x_disp = math.cos(radian_direction)
                y_disp = math.sin(radian_direction)

                # Update x coordinate
                new_x = self.position[0] + x_disp * speed
                self.position[0] = new_x

                # Update y coordinate
                new_y = self.position[1] + y_disp * speed
                self.position[1] = new_y

                dist_to_trash = self.distance_to(self.nearest_trash)
                if dist_to_trash < 0.1:
                    self.position[0] = self.nearest_trash.position[0]
                    self.position[1] = self.nearest_trash.position[1]
                    self.nearest_trash.size += 1
                    self.nearest_trash = None
                    self.wants_to_litter = False
                    self.wait = TIME_TO_PRODUCE_TRASH



    def litter(self):
        Trash.create_agents(
            self.model,
            1,
            space=self.space,
            x_coord=self.position[0],
            y_coord=self.position[1]
        )
        self.wants_to_litter = False
    
    def get_nearest_human_in_front(self, radius):
        """
        Finds the nearest agent of type Human or Robot in front of self with given radius.

        Args:
            radius: radius of search

        Returns:
            The nearest Human or RObot, or None if none are found.
        """
        all_neighbors = self.get_neighbors_in_radius(radius)
        x = 1 if self.destination == 0 else -1

        # Filter agents by type
        human_neighbors = [agent for agent in all_neighbors[0] if isinstance(agent, Human | Robot) and x*(self.position[0] - agent.position[0]) > 0]

        if not human_neighbors:
            return None

        # Find the closest agent of the given type using Euclidian Distancen      
        nearest_agent = min(human_neighbors, key=lambda neighbor:  self.distance_to(neighbor))
        
        return nearest_agent
    

    def get_nearest_trash(self, radius):
        """
        Finds the nearest Trash in given radius.

        Args:
            radius: radius of search

        Returns:
            The nearest Trash in radius, or None if none are found.
        """
        all_neighbors = self.get_neighbors_in_radius(radius)

        # Filter agents by type
        trash_neighbors = [agent for agent in all_neighbors[0] if isinstance(agent, Trash)]

        if not trash_neighbors:
            return None
        
        # Find the closest agent of the given type using Euclidian Distancen      
        nearest_trash = min(trash_neighbors, key=lambda neighbor: self.distance_to(neighbor))
        
        return nearest_trash
    
    def distance_to(self, agent: ContinuousSpaceAgent):
        return math.sqrt(math.pow(self.position[0] - agent.position[0], 2) + math.pow(self.position[1] - agent.position[1], 2))


# Trash of different size that lies on the street
class Trash(ContinuousSpaceAgent):
    """Initializes a trash spot.

    Args:
        model: Mesa model
        space: Continuous space that the trash is part of
        x_coord: X coordinate of the trash
        y_coord: Y coordinate of the trash
    """
    def __init__(self, model, space, x_coord, y_coord):
        super().__init__(space, model)

        # Coordinates of the trash spot
        self.position[0] = x_coord
        self.position[1] = y_coord
        # Size of the trash spot. One unit of trash can be considered as one cup or food packaging
        self.size = 1

    # Increase amount of trash in the spot by one unit
    def increase(self):
        self.size += 1
