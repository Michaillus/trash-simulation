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
            trash_spawn_rate = 0,
            people_speed = 0,
            robot_speed = 0,
            seed = None
        ):

        super().__init__(seed=seed)

        self.width = width
        self.height = height

        # Create a continuous space
        dimensions = [[0, width], [0, height]]
        rng = random.Random(42)
        self.space = ContinuousSpace(dimensions, torus=False, random=rng)

        # Create robot
        Robot.create_agents(
            self,
            1,
            space=self.space,
            initial_x=10,
            initial_y=10
        )

        # Create people
        Human.create_agents(
            self,
            nr_of_people,
            space=self.space
        )


    def step(self):
        # First activate all the people
        self.agents_by_type[Human].shuffle_do("step")
        # Then activate the robot
        self.agents_by_type[Robot].do("step")

trash_collection = TrashCollection()
trash_collection.step()