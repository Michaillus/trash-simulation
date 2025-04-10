import math
import random

from mesa.experimental.continuous_space.continuous_space_agents import ContinuousSpace, ContinuousSpaceAgent

EAST = 0
WEST = 180

DIST_FROM_EDGE = 1

LITTER_SEEK_RADIUS = 6

STOP_RADIUS = 1
PERSONAL_SPACE_RADIUS = 2.5
TIME_TO_PRODUCE_TRASH = 20

MEDIUM_TRASH = 4
BIG_TRASH = 10

LUNCH_START_TIME = 216000 # Given that simulation starts at 6:00 AM, lunch starts at 12:00 PM (216000 is 6h in deciseconds)
LUNCH_END_TIME = 288000 # Lunch ends at 2:00 PM
DINNER_START_TIME = 468000 # Dinner starts at 7:00 PM
DINNER_END_TIME = 540000 # Dinner ends at 9:00 PM

class DirectionalAgent(ContinuousSpaceAgent):
    """Class with common functionality for agent that have direction.

        Args:
            space: Continue space that the agent is part of
            model: Mesa model
            initial_direction: Direction the agent is facing initially in degrees counting from east counter-clockwise
            max_rotation: Maximum rotation of agent in degrees per step (decisecond)
    """

    def __init__(self,
                 space: ContinuousSpace,
                 model,
                 initial_direction,
                 max_rotation):
        super().__init__(space, model)

        self.direction = initial_direction
        self.max_rotation = max_rotation


    def move_straight(self, speed):

        # Define agent direction in radians and displacement proportion in x and y directions
        radian_direction = 2 * math.pi * (self.direction / 360)
        x_disp = math.cos(radian_direction)
        y_disp = math.sin(radian_direction)

        # Update x coordinate
        self.position[0] += x_disp * speed

        # Update y coordinate
        new_y = self.position[1] + y_disp * speed
        if new_y < 0:
            new_y = 0
            self.direction = - self.direction
        if new_y > self.space.height:
            new_y = self.space.height
            self.direction = - self.direction
        self.position[1] = new_y

    def distance_to(self, agent: ContinuousSpaceAgent):
        return math.sqrt(math.pow(self.position[0] - agent.position[0], 2) + math.pow(self.position[1] - agent.position[1], 2))

    # Get smallest (can be negative) angle between current direction and direction towards the position pos
    def get_angle_towards(self, pos):
        angle = 360 * math.atan2(pos[1] - self.position[1], pos[0] - self.position[0]) / (2 * math.pi)

        angle_diff = angle - self.direction
        if abs(angle_diff + 360) < abs(angle_diff):
            angle_diff += 360
        if abs(angle_diff - 360) < abs(angle_diff):
            angle_diff -= 360
        return angle_diff

# Robot agent that moves along the street and sweeps trash
class Robot(DirectionalAgent):
    """Initialize the robot

    Args:
        model: Mesa model
        space: Continue space that the robot is part of
        max_speed: Maximum speed that the robot can attain in meters per decisecond (0.1 second)
        capacity: Number of trash units that the robot can fit
    """
    def __init__(self,
                 model,
                 space: ContinuousSpace,
                 max_speed = 10,
                 capacity = 100,
                 visibility = 10):

        # Robot initially looking rightwards.
        super().__init__(space, model, initial_direction=EAST, max_rotation=2)

        self.X_COORD_OFFSET = space.width // 5

        # Initial position of the robot
        self.position[0] = -self.X_COORD_OFFSET
        self.position[1] = space.height / 2

        # Maximum speed of the robot
        self.max_speed = max_speed
        # Maximum speed of the robot when it is sweeping or passing nearby people
        self.slow_speed = 0.2 * max_speed
        # Initial fullness and capacity of the robot
        self.fullness = 0
        self.capacity = capacity
        # Radius (in meters) in which robot can recognize trash and people
        self.visibility = visibility

        # Time passed since the start of a cleaning loop in deciseconds
        self.time_passed = 0
        # Expected time it should take to finish a cleaning loop in seconds
        self.expected_time = (1 + 0.05 * model.nr_of_people) * space.width / max_speed

        # Spot of trash that robot moves to
        self.target_trash = None

        # Amount of trash cleaned by robot from the start of simulation
        self.trash_cleaned = 0
        # Time left to charge
        self.time_to_charge = 0

        #  Whether the robot is close to a human in the current step
        self.close_to_human = False

    # Actions of the robot on each step of the model
    def step(self):
        # Check if robot is charging
        if self.time_to_charge > 0:
            self.charge()
            return

        # Choosing the next target if there is none and there is place in the robot left
        from Algorithm import choose_next_target
        if self.fullness < self.capacity and self.target_trash is None:
            agents_nearby, _ = self.get_neighbors_in_radius(self.visibility)
            trash_in_front = [agent for agent in agents_nearby if isinstance(agent, Trash)
                              and agent.position[0] > self.position[0]]
            self.target_trash = choose_next_target(self, trash_in_front)

        target_pos = None
        speed = self.max_speed
        if self.target_trash is None:
            # No trash in front, just go straight
            target_pos = [2 * self.space.width, self.position[1]]
        else:
            # If there is trash to collect, move towards the trash
            target_pos = self.target_trash.position

            # If trash is close enough, start sweeping
            if self.distance_to(self.target_trash) < self.max_speed:
                speed = self.slow_speed
                self.sweep()

        # Adjust speed depending on people nearby
        speed = self.adjust_speed(speed)

        # Move towards chosen position with chosen speed
        self.move(speed, target_pos)

        # Trash was missed (most probably due to robot being unable to change direction quick enough)
        if self.target_trash is not None and self.position[0] > self.target_trash.position[0]:
            self.target_trash = None

        # Robot is getting emptied and charges when reached the end of loop
        if self.position[0] > (self.space.width + self.X_COORD_OFFSET):
            self.time_to_charge = 36000
            self.fullness = 0

        self.time_passed += 1

    """One step of robot movement. The robot turns up to maximum allowed rotation towards target position and moves
    forward with given speed.
    
    Args:
        speed: Speed with which the robot moves
        position: Position towards which robot rotates and moves 
    """
    def move(self, speed, position):
        # Turn towards the position
        angle_diff = self.get_angle_towards(position)
        self.direction += sign(angle_diff) * min(abs(angle_diff), self.max_rotation)

        # Move towards the position with given speed
        self.move_straight(speed)

    """Remove all the trash one step behind the robot considering that robot was moving with given speed.
    If robot was moving with the speed more than the max_sweep_speed, sweeping doesn't occur and an error
    message is printed.

    Args:
        speed: Speed with which the robot moved in current step
    """
    def sweep(self):
        # Define sweeping radius - length that robot passes in one step(decisecond) with sweeping speed
        sweeping_radius = self.slow_speed

        # Get all trash in the radius
        agents_nearby, _ = self.get_neighbors_in_radius(sweeping_radius)
        trash_nearby = [agent for agent in agents_nearby if isinstance(agent, Trash)]

        # Remove all the trash nearby
        for trash in trash_nearby:
            self.trash_cleaned += trash.size
            self.fullness += trash.size

            # Reset nearest trash for people who had this trash as nearest
            for human in self.model.agents_by_type.get(Human, []):
                if human.nearest_trash == trash:
                    human.nearest_trash = None

            # Remove trash agent
            trash.remove()
            # Reset target trash
            self.target_trash = None


    def charge(self):
        self.time_to_charge -= 1
        if self.time_to_charge == 0:
            self.position[0] = -self.X_COORD_OFFSET
            self.position[1] = self.space.height / 2


    def adjust_speed(self, speed):
        agents_very_close, _ = self.get_neighbors_in_radius(STOP_RADIUS)
        people_front_close = [agent for agent in agents_very_close if isinstance(agent, Human)
                              and abs(self.get_angle_towards(agent.position)) <= 90]
        if len(people_front_close) > 0:
            self.close_to_human = True
            return 0

        agents_nearby, _ = self.get_neighbors_in_radius(PERSONAL_SPACE_RADIUS)
        people_front_nearby = [agent for agent in agents_nearby if isinstance(agent, Human)
                              and abs(self.get_angle_towards(agent.position)) <= 90]
        if len(people_front_nearby) > 0:
            self.close_to_human = True
            return self.slow_speed
        else:
            self.close_to_human = False
            return speed


class TrashCar(ContinuousSpaceAgent):
    """Initialize the robot

    Args:
        model: Mesa model
        space: Continue space that the robot is part of
        time_until_first_sweep: Number of steps until first sweep
        time_between_sweeps: Number of steps between sweeps
    """
    def __init__(self, model,
                 space: ContinuousSpace,
                 time_until_first_sweep = 100,
                 time_between_sweeps = 3600):

        super().__init__(space, model)

        # Initialize time until first sweep and time between sweeps.
        self.time_until_first_sweep = time_until_first_sweep
        self.TIME_BETWEEN_SWEEPS = time_between_sweeps
        self.time_until_next_sweep = self.TIME_BETWEEN_SWEEPS

        self.trash_cleaned = 0

    def step(self):
        self.time_until_first_sweep -= 1
        if self.time_until_first_sweep > 0:
            return
        elif self.time_until_first_sweep == 0:
            self.sweep()

        if self.time_until_next_sweep == 0:
            self.sweep()
            self.time_until_next_sweep = self.TIME_BETWEEN_SWEEPS
        self.time_until_next_sweep -= 1

    def sweep(self):
        for trash in list(self.model.agents_by_type.get(Trash, [])):
            self.trash_cleaned += trash.size
            trash.remove()

        for human in self.model.agents_by_type.get(Human, []):
            human.wants_to_litter = False


# Human agent that walks on the street and litters
class Human(DirectionalAgent):
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

        self.X_COORD_OFFSET = space.width // 5

        # Direction that the human faces counting from rightwards direction counterclockwise in degrees
        direction_for_given_x_coord = 0 if x_coord == -self.X_COORD_OFFSET else 180
        initial_direction = random.randint(0, 1) * 180 if x_coord is None else direction_for_given_x_coord

        super().__init__(space, model, initial_direction=initial_direction, max_rotation=5)

        # Initial position of the human
        self.position[0] = random.uniform(0, self.space.width) if x_coord is None else x_coord
        self.position[1] = random.uniform(0, self.space.height)

        # Walking speed of the human
        self.speed = speed
        # Littering rate of the human
        self.initial_littering_rate = littering_rate


        # Destination of the human depending on direction
        if self.direction == EAST:
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

        # Littering rate is increased during lunch and dinner time
        if LUNCH_START_TIME <= self.model.steps < LUNCH_END_TIME or DINNER_START_TIME <= self.model.steps < DINNER_END_TIME:
            littering_rate = self.initial_littering_rate * 3
        else:
            littering_rate = self.initial_littering_rate

        # Litter
        if random.uniform(0, 1) < littering_rate:
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
                    littering_rate=self.initial_littering_rate,
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
            self.direction = (self.direction + random.uniform(-5*self.average_rotation, 5*self.average_rotation)) % 360


            # Update direction if human gets too close to street edge 
            if (self.position[1] < DIST_FROM_EDGE and self.destination == 0 or
                self.position[1] > self.space.height - DIST_FROM_EDGE and self.destination == self.space.width):
                self.direction = (self.direction - 30) % 360

            if (self.position[1] > self.space.height - DIST_FROM_EDGE and self.destination == 0 or
                self.position[1] < DIST_FROM_EDGE and self.destination == self.space.width):
                self.direction = (self.direction + 30) % 360
            

            # Update direction if there is a human nearby, angle of new direction also depends on human's destination
            # (takes priority over moving away from the edge)
            nearest_neighbor = self.get_nearest_human_in_front(PERSONAL_SPACE_RADIUS)
            if nearest_neighbor:
                
                # Depending on position of nearest human relative to self, move 30 degrees away from neighbor
                if self.destination == self.space.width:
                    x = self.position[1] - nearest_neighbor.position[1]
                    self.direction = (self.direction + math.copysign(30, x)) % 360
                elif self.destination == 0:
                    x = nearest_neighbor.position[1] - self.position[1]
                    self.direction = (self.direction + math.copysign(30, x)) % 360

            # Move straight with human speed
            self.move_straight(speed)

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
                if dist_to_trash < math.sqrt((x_disp * speed)**2 + (y_disp * speed)**2):
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
        human_neighbors = [agent for agent in all_neighbors[0] if isinstance(agent, Human) and x*(self.position[0] - agent.position[0]) > 0]

        if not human_neighbors:
            return None

        # Find the closest agent of the given type using Euclidian Distance
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
        
        # Find the closest agent of the given type using Euclidian Distance
        nearest_trash = min(trash_neighbors, key=lambda neighbor: self.distance_to(neighbor))
        
        return nearest_trash



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


def sign(x):
    return 2 * (x >= 0) - 1