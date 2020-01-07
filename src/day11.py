
from typing import List

from src import computer


def get_painted_positions(program: List[int]) -> dict:
    """
    Returns a dictionary whose keys are tuples containing the positions
    visited by the 'hull painting robot', assuming it starts at position
    (0,0). The dictinary values are the final color of that cell after
    the robot paints it: 0-black, 1-white
    """

    # Robot parameters
    direction = (0,1) # up: (0,1), right: (1,0), down: (0,-1), left: (-1,0)
    current_position = (0,0)
    visited = {}

    # Launch the computer
    pc = computer.intcode_computer(program=program,
                                   wait_execution=False)
    pc.run_program()

    # Go trough the program outputs
    while pc.execution_finished is False:

        # Get current cell color
        cell_color = visited.get(current_position, 0)

        # Input camera retrieved color
        pc.set_input(cell_color)

        # Get computer output
        output = pc.get_output()
        new_color = output[0]
        turn = output[1]

        # Update color at current cell
        visited.update({current_position: new_color})

        # Move the robot
        if turn == 0:
            # turn left
            direction = (-direction[1], direction[0])
        elif turn == 1:
            # turn right
            direction = (direction[1], -direction[0])
        else:
            raise ValueError('Incorrect turning value {}'.format(turn))
        current_position = tuple(map(sum, zip(current_position, direction)))

    return visited
