from src import computer

from typing import List
import os
from scipy import sparse as sp
import readchar
import time

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
                 autoplay: bool = False,
                 print_screen: bool = True
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

        # Game parameters
        self.console = False
        self.score = 0
        self.max_score = 0  # To print when game is over
        self.autoplay = autoplay
        self.print_screen = print_screen

    def insert_quarters(self, quarters: int):
        self.computer.update_memory((0, quarters))
        self.console = True

    def _update_status(self, output: List[int]):
        """ Update screen using the received computer output """

        n = 3*int(len(output)/3)
        for i in range(0, n, 3):
            if output[i] == -1:
                # New score
                if output[i+1] != 0:
                    raise ValueError('Incorrect output format!', output)
                self.score = output[i+2]
                if self.score > self.max_score:
                    self.max_score = self.score
            else:
                # Screen
                x = output[i]
                y = output[i+1]
                tile_id = output[i+2]
                self.screen[x, y] = tile_id

        return output[(i+3):]

    def _print_screen(self, output: List[int]):
        """ Creates a heatmap to represent the current screen status,
        or print the status in the terminal, depending on the value of
        the parameter 'console' """
        if not self.print_screen:
            return
        screen = self.screen.transpose().toarray()

        # Return a heatmap (for part 1)
        if not self.console:
            max_size = max(self.x_lim, self.y_lim)
            x_size = round(7*(self.x_lim/max_size))
            y_size = round(7*(self.y_lim/max_size))
            fig, ax = plt.subplots(figsize=(x_size, y_size))
            return ax.pcolor(screen)

        # Print the current screen in the console
        print("\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n")
        for row in screen:
            line = []
            for i in range(len(row)):
                tile = row[i]
                if tile == self.tiles['wall']:
                    if i == 0 or i == (self.x_lim-1):
                        line.append('|')
                    else:
                        line.append('-')
                elif tile == self.tiles['block']:
                    line.append('#')
                elif tile == self.tiles['paddle']:
                    line.append('=')
                elif tile == self.tiles['ball']:
                    line.append('o')
                else:
                    line.append(' ')
            print(''.join(line))

        # Print the current score
        print("\n")
        print(f'Your score: {self.score}')

    def _initial_screen(self):
        """ Print initial screen before user starts playing """

        # Get all the movements
        output = []
        while not self.computer.waiting_for_input and not self.computer.execution_finished:
            output.extend(self.computer.get_output())

        # Get size of the screen
        self.x_lim = max([output[i] for i in range(0, len(output), 3)]) + 1
        self.y_lim = max([output[i] for i in range(1, len(output), 3)]) + 1

        # Initialize screen
        self.screen = sp.lil_matrix((self.x_lim, self.y_lim), dtype='uint8')
        self._update_status(output)

        # Print game
        return self._print_screen(output)

    @staticmethod
    def _read_key():
        """ Reads an arrow from the keyboard. Up and down are neutral movements """
        keypress = readchar.readkey()
        key = None
        while key is None:
            if keypress == readchar.key.LEFT:
                key = 'left'
            elif keypress == readchar.key.RIGHT:
                key = 'right'
            elif (keypress == readchar.key.UP) or (keypress == readchar.key.DOWN):
                key = 'neutral'
        return key

    def _get_key(self):
        """ Returns the next movement, depending on whether the user is
        playing or not.
        - If the user is playing, reads an arrow
        - If the computer is playing, it computes the direction using the
        relative positions of the ball and the paddle
        """
        if not self.autoplay:
            return self._read_key()
        else:
            ball = (self.screen == self.tiles['ball']).nonzero()
            paddle = (self.screen == self.tiles['paddle']).nonzero()
            if len(ball[0]) > 0 and len(paddle[0]) > 0:
                if ball[0][0] < paddle[0][0]:
                    return 'left'
                elif ball[0][0] > paddle[0][0]:
                    return 'right'
                else:
                    return 'neutral'
            else:
                return 'neutral'

    def start_game(self):
        """ Runs the full game """
        self.computer.run_program()

        # Print initial screen
        out = self._initial_screen()
        if not self.console:
            return out

        leftovers = []
        while not self.computer.execution_finished:
            if self.autoplay is True and self.print_screen is True:
                time.sleep(0.2)

            if self.computer.waiting_for_input:
                key = self._get_key()
                if key == 'left':
                    self.computer.set_input(-1, clear=True)
                elif key == 'right':
                    self.computer.set_input(1, clear=True)
                else:
                    self.computer.set_input(0, clear=True)

            # Update the screen after the movement
            output = self.computer.get_output()
            self.computer.input_queue.queue.clear()
            leftovers = self._update_status(output)

            # Sometimes the output is not complete...
            while len(leftovers) > 0:
                output = leftovers + self.computer.get_output()
                leftovers = self._update_status(output)
            self._print_screen(output)
            self.computer.input_queue.queue.clear()

    def count_tiles(self, tile_type: str) -> int:
        """ Count tiles type in the current screen """
        if tile_type not in self.tiles.keys():
            raise('Invalid tile type.')

        tile = self.tiles[tile_type]
        return (self.screen == tile).sum()


def play_arcade(autoplay: bool = False, print_screen: bool = True):
    """Runs the game!
    
    Keyword Arguments:
        autoplay {bool} -- Whether the computer should play (default: {False})
        print_screen {bool} -- In case the computer is playing, whether the
            screen should be printed or not (default: {True})
    """
    arcade = ArcadeCabinet(program_path='program.txt',
                           root_path='data/raw/day13',
                           autoplay=autoplay,
                           print_screen=print_screen
                           )

    if autoplay is False:
        print("\n\n")
        print("---------------------------------------------------")
        print("- Use left and right arrows to move the paddle")
        print("- Use up or down arrow to stay in the same position")
        print("---------------------------------------------------")
        print("\n\n")
        print("Let's play! (press any key to start)")
        while readchar.readkey() is None:
            pass

    arcade.insert_quarters(2)
    arcade.start_game()

    print("\n\n")
    if arcade.score == 0:
        print('GAME OVER...')
    else:
        print('WELL DONE!!!')
    print(f' Your final score is: {arcade.max_score}')
    print("\n\n")


if __name__ == '__main__':
    play_arcade()
