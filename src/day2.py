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
            raise ValueError('Something went wrong! Invalid opcode: {}'.format(opcode))

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

        i = i + 4 # Jump to next opcode
            
    raise ValueError('Execution finished without ending opcode!')
