from typing import List
from queue import Queue
import threading


class intcode_computer(object):

    def start_computer(self, program: List[int] = None):
        """
        Starts the computer to run a program
        """
        self.pointer = 0
        self.relative_base = 0
        self.execution_finished = False

        program = self.program if program is None else program
        self.memory = dict(zip(list(range(len(program))), program))

    def __init__(self,
                 program: List[int],
                 input_queue: List[int] = None,
                 output_queue: List[int] = None,
                 test_mode: bool = False,
                 wait_execution: bool = True
                 ):

        # Check the parameters
        if not isinstance(program, List) or not all([isinstance(i, int) for i in program]):
            raise ValueError('Program must be a list of integers!')

        # Computer parameters
        self.start_computer(program)
        self.test_mode = test_mode
        self.wait_execution = wait_execution

        # Program info
        self.program = program
        self.input_queue = Queue() if input_queue is None else input_queue
        self.output_queue = Queue() if output_queue is None else output_queue

        # Dictionary of method to apply depending on the code
        self.instruction_info = {'01': (self._sum, 2),
                                 '02': (self._multiply, 2),
                                 '03': (self._input, 0),
                                 '04': (self._output, 1),
                                 '05': (self._jump_if_true, 2),
                                 '06': (self._jump_if_false, 2),
                                 '07': (self._less_than, 2),
                                 '08': (self._equals, 2),
                                 '09': (self._update_base, 1),
                                 '99': (self._finish, 0)
                                 }

    def set_input(self, input):
        self.input_queue.put(input)

    def get_output(self):
        output_list = []
        while not self.output_queue.empty():
            output_list.append(self.output_queue.get())
        return output_list

    def run_program(self):
        """
        Runs the program
        """
        # Run the program
        self.thread = threading.Thread(target=self._run_program)
        self.thread.start()
        
        # Wait for it to finish
        if self.wait_execution is True:
            self.thread.join()

    def _format_modes(self, modes: str, n_params: int) -> List[int]:
        """
        Gets the modes of the parameters from the original code
        """
        modes = modes[::-1]  # Reverse it
        modes = list(map(int, modes))
        if len(modes) < n_params:
            modes = modes + [0]*(n_params-len(modes))
        return(modes)

    def _run_program(self):
        """
        Private method to run the program in a thread 
        """
        while self.execution_finished is False and self.pointer < len(self.memory):

            # Read instruction code
            opcode = str(self.memory[self.pointer])
            op = opcode[-2:]
            if len(op) == 1:
                op = '0'+op

            # Get the method info
            method_info = self.instruction_info[op]

            # Format modes
            modes = self._format_modes(modes=opcode[:-2],
                                       n_params=method_info[1]+1)

            if self.test_mode is True:
                print('Pointer {p}, code {c}, modes {m}'.format(
                    p=self.pointer, c=op, m=modes))

            # Call the corresponding method
            method = method_info[0]
            method(modes=modes, n_params=method_info[1])

        if self.execution_finished is False:
            raise ValueError('Execution finished without ending opcode!')


    def _get_position(self, mode: int, pointer_offset: int = 0):
        """
        Get the memory position from where the paramter has to be read,
        depending on the mode.
        """
        if mode == 0:
            return self.memory[self.pointer + 1 + pointer_offset]
        elif mode == 2:
            offset = self.memory[self.pointer + 1 + pointer_offset]
            return self.relative_base + offset
        raise ValueError('Invalid mode for position of the parameter!')

    def _read_parameters(self,
                         modes: List[int],
                         n_params: int
                         ) -> List[int]:
        """
        Reads the parameters of a method using their mode.
        The modes parameter is the string opcode without the
        two last digits of the operation identifier.
        """

        params = []

        for i in range(n_params):
            mode = modes[i]

            if mode == 0 or mode == 2:
                # Position mode or relative mode
                position = self._get_position(mode, pointer_offset=i)
                params.append(self.memory.get(position, 0))

            elif mode == 1:
                # Inmediate mode
                params.append(self.memory[self.pointer + 1 + i])

            else:
                raise ValueError('Invalid mode!')

        return params

    def _sum(self, modes: List[int], n_params: int = 2, **kwargs):
        # Read the method parameters
        params = self._read_parameters(modes, n_params)

        # Get the storing possition
        pos = self._get_position(modes[-1], pointer_offset=n_params)

        # Apply the method
        self.memory[pos] = params[0] + params[1]

        # Increate the pointer
        self.pointer += 4

    def _multiply(self, modes: List[int], n_params: int = 2, **kwargs):
        # Read the method parameters
        params = self._read_parameters(modes, n_params)

        # Get the storing possition
        pos = self._get_position(modes[-1], pointer_offset=n_params)

        # Apply the method
        self.memory[pos] = params[0] * params[1]

        # Increate the pointer
        self.pointer += 4

    def _input(self, modes: List[int], **kwargs):
        # Get the storing possition
        pos = self._get_position(modes[-1])

        # Store the input value
        self.memory[pos] = self.input_queue.get()
        self.input_queue.task_done()

        # Increate the pointer
        self.pointer += 2

    def _output(self, modes: List[int], n_params: int = 1, **kwargs):
        # Read the method parameters
        params = self._read_parameters(modes, n_params)

        # Add output value to the queue
        self.output_queue.put(params[0])

        # Increate the pointer
        self.pointer += 2

    def _jump_if_true(self, modes: List[int], n_params: int = 2, **kwargs):
        # Read the method parameters
        params = self._read_parameters(modes, n_params)

        if params[0] != 0:
            self.pointer = params[1]
        else:
            self.pointer += 3

    def _jump_if_false(self, modes: List[int], n_params: int = 2, **kwargs):
        # Read the method parameters
        params = self._read_parameters(modes, n_params)

        if params[0] == 0:
            self.pointer = params[1]
        else:
            self.pointer += 3

    def _less_than(self, modes: List[int], n_params: int = 2, **kwargs):
        # Read the method parameters
        params = self._read_parameters(modes, n_params)

        # Get the storing possition
        pos = self._get_position(modes[-1], pointer_offset=n_params)

        # Apply the method
        self.memory[pos] = 1 if params[0] < params[1] else 0

        # Increate the pointer
        self.pointer += 4

    def _equals(self, modes: List[int], n_params: int = 2, **kwargs):
        # Read the method parameters
        params = self._read_parameters(modes, n_params)

        # Get the storing possition
        pos = self._get_position(modes[-1], pointer_offset=n_params)

        # Apply the method
        self.memory[pos] = 1 if params[0] == params[1] else 0

        # Increate the pointer
        self.pointer += 4

    def _update_base(self, modes: List[int], n_params: int = 1, **kwargs):
        # Read the method parameters
        params = self._read_parameters(modes, n_params)

        # Adjust the relative base value
        self.relative_base += params[0]

        # Increate the pointer
        self.pointer += 2

    def _finish(self, **kwargs):
        self.execution_finished = True
