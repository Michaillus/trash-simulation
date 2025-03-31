from Agents import Robot, Human, Trash
from Model import TrashCollection
from mesa.visualization import (
    SolaraViz,
    make_space_component
)

# Function to portray the agents. Defines visual properties of each agent.
def trash_collection_portrayal(agent):
    if agent is None:
        return

    # Defines size of agents
    portrayal = {
        "size": 25,
    }

    # Defines color and shape of the robot
    # For now robot is a blue square
    if isinstance(agent, Robot):
        portrayal["color"] = "tab:blue"
        portrayal["marker"] = "s"

    # Defines color and shape of humans
    # For now each human is an orange circle
    if isinstance(agent, Human):
        portrayal["color"] = "tab:orange"
        portrayal["marker"] = "o"

    # Defines color and shape of trash spots
    # For now each trash spot is a grey triangle
    if isinstance(agent, Trash):
        portrayal["color"] = "tab:grey"
        portrayal["marker"] = "x"

    return portrayal


def post_process(ax):
    ax.set_aspect("equal")
    ax.set_xticks([])
    ax.set_yticks([])

# Parameters of the model
model_params = {
    "seed": {
        "type": "InputText",
        "value": 42,
        "label": "Random seed",
    },

    "width": {
        "type": "SliderInt",
        "value": 100,
        "label": "Street length",
        "min": 10,
        "max": 300,
        "step": 1,
    },

    "height": {
        "type": "SliderInt",
        "value": 20,
        "label": "Street width",
        "min": 5,
        "max": 50,
        "step": 1,
    },

    "nr_of_people": {
        "type": "SliderInt",
        "value": 40,
        "label": "Number of people",
        "min": 1,
        "max": 200,
        "step": 1,
    },

    "human_speed": {
        "type": "SliderInt",
        "value": 10,
        "label": "Speed with which people move",
        "min": 1,
        "max": 50,
        "step": 1,
    },

    "human_littering_rate": {
        "type": "SliderInt",
        "value": 5,
        "label": "People littering rate",
        "min": 0,
        "max": 100,
        "step": 1,
    },

    "robot_max_energy": {
        "type": "SliderInt",
        "value": 100,
        "label": "Maximum energy of robot",
        "min": 0,
        "max": 1000,
        "step": 1,
    },

    "robot_max_speed": {
        "type": "SliderInt",
        "value": 10,
        "label": "Maximum speed of robot",
        "min": 0,
        "max": 50,
        "step": 1,
    },

    "robot_capacity": {
        "type": "SliderInt",
        "value": 100,
        "label": "Capacity of robot",
        "min": 0,
        "max": 1000,
        "step": 1,
    },
}

# Create an instance of the model
trash_collection = TrashCollection()

# Component of visualization that shows the space
space_component = make_space_component(
    trash_collection_portrayal, draw_grid=False, post_process=post_process
)

# Instance of a visualization
page = SolaraViz(
    trash_collection,
    components=[space_component],
    model_params=model_params,
    name="Trash Collection"
)

page
