from typing import List


class intcode_computer(object):

    def __init__(self,
                 program: List[int]
                 ):
        self.memory = program.copy()
        self.pointer = 0
        self.execution_finished = False

        # Dictionary of method to apply depending on the code
        self.instruction_appliers = {'01': self._sum,
                                     '02': self._multiply,
                                     '03': self._input,
                                     '04': self._output,
                                     '05': self._jump_if_true,
                                     '06': self._jump_if_false,
                                     '07': self._less_than,
                                     '08': self._equals,
                                     '99': self._finish
                                     }

    def run_program(self, program_input: int = None):
        """
        Runs the program using the specified input
        """

        while self.execution_finished is False and self.pointer < len(self.memory):

            # Read instruction code
            opcode = str(self.memory[self.pointer])
            op = opcode[-2:]
            modes = opcode[:-2]

            if len(op) == 1:
                op = '0'+op

            # Call the corresponding method
            method = self.instruction_appliers[op]
            method(modes=modes, program_input=program_input)

        if self.execution_finished is False:
            raise ValueError('Execution finished without ending opcode!')

        # Restart the pointer for next execution
        self.pointer = 0

    def _read_parameters(self,
                         modes: str,
                         n_params: int
                         ) -> List[int]:
        """Reads the parameters of a method using their mode.
        The modes parameter is the string opcode without the
        two last digits of the operation identifier.
        """

        modes = modes[::-1]  # Reverse it
        params = []

        for i in range(n_params):
            mode = int(modes[i]) if i < len(modes) else 0

            if mode == 0:
                position = self.memory[self.pointer + 1 + i]
                params.append(self.memory[position])
            else:
                params.append(self.memory[self.pointer + 1 + i])

        return params

    def _sum(self, modes: str, n_params: int = 2, **kwargs):
        # Read the method parameters
        params = self._read_parameters(modes, n_params)

        # Get the storing possition
        pos = self.memory[self.pointer+3]

        # Apply the method
        self.memory[pos] = params[0] + params[1]

        # Increate the pointer
        self.pointer += 4

    def _multiply(self, modes: str, n_params: int = 2, **kwargs):
        # Read the method parameters
        params = self._read_parameters(modes, n_params)

        # Get the storing possition
        pos = self.memory[self.pointer+3]

        # Apply the method
        self.memory[pos] = params[0] * params[1]

        # Increate the pointer
        self.pointer += 4

    def _input(self, program_input: int, **kwargs):
        if program_input is None:
            raise ValueError('No input provided!')

        # Get the storing possition
        pos = self.memory[self.pointer+1]

        # Store the input value
        self.memory[pos] = program_input

        # Increate the pointer
        self.pointer += 2

    def _output(self, modes: str, n_params: int = 1, **kwargs):
        # Read the method parameters
        params = self._read_parameters(modes, n_params)

        # Output the value
        print(params[0])

        # Increate the pointer
        self.pointer += 2

    def _jump_if_true(self, modes: str, n_params: int = 2, **kwargs):
        # Read the method parameters
        params = self._read_parameters(modes, n_params)

        if params[0] != 0:
            self.pointer = params[1]
        else:
            self.pointer += 3

    def _jump_if_false(self, modes: str, n_params: int = 2, **kwargs):
        # Read the method parameters
        params = self._read_parameters(modes, n_params)

        if params[0] == 0:
            self.pointer = params[1]
        else:
            self.pointer += 3

    def _less_than(self, modes: str, n_params: int = 2, **kwargs):
        # Read the method parameters
        params = self._read_parameters(modes, n_params)

        # Get the storing possition
        pos = self.memory[self.pointer+3]

        # Apply the method
        self.memory[pos] = 1 if params[0] < params[1] else 0

        # Increate the pointer
        self.pointer += 4

    def _equals(self, modes: str, n_params: int = 2, **kwargs):
        # Read the method parameters
        params = self._read_parameters(modes, n_params)

        # Get the storing possition
        pos = self.memory[self.pointer+3]

        # Apply the method
        self.memory[pos] = 1 if params[0] == params[1] else 0

        # Increate the pointer
        self.pointer += 4

    def _finish(self, **kwargs):
        self.execution_finished = True
