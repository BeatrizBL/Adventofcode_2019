from src import computer

from queue import Queue
from typing import List
import itertools
import math
import os
import time


class Amplifiers(object):

    def __init__(self,
                 phase_setting: List[int],
                 program: List[int],
                 feedback_loop: bool = False
                 ):

        n_amplifiers = len(phase_setting)
        self.phase = phase_setting

        # Create input & output queues, and amplifiers
        input_queue = Queue()
        self._queues = [input_queue]
        self._amplifiers = []
        for i in range(n_amplifiers):

            # Output queue, connecting with the first one if needed
            if feedback_loop is True and i == (n_amplifiers-1):
                output_queue = self._queues[0]
            else:
                output_queue = Queue()

            self._queues.append(output_queue)

            # Create amplifier
            amplifier = computer.intcode_computer(program=program,
                                                  input_queue=input_queue,
                                                  output_queue=output_queue
                                                  )
            self._amplifiers.append(amplifier)

            # Update input queue
            input_queue = output_queue

    def run_amplifiers(self, amplifier_input: int):

        # Set the phase settings of all the amplifiers
        n_amplifiers = len(self._amplifiers)
        for i in range(n_amplifiers):
            self._amplifiers[i].set_input(self.phase[i])

        # Set input for the first amplifier
        self._amplifiers[0].set_input(amplifier_input)

        # Run the amplifiers
        for i in range(n_amplifiers):
            self._amplifiers[i].run_program()

        # Wait until the last amplifier ends
        self._amplifiers[n_amplifiers-1].program_finished.wait()

        # Return the chain output
        return self._amplifiers[n_amplifiers-1].get_output()[0]


def highest_amplification_signal(program_path: str = None,
                                 program: str = None,
                                 root_path: str = 'data/raw',
                                 sequence_signals: List[int] = [0, 1, 2, 3, 4],
                                 feedback_loop: bool = False,
                                 ) -> int:
    """
    From an input program, it computes the optimal phase setting sequence
    which produces the maximum possible value for the thrusters signal.
    It returns a tuple whose first argument is the setting sequence and
    its second argument is the signal.
    """

    if program_path is not None:
        # Check the parameters
        path = os.path.join(root_path, program_path)
        if not os.path.exists(path):
            raise ValueError('Program not available at {}'.format(path))

        if program is not None:
            raise ValueError('WARNING: Using program from file')

        # Read the program
        f = open(path, 'r')
        program = f.read()

    elif program is None:
        raise ValueError('Provide some program!')

    program = list(map(int, program.split(',')))

    # Compute all possible phase settings
    n_amplifiers = len(sequence_signals)
    print('Testing {} phase settings'.format(math.factorial(n_amplifiers)))
    phases = itertools.permutations(sequence_signals)

    # Iterate over the phases
    max_output = -1
    max_phase = None
    for phs in phases:

        # Create and connect the amplifiers
        amplifiers = Amplifiers(phase_setting=phs,
                                program=program,
                                feedback_loop=feedback_loop)
        amp_output = amplifiers.run_amplifiers(0)

        # Check if it is higher than the current maximum
        if amp_output > max_output:
            max_output = amp_output
            max_phase = phs

    return (max_phase, max_output)
