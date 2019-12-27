from typing import List
import numpy as np
import os

def highest_amplification_signal(digits_path: str,
                                 n_rows: int,
                                 n_cols: int,
                                 root_path: str = 'data/raw'
                                 ) -> List[np.ndarray]:
    """
    From a file containing the digits of an image, it returns
    a list with the different layers. Each layer is represented
    as a numpy array. 
    """

    # Read the image file
    path = os.path.join(root_path, digits_path)
    f = open(path, 'r')
    digits = f.read()
    digits = digits.replace('\n', '')
    digits = list(map(int, list(digits)))

    # Split the digits into layers
    n = n_rows * n_cols
    layers = [digits[i:i + n] for i in range(0, len(digits), n)]

    # Reshape the images
    layers = [np.asarray(img) for img in layers]
    layers = [img.reshape(n_rows, n_cols) for img in layers]

    return layers


def check_corrupted_image(img: List[np.array]) -> int:
    """
    Returns the number to decide whether the image is corrupted:
    number of 1 digits multiplied by the number of 2 digits for
    the layer that contains the fewest 0 digits.
    """
    min_count = None
    min_zeros = np.infty

    # Loop over the layers of the image
    for layer in img:
        unique, counts = np.unique(layer, return_counts=True)
        digit_count = dict(zip(unique, counts))
        
        # Check if it is the minimm
        if 0 in digit_count.keys() and digit_count[0] < min_zeros:
            min_zeros = digit_count[0]
            min_count = digit_count

    # Check the selecte layer
    if 1 not in min_count.keys() or 2 not in min_count.keys():
        raise ValueError('Corrupted image!')

    # Return the check number
    return min_count[1] * min_count[2]