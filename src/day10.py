from typing import List
import numpy as np
import pandas as pd
import os

from src.visualization import altair_plots


def read_asteroid_map(map_path: str,
                      root_path: str = 'data/raw',
                      ) -> np.ndarray:
    """
    Reads a file containing an asteroids map and returns a zero
    matrix with ones in asteroid positions.
    """

    # Check the parameters
    path = os.path.join(root_path, map_path)
    if not os.path.exists(path):
        raise ValueError('Map not available at {}'.format(path))

    # Read the program
    f = open(path, 'r')
    asteroids = f.read()
    asteroids = asteroids.split('\n')

    # Process the string
    asteroid_map = []
    for row in asteroids:
        if len(row) > 0:
            asteroid_map.append([(1 if i == '#' else 0) for i in row])

    return(np.array(asteroid_map).transpose())


def _find_close(inline: List[tuple],
                point: tuple
                ) -> List[tuple]:
    """
    Find the closest asteroids to the given point in the same line
    """

    # Base cases
    if len(inline) == 0:
        return([])
    if len(inline) == 1:
        return(inline)

    # Divide the two sides of the line
    if inline[0][0] == point[0]:
        # Vertical line: up and down sides
        side1 = [p for p in inline if p[1] > point[1]]
        side2 = [p for p in inline if p[1] < point[1]]
    else:
        # Non vertical line: left and right sides
        side1 = [p for p in inline if p[0] > point[0]]
        side2 = [p for p in inline if p[0] < point[0]]

    # Keep closest asteroids
    closest = []
    for side in [side1, side2]:
        if len(side) == 1:
            closest.extend(side)
        elif len(side) > 1:
            # Compute the Euclidean distances
            ds = [(point[0]-a)**2+(point[1]-b)**2 for a, b in side]
            closest.append(side[ds.index(min(ds))])

    return closest


def mark_visible_asteroids(asteroids_map: np.ndarray,
                           pos: tuple
                           ) -> np.ndarray:
    """
    Returns a matrix with 1's at the positions of the visible
    asteroids from the provided position.
    """

    # Copy map to contain visible asteroids
    asteroids_map = asteroids_map.copy()
    asteroids_map[pos[0], pos[1]] = 0

    # Posible positions
    x_positions = list(range(asteroids_map.shape[0]))
    y_positions = list(range(asteroids_map.shape[1]))

    # Get list of unchecked asteroids
    unchecked = list(zip(*np.where(asteroids_map == 1)))

    while len(unchecked)>0:
        x,y = unchecked[0]

        # Compute the positions in the same line
        def line(pos_x): return y + (pos_x-x)*(pos[1]-y)/(pos[0]-x)
        if pos[0] != x:
            values = [(a, int(line(a)))
                      for a in x_positions if line(a).is_integer()]
        else:
            values = [(x, b) for b in y_positions]

        # Remove positions out of the bounds
        values = [p for p in values if p[1] >=
                  0 and p[1] < asteroids_map.shape[1]]

        # Filter to asteroids in those positions
        inline_asteroids = [
            p for p in values if asteroids_map[p[0], p[1]] > 0]

        # Keep just the two closest asteroids
        closest_asteroids = _find_close(inline_asteroids, pos)
        for asteroid in inline_asteroids:
            unchecked.remove(asteroid)
            if asteroid not in closest_asteroids:
                asteroids_map[asteroid[0], asteroid[1]] = 0

    return asteroids_map


def plot_asteroid_map(asteroids_map: np.ndarray,
                      visible_asteroids: np.ndarray,
                      optimal_point: tuple
                      ):
    """
    Plot an asteroid map, marking the visible and non-visible ones
    from the optimal position
    """
    # Lists of tuples
    asteroids = list(zip(*np.where(asteroids_map == 1)))
    positions = list(zip(*np.where(visible_asteroids == 1)))

    # Create the dataframe
    def value_point(p): return 'Visible' if p in positions else (
        'Optimal' if p == optimal_point else 'Non visible')
    values = [value_point(p) for p in asteroids]
    df = pd.DataFrame({'x': [p[0] for p in asteroids],
                       'y': [-p[1] for p in asteroids],
                       'value': values})

    # Plot
    altair_plots.scatter_plot(df,
                              sorting=['Optimal', 'Visible', 'Non visible']
                              ).display()


def count_optimal_detected(asteroids_map: np.ndarray) -> int:
    """
    Finds the asteroid from where the maximum number of other asteroids
    are detected. Plots the map marking the visible asteroids along with 
    the optimal position, and returns the number of detected asteroids.
    """

    # Variables to store the optimal values
    max_visible = 0
    max_position = None
    visible_asteroids = None

    # Find optimal asteroid
    for x in range(asteroids_map.shape[0]):
        for y in range(asteroids_map.shape[1]):
            if asteroids_map[x, y] > 0:

                visible = mark_visible_asteroids(asteroids_map, (x, y))

                if visible.sum() > max_visible:
                    max_visible = visible.sum()
                    max_position = (x, y)
                    visible_asteroids = visible.copy()

    # Plot the asteroid map
    plot_asteroid_map(asteroids_map, visible_asteroids, max_position)

    return max_visible
