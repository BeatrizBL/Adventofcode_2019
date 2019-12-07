from typing import List


def intcode_computer(program: List[int],
                     sum_code: int = 1,
                     multiply_code: int = 2,
                     finish_code: int = 99
                     ) -> List[int]:
    """
    An Intcode program is a list of integers separated by commas (like 1,0,0,3,99). 
    To run one, start by looking at the first integer. Here, you will find an opcode,
    either 1, 2, or 99. 

    The opcode indicates what to do:

    - Opcode 99 means that the program is finished and should immediately halt.

    - Opcode 1 adds together numbers read from two positions and stores the result in a 
      third position. The three integers immediately after the opcode tell you these 
      three positions - the first two indicate the positions from which you should read 
      the input values, and the third indicates the position at which the output should 
      be stored.

    - Opcode 2 works exactly like opcode 1, except it multiplies the two inputs instead 
      of adding them. 
    """
    output = program.copy()

    # Go down the program
    i = 0
    while i < len(output):
        opcode = output[i]

        # Check opcode
        if opcode not in [sum_code, multiply_code, finish_code]:
            raise ValueError(
                'Something went wrong! Invalid opcode: {}'.format(opcode))

        # Finish execution
        if opcode == finish_code:
            return output

        pos1 = output[i+1]
        pos2 = output[i+2]
        pos_store = output[i+3]

        # Sum
        if opcode == sum_code:
            output[pos_store] = output[pos1] + output[pos2]

        # Multiply
        if opcode == multiply_code:
            output[pos_store] = output[pos1] * output[pos2]

        i = i + 4  # Jump to next opcode

    raise ValueError('Execution finished without ending opcode!')


def binary_search_code(program: List[int],
                       code: int,
                       verb_pos: int = 2,
                       value_range: tuple = (0,99)
                       ) -> int:
    """
    Iterative implementation of binary search.
    It returns the value between 0 and 99 for the "verb" that generates 
    the desired error code for the given program.
    If it can't find it, returns -1.
    """

    # Initialize the values
    program = program.copy()
    left = value_range[0]
    right = value_range[1]

    # Binary search
    while left <= right:
        mid = int(left + (right - left)/2)

        program[verb_pos] = mid
        output = intcode_computer(program)
        value = output[0]

        # Check if the value is at mid
        if code == value:
            return mid

        # If the value is greater, ignore left half
        elif value < code:
            left = mid + 1

        # If the value is smaller, ignore right half
        else:
            right = mid - 1

    # If the error code can't be obtained
    return -1


def get_error_code(output: int,
                   program: List[int]
                   ) -> int:
    """
    Determine what pair of inputs, "noun" and "verb", produces the output.
    The inputs should be provided to the program by replacing the values 
    at addresses 1 and 2. The value placed in address 1 is called the "noun", 
    and the value placed in address 2 is called the "verb".
    It returns the error code: 100 * noun + verb

    Implementation options:
        - By brute force, looping twice over 0-99
        - Looping over the noun linearly, and using binary search for the verb,
          since all the values of the program are integers, and therefore
          positive (IMPLEMENTED)
        - Optimize the possible value intervals for both noun and verb checking
          the possible min and max outputs for each pair
    """

    # Reset the memory
    program = program.copy()

    # Linear loop over the noun
    for noun in range(0, 100):
        program[1] = noun

        # Binary search over the verb
        verb = binary_search_code(program, output)

        # Return the code if found
        if verb != -1:
            return (100 * noun + verb)

    raise ValueError('Code not found!')
