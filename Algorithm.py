import math

from mesa.model import Model
from Agents import Trash, Robot

# Return maximum trash size out of all trash spots
def maximum_trash_size(model: Model) -> int:
    max_size = 0
    for trash in model.agents_by_type[Trash]:
        max_size = max(max_size, trash.size)

    return max_size

"""Gives a floating point number score for a given trash spot. The bigger the score, the more feasible for
    the robot to collect the trash. The robot has four considerations that define feasibility of clearing a trash spot:
    1) Robot movement across the street should be minimized
    2) It is better to clean bigger spots of trash
    3) Robot should spend time proportionally to distance covered
    4) Robot should get full proportionally to distance covered
    
    Args:
        robot: The robot that collects the trash
        trash: Trash spot for which the score is calculated
"""
def trash_score(robot: Robot, trash: Trash) -> float:

    # Score of angle between rightwards direction and the trash spot
    x_disp = trash.position[0] - robot.position[0]
    y_disp = trash.position[1] - robot.position[1]
    angle = abs(360 * (math.atan2(y_disp, x_disp) / 2*math.pi))
    s_angle = 1 - angle / 180

    # Score by amount of trash
    max_trash_size = maximum_trash_size(robot.model)
    if max_trash_size == 0:
        s_amount = 0
    else:
        s_amount = trash.size / maximum_trash_size(robot.model)

    x_coord_after = trash.position[0]
    dist_part_covered = x_coord_after / robot.space.width

    # Score of time proportionality
    x_dist = (robot.position[0] - trash.position[0])
    y_dist = (robot.position[1] - trash.position[1])
    dist = (x_dist**2 + y_dist**2)**0.5
    time_to_trash = (1 + 0.05 * robot.model.nr_of_people) * dist / robot.max_speed
    time_part_passed = (robot.time_passed + time_to_trash) / robot.expected_time
    s_time = 1 - abs(dist_part_covered - time_part_passed)

    # Score of fullness proportionality
    capacity_part_filled = robot.fullness + trash.size / robot.capacity
    s_fullness = 1 - abs(dist_part_covered - capacity_part_filled)

    # Weights of the four score components
    w1 = 1
    w2 = 2
    w3 = 1
    w4 = 1
    # Total score of the trash spot
    score = w1 * s_angle + w2 * s_amount + w3 * s_time + w4 * s_fullness
    return score
