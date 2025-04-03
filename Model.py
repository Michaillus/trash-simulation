import random

from mesa import Model
from mesa.experimental.continuous_space.continuous_space import ContinuousSpace
from Agents import Human, Robot, Trash


"""Model that simulates a street with people passing along the street and throwing trash.
    A robot patrols the street and sweeps the trash.
    One step of the model is a decisecond (0.1 second) in real life.
    
    Args:
        street_length: Length of the street in meters
        street_width: Width of the street in meters
        nr_of_people: Number of people on the street
        human_speed_km_h: Speed of humans in kilometers/hour
        littering_rate: Rate with which people litter on the street in trash units per hour
        robot_max_energy: Maximum energy that robot can have
        robot_max_speed_km_h: Maximum speed of the robot in kilometers/hour
        robot_capacity: Capacity of the robot in units of trash
        seed: Seed for random number generator
"""
class TrashCollection(Model):
    def __init__(
            self,
            street_length = 100,
            street_width = 30,
            nr_of_people = 20,
            human_speed_km_h = 10,
            littering_rate = 5,
            robot_max_energy = 100,
            robot_max_speed_km_h = 10,
            robot_capacity = 100,
            enable_robot = True,
            seed = None
        ):

        super().__init__(seed=seed)

        # Size of the space
        # Width of space - x coordinate - is the length of the street
        self.width = street_length
        # Length of space - y coordinate - is the width of the street
        self.height = street_width

        # Attributes of Humans
        self.nr_of_people = nr_of_people
        # Speed of humans in meters per decisecond
        self.human_speed = human_speed_km_h / 36
        self.littering_rate = littering_rate

        # Create a continuous space
        dimensions = [[0, street_length], [0, street_width]]
        rng = random.Random(seed)
        self.space = ContinuousSpace(dimensions, torus=False, random=rng)

        # Create robot if the robot is enabled
        if enable_robot:
            Robot.create_agents(
                self,
                1,
                space=self.space,
                max_energy=robot_max_energy,
                # Maximum speed of the robot is converted to meters per decisecond
                max_speed=robot_max_speed_km_h / 36,
                capacity=robot_capacity,
            )

        # Populate the street with nr_of_people people at start
        Human.create_agents(
            self,
            nr_of_people,
            space=self.space,
            speed=self.human_speed,
            # Littering rate is converted to units of trash per decisecond
            littering_rate=littering_rate / 36000,
        )

        # Make the model running
        self.running = True


    def step(self):
        # First activate all the people
        self.agents_by_type[Human].shuffle_do("step")
        # Then activate the robot
        self.agents_by_type[Robot].do("step")
