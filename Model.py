from datetime import datetime
import random

from mesa import Model
from mesa.datacollection import DataCollector
from mesa.experimental.continuous_space.continuous_space import ContinuousSpace

from Agents import Human, Robot, Trash, TrashCar

# Number of steps in second, minute, hour, day. One step is equivalent to decisecond = 1/10 second
STEPS_IN_SECONDS = 10
STEPS_IN_MINUTE = 60*STEPS_IN_SECONDS
STEPS_IN_HOUR = 60*STEPS_IN_MINUTE
STEPS_IN_DAY = 24*STEPS_IN_HOUR

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
        robot_visibility: Radius (in meters) in which robot can identify trash and people
        off_screen_time: Time in minutes that robot is out of the simulation when it reaches the end of the street
        full_simulation_time: The time of simulation in hours after which it stops
        enable_robot: If robot should be enabled and collect trash or stay idle
        
        seed: Seed for random number generator
"""
class TrashCollection(Model):
    def __init__(
            self,
            street_length = 100,
            street_width = 30,
            nr_of_people = 20,
            human_speed_km_h = 10,
            littering_rate = 10,
            robot_max_speed_km_h = 10,
            robot_capacity = 100,
            robot_visibility = 10,
            off_screen_time = 30,
            full_simulation_time = 24,
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

        # Number of hours that simulation runs in total
        self.full_simulation_time = full_simulation_time

        # Create a continuous space
        dimensions = [[0, street_length], [0, street_width]]
        rng = random.Random(seed)
        self.space = ContinuousSpace(dimensions, torus=False, random=rng)

        self.count = 0

        # Required for simulating current cleaning strategy
        self.total_trash_produced = 0

        # Set up data collection
        model_reporters={
                "Amount of trash on street": lambda m: sum(trash.size for trash in m.agents_by_type.get(Trash, [])),
                # Does not accurately reflect total trash produced, perfectly reflects amount of trash there would be using trashcar
                "Total trash produced": lambda m: m.total_trash_produced if m.steps < 863900 else 0,
                "Robot Disturbance": lambda m: (
                    sum(robot.close_to_human for robot in m.agents_by_type.get(Robot, [])) if len(m.agents_by_type.get(Robot, [])) > 0 else 0
                ),
                "Ticks with Robot present": lambda m: (
                    1 if any(robot.present for robot in m.agents_by_type.get(Robot, [])) else 0
                )
            }

        self.datacollector = DataCollector(model_reporters)

        # Create robot if the robot is enabled
        self.enable_robot = enable_robot

        if self.enable_robot:
            Robot.create_agents(
                self,
                1,
                space=self.space,
                # Maximum speed of the robot is converted to meters per decisecond
                max_speed=robot_max_speed_km_h / 36,
                capacity=robot_capacity,
                visibility=robot_visibility,
                off_screen_steps=off_screen_time * STEPS_IN_MINUTE,
            )
        else:
            TrashCar.create_agents(
                self,
                1,
                space=self.space,
                time_until_first_sweep=6*STEPS_IN_HOUR, # 6 hours in steps = deciseconds
                time_between_sweeps=STEPS_IN_DAY, # 1 day in steps = deciseconds
            )

        # Populate the street with nr_of_people people at start
        Human.create_agents(
            self,
            nr_of_people,
            space=self.space,
            speed=self.human_speed,
            # Littering rate is converted to average number of units of trash thrown by a person per step
            littering_rate=littering_rate / STEPS_IN_DAY,
        )

        # Make the model running
        self.running = True
        self.datacollector.collect(self)


    def step(self):
        # First activate all the people
        self.agents_by_type[Human].shuffle_do("step")
        if self.enable_robot:
            # Then activate the robot
            self.agents_by_type[Robot].do("step")
        else:
            self.agents_by_type[TrashCar].do("step")

        # Collect data
        self.datacollector.collect(self)

        if self.steps == self.full_simulation_time * STEPS_IN_HOUR: # 864000 number of steps in 24 hours (1 day)
            self.running = False
            df = self.datacollector.get_model_vars_dataframe()
            df.to_csv(f"logs\\{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.csv", index_label="Step") # file name format: YYYY-MM-DD_HH-MM-SS
