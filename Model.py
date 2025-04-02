import random

from mesa import Model
from mesa.experimental.continuous_space.continuous_space import ContinuousSpace

from Agents import Human, Robot

class TrashCollection(Model):
    def __init__(
            self,
            width = 100,
            height = 30,
            nr_of_people = 20,
            human_speed = 10,
            littering_rate = 5,
            robot_max_energy = 100,
            robot_max_speed = 10,
            robot_capacity = 100,
            seed = None
        ):

        super().__init__(seed=seed)

        # Size of the space: width and height in meters
        self.width = width
        self.height = height

        # Attributes of Humans
        self.nr_of_people = nr_of_people
        self.human_speed = human_speed
        self.littering_rate = littering_rate

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

        # Populate the street with half of nr_of_people at start
        Human.create_agents(
            self,
            nr_of_people,
            space=self.space,
            speed=human_speed,
            littering_rate=littering_rate,
        )

        # Make the model running
        self.running = True


    def step(self):
        # First activate all the people
        self.agents_by_type[Human].shuffle_do("step")
        # Then activate the robot
        self.agents_by_type[Robot].do("step")
