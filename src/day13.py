from src import computer

from typing import List
import os
# import pandas as pd
from scipy import sparse as sp

import matplotlib.pyplot as plt
import matplotlib.animation


class ArcadeCabinet(object):
    tiles = {'empty': 0,
             'wall': 1,
             'block': 2,
             'paddle': 3,
             'ball': 4}

    def __init__(self, program_path: str,
                 root_path: str = 'data/raw',
                 ):

        # Check the parameters
        path = os.path.join(root_path, program_path)
        if not os.path.exists(path):
            raise ValueError('Program not available at {}'.format(path))

        # Read the program
        f = open(path, 'r')
        program = f.read()
        program = list(map(int, program.split(',')))

        self.computer = computer.intcode_computer(
            program=program,
            wait_execution=False
        )

        # Initialize screen
        self.x_lim = 0
        self.y_lim = 0
        self.screen = None

    def _update_screen_status(self, output: List[int]):
        """ Update screen using the received computer output """
        if len(output) % 3 != 0:
            raise ValueError('Wrong output format!')

        for i in range(0, len(output), 3):
            x = output[i]
            y = output[i+1]
            tile_id = output[i+2]
            self.screen[x, y] = tile_id

    def _print_screen(self, output: List[int]):
        """ Creates a heatmap to represent the current screen status """
        max_size = max(self.x_lim, self.y_lim)
        x_size = round(7*(self.x_lim/max_size))
        y_size = round(7*(self.y_lim/max_size))
        fig, ax = plt.subplots(figsize=(x_size, y_size))
        screen = self.screen.transpose().toarray()

        return ax.pcolor(screen)

    def start_game(self):
        """ Runs the full program """
        self.computer.run_program()

        # Get all the movements
        output = []
        while not self.computer.execution_finished:
            output.extend(self.computer.get_output())

        # Get size of the screen
        self.x_lim = max([output[i] for i in range(0, len(output), 3)]) + 1
        self.y_lim = max([output[i] for i in range(1, len(output), 3)]) + 1

        # Initialize screen
        self.screen = sp.lil_matrix((self.x_lim, self.y_lim), dtype='uint8')
        self._update_screen_status(output)

        # Print game
        return self._print_screen(output)

    def count_tiles(self, tile_type: str) -> int:
        """ Count tiles type in the current screen """
        if tile_type not in self.tiles.keys():
            raise('Invalid tile type.')

        tile = self.tiles[tile_type]
        return (self.screen == tile).sum()
