import random

from mesa import Model
from mesa.experimental.continuous_space.continuous_space import ContinuousSpace
from Agents import Human
from Agents import Robot

class TrashCollection(Model):
    def __init__(
            self,
            width = 100,
            height = 20,
            nr_of_people = 4,
            human_speed = 0,
            human_littering_rate = 0,
            robot_max_energy = 100,
            robot_max_speed = 10,
            robot_capacity = 100,
            seed = None
        ):

        super().__init__(seed=seed)

        self.width = width
        self.height = height

        # Create a continuous space
        dimensions = [[0, width], [0, height]]
        rng = random.Random(seed)
        self.space = ContinuousSpace(dimensions, torus=False, random=rng)

        # Create robot
        Robot.create_agents(
            self,
            1,
            space=self.space,
            max_energy=robot_max_energy,
            max_speed=robot_max_speed,
            capacity=robot_capacity,
        )

        # Create people
        Human.create_agents(
            self,
            nr_of_people,
            space=self.space,
            speed=human_speed,
            littering_rate=human_littering_rate,
        )

        # Make the model running
        self.running = True


    def step(self):
        # First activate all the people
        self.agents_by_type[Human].shuffle_do("step")
        # Then activate the robot
        self.agents_by_type[Robot].do("step")