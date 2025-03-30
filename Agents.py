import random

from mesa.experimental.continuous_space.continuous_space_agents import ContinuousSpaceAgent

class Robot(ContinuousSpaceAgent):
    def __init__(self, model, space, initial_x = 0, initial_y = 0, max_energy = 100, max_speed = 10):
        super().__init__(space, model)

        # Set position of the robot
        self.position[0] = initial_x
        self.position[1] = initial_y

    def step(self):
        print(f"I am a robot {self.unique_id} at {self.position[0]}, {self.position[1]}")

    def move(self, speed):
        print("Robot is moving")

    def sweep(self):
        print("Robot is sweeping")

    def charge(self):
        print("Robot is charging")

class Human(ContinuousSpaceAgent):
    def __init__(self, model, space):
        super().__init__(space, model)

        # Set initial position of the human
        self.position[0] = random.uniform(0, self.space.width)
        self.position[1] = random.uniform(0, self.space.height)

    def step(self):
        print(f"I am a human {self.unique_id} at {self.position[0]}, {self.position[1]}")

class Trash(ContinuousSpaceAgent):
    def __init__(self, space, model):
        super().__init__(space, model)
