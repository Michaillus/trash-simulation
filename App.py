from Agents import Robot, Human, Trash, TrashCar
from Model import TrashCollection
from matplotlib.axes import Axes
from mesa.visualization import (
    SolaraViz,
    make_space_component,
)

# Function to portray the agents. Defines visual properties of each agent.
def trash_collection_portrayal(agent):
    if agent is None:
        return

    # Defines size of agents
    portrayal: dict[str, int | str] = {
        "size": 150,
    }

    # Defines color and shape of the robot
    # For now robot is a blue square
    if isinstance(agent, Robot):
        portrayal["color"] = "tab:blue"
        portrayal["marker"] = "s"
        portrayal["zorder"] = 3

    # Defines color and shape of humans
    # For now each human is an orange circle
    if isinstance(agent, Human):
        portrayal["color"] = "tab:orange"
        portrayal["marker"] = "o"
        portrayal["zorder"] = 2


    # Defines color and shape of trash spots
    # For now each trash spot is a grey cross
    if isinstance(agent, Trash):
        
        portrayal["marker"] = "X"
        portrayal["zorder"] = 1

        # As Trash "size" increases its marker's size increases and its color gets darker.
        portrayal["size"] = 150 + 30 * agent.size
        portrayal["color"] = str(0.5**agent.size)
    
    if isinstance(agent, TrashCar):
        portrayal["color"] = "1.0"
        portrayal["zorder"] = 0

    return portrayal


def post_process(ax: Axes):
    ax.set_aspect('equal')
    ax.set_xticks([])
    ax.set_yticks([])
    ax.get_figure().set_size_inches(15,5)

# Parameters of the model
model_params = {
    "seed": {
        "type": "InputText",
        "value": 42,
        "label": "Random seed",
    },

    "street_length": {
        "type": "SliderInt",
        "value": 150,
        "label": "Street length (meters)",
        "min": 100,
        "max": 300,
        "step": 1,
    },

    "street_width": {
        "type": "SliderInt",
        "value": 15,
        "label": "Street width (meters)",
        "min": 5,
        "max": 20,
        "step": 1,
    },

    "nr_of_people": {
        "type": "SliderInt",
        "value": 20,
        "label": "Number of people",
        "min": 1,
        "max": 200,
        "step": 1,
    },

    "human_speed_km_h": {
        "type": "SliderInt",
        "value": 5,
        "label": "People speed (km/h)",
        "min": 1,
        "max": 20,
        "step": 1,
    },

    "littering_rate": {
        "type": "SliderInt",
        "value": 12,
        "label": "Littering rate (trash units/day)",
        "min": 0,
        "max": 100,
        "step": 1,
    },

    "robot_max_speed_km_h": {
        "type": "SliderInt",
        "value": 7,
        "label": "Maximum robot speed (km/h)",
        "min": 1,
        "max": 50,
        "step": 1,
    },

    "robot_capacity": {
        "type": "SliderInt",
        "value": 50,
        "label": "Robot capacity (trash units)",
        "min": 1,
        "max": 200,
        "step": 1,
    },

    "robot_visibility": {
        "type": "SliderInt",
        "value": 10,
        "label": "Visibility of robot (meters)",
        "min": 1,
        "max": 50,
        "step": 1,
    },

    "off_screen_time": {
        "type": "SliderInt",
        "value": 30,
        "label": "Robot time out of screen (minutes)",
        "min": 1,
        "max": 180,
    },

    "full_simulation_time": {
        "type": "SliderInt",
        "value": 24,
        "label": "Full simulation time (hours)",
        "min": 1,
        "max": 72,
        "step": 1,
    },

    "enable_robot": {
        "type": "Checkbox",
        "value": True,
        "label": "Enable Robot",
    }
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
