from src import computer
from typing import List
import itertools
import math
import os


def highest_amplification_signal(program_path: str = None,
                                 program: str = None,
                                 root_path: str = 'data/raw',
                                 sequence_signals: List[int] = [0, 1, 2, 3, 4],
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

        # Input for the first amplifier
        amp_input = 0

        # Iterate over the amplifiers chain
        for i in range(n_amplifiers):
            p = phs[i]
            amp = computer.intcode_computer(program,
                                            program_input=[p, amp_input])
            amp_output = amp.run_program()
            amp_input = amp_output

        # Check if it is higher than the current maximum
        if amp_output > max_output:
            max_output = amp_output
            max_phase = phs

    return (max_phase, max_output)
