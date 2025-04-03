import math
import random

from mesa.experimental.continuous_space.continuous_space_agents import ContinuousSpace, ContinuousSpaceAgent

# Robot agent that moves along the street and sweeps trash
class Robot(ContinuousSpaceAgent):
    """Initialize the robot

    Args:
        model: Mesa model
        space: Continue space that the robot is part of
        max_energy: Maximum energy that the robot can get
        max_speed: Maximum speed that the robot can attain
        capacity: Number of trash units that the robot can fit
    """
    def __init__(self, model,
                 space: ContinuousSpace,
                 max_energy = 100,
                 max_speed = 10,
                 capacity = 100):
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
        print(f"I am a robot {self.unique_id} at {self.position[0]}, {self.position[1]}")
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
                 speed = 5,
                 littering_rate = 5):
        super().__init__(space, model)

        # Initial position of the human
        self.position[0] = random.uniform(0, self.space.width)
        self.position[1] = random.uniform(0, self.space.height)

        # Walking speed of the human
        self.speed = speed
        # Littering rate of the human
        self.littering_rate = littering_rate
        # Direction that the human faces counting from rightwards direction counter in degrees and
        # average rotation of the human per step
        self.direction = random.uniform(0, 360)
        self.average_rotation = 1

    def step(self):
        self.move(self.speed)
        if random.uniform(0, 1) < self.littering_rate / 1000:
            self.litter()

    def move(self, speed):
        # TODO: Write a proper human movement function in which people don't just move randomly

        # Define human direction in radians and displacement coefficient in x and y directions
        radian_direction = 2*math.pi * (self.direction/360)
        x_disp = math.cos(radian_direction)
        y_disp = math.sin(radian_direction)

        # Update x coordinate
        new_x = self.position[0] + x_disp * speed / 100
        if new_x < 0:
            new_x = 0
            self.direction = 180 - self.direction
        if new_x > self.space.width:
            new_x = self.space.width
            self.direction = 180 - self.direction
        self.position[0] = new_x

        # Update y coordinate
        new_y = self.position[1] + y_disp * speed / 100
        if new_y < 0:
            new_y = 0
            self.direction = - self.direction
        if new_y > self.space.height:
            new_y = self.space.height
            self.direction = - self.direction
        self.position[1] = new_y

        # Update direction
        self.direction = (self.direction + random.uniform(-2*self.average_rotation, 2*self.average_rotation) + 360) % 360

    def litter(self):
        # TODO: Write a proper littering function that makes people throw trash in an existing pile if there is one nearby
        print(f"Human {self.unique_id} is littering")
        Trash.create_agents(
            self.model,
            1,
            space=self.space,
            x_coord=self.position[0],
            y_coord=self.position[1]
        )

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