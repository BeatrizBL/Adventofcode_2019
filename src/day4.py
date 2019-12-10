

def count_passwords(interval: tuple,
                    n_digits: int = 6
                    ) -> int:
    """
    Checks, by brute force, how many numbers in the interval fulfil 
    the password requirements.
    """
    lower = interval[0]
    upper = interval[1]

    # Check limits are 6 digit numbers
    if len(str(lower)) > n_digits or len(str(upper)) < n_digits:
        print('No {} digits numbers in that interval!'.format(n_digits))
        return 0

    if len(str(lower)) < n_digits:
        lower = int('1'*n_digits)
        print('Lower limit less than {n} digits! Using {l}'.format(
            n=n_digits, l=lower))

    if len(str(upper)) > 6:
        upper = int('9'*n_digits)
        print('Upper limit bigger than {n} digits! Using {u}'.format(
            n=n_digits, u=upper))

    # Check all numbers in the interval
    n = 0
    for num in range(lower, upper+1):
        num_str = str(num)

        # No decreasing numbers
        non_dec = all([num_str[i] <= num_str[i+1]
                       for i in range(len(num_str)-1)])

        # Consecutive numbers
        consec = any([num_str[i] == num_str[i+1]
                      for i in range(len(num_str)-1)])

        if non_dec and consec:
            n = n+1

    return n


def count_passwords_part2(interval: tuple,
                          n_digits: int = 6
                          ) -> int:
    """
    Checks, by brute force, how many numbers in the interval fulfil 
    the password requirements.
    """
    lower = interval[0]
    upper = interval[1]

    # Check limits are 6 digit numbers
    if len(str(lower)) > n_digits or len(str(upper)) < n_digits:
        print('No {} digits numbers in that interval!'.format(n_digits))
        return 0

    if len(str(lower)) < n_digits:
        lower = int('1'*n_digits)
        print('Lower limit less than {n} digits! Using {l}'.format(
            n=n_digits, l=lower))

    if len(str(upper)) > 6:
        upper = int('9'*n_digits)
        print('Upper limit bigger than {n} digits! Using {u}'.format(
            n=n_digits, u=upper))

    # Check all numbers in the interval
    n = 0
    for num in range(lower, upper+1):

        # Split digits into a list
        num_str = str(num)
        num_list = [int(num_str[i]) for i in range(len(num_str))]

        # Get difference of consecutive numbers
        num_diff = [j-i for i, j in zip(num_list[:-1], num_list[1:])]

        # No decreasing numbers
        if all([i >= 0 for i in num_diff]):

            # Mark jumps as 1's
            jumps = [(1 if i > 0 else 0) for i in num_diff]

            if (jumps[0] == 0 and jumps[1] == 1):
                # 2 consecutive digits at the beginning
                n = n+1
            elif (jumps[-2] == 1 and jumps[-1] == 0):
                # 2 consecutive digits at the end
                n = n+1
            elif '101' in ''.join(map(str, jumps)):
                # 2 consecutive digits in the middle
                n = n+1

    return n
