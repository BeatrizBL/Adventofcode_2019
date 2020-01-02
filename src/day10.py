from typing import List
from queue import Queue
import numpy as np
import pandas as pd
import math
import os

import ipywidgets as widgets
from ipywidgets import interact
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


def _find_inline_asteroids(asteroids_map: np.ndarray,
                           pos: tuple,
                           asteroid: tuple,
                           one_side: bool = False
                           ) -> List[tuple]:

    x, y = asteroid

    # Posible positions
    x_positions = list(range(asteroids_map.shape[0]))
    y_positions = list(range(asteroids_map.shape[1]))

    # Just one side of the line
    if one_side is True:
        if pos[0] != x:
            # Non vertical line
            if pos[0] > x:
                x_positions = [
                    a for a in x_positions if a < pos[0]]  # Pos right
            else:
                x_positions = [
                    a for a in x_positions if a > pos[0]]  # Pos left
        else:
            # Vertical line
            if pos[1] > y:
                y_positions = [
                    b for b in y_positions if b < pos[1]]  # Pos down
            else:
                y_positions = [b for b in y_positions if b > pos[1]]  # Pos up

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
    return([p for p in values if asteroids_map[p[0], p[1]] > 0])


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

    # Get list of unchecked asteroids
    unchecked = list(zip(*np.where(asteroids_map == 1)))

    while len(unchecked) > 0:
        asteroid = unchecked[0]

        # Compute the positions in the same line
        inline_asteroids = _find_inline_asteroids(asteroids_map,
                                                  pos, asteroid)

        # Keep just the two closest asteroids
        closest_asteroids = _find_close(inline_asteroids, pos)
        for asteroid in inline_asteroids:
            unchecked.remove(asteroid)
            if asteroid not in closest_asteroids:
                asteroids_map[asteroid[0], asteroid[1]] = 0

    return asteroids_map


def plot_asteroid_map(asteroids_map: np.ndarray,
                      visible_asteroids: np.ndarray,
                      optimal_point: tuple,
                      legend_visible: bool = True,
                      xlims: tuple = None,
                      ylims: tuple = None
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
                              sorting=['Optimal', 'Visible', 'Non visible'],
                              legend_visible=legend_visible,
                              xlims=xlims,
                              ylims=ylims
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

    return (max_position, max_visible)


def build_angle_structure(asteroids_map: np.ndarray,
                          location: tuple
                          ) -> dict:
    """
    Creates a dictionary structure to store the asteroids aligned in a 
    given angle, when comparing with the vertical line from the provided
    location.
    """

    # Get list of unchecked asteroids
    unchecked = list(zip(*np.where(asteroids_map == 1)))
    unchecked.remove(location)
    angles = {}

    while len(unchecked) > 0:
        asteroid = unchecked[0]

        # Find other asteroids in the same direction
        aligned = _find_inline_asteroids(asteroids_map,
                                         location, asteroid,
                                         one_side=True)

        # Sort them by distance
        ds = [(location[0]-a)**2+(location[1]-b)**2 for a, b in aligned]
        aligned_sorted = [aligned[ix] for ix in np.argsort(ds)]

        # Compute the angle to the vertical
        v = (asteroid[0]-location[0], asteroid[1]-location[1])
        dot_product = sum((a*b) for a, b in zip(v, (0, -1)))
        norm = math.sqrt(sum((a*b) for a, b in zip(v, v)))
        angle = round(math.degrees(math.acos(dot_product / norm)), 2)
        if asteroid[0] < location[0]:
            angle = 360 - angle

        # Store the asteroids
        angles[angle] = aligned_sorted
        [unchecked.remove(ast) for ast in aligned]

    return angles


def vaporize_asteroids(asteroids_map: np.ndarray,
                       location: tuple,
                       n_asteroids: int = None
                       ) -> List[tuple]:
    """
    Computes the vaporized asteroids until a desired number. That is,
    the first visible asteroid each round when rotating from the up
    vertical position.
    Returns a list of the asteroids in order.
    """

    # Final number of asteroids to vaporize
    total = asteroids_map.sum() - 1
    if n_asteroids is None or n_asteroids > total:
        n_asteroids = total

    # Get angles
    angles = build_angle_structure(asteroids_map, location)
    rotation_angles = sorted(list(angles.keys()))
    rotation = Queue()
    [rotation.put(a) for a in rotation_angles]

    vaporized = []
    for i in range(n_asteroids):
        angle = rotation.get()
        asteroids = angles[angle]
        vaporized.append(asteroids[0])

        # If there are more asteroids, add the angle back
        if len(asteroids) > 1:
            angles[angle] = asteroids[1:]
            rotation.put(angle)
        else:
            angles[angle] = []

    return vaporized


def animated_vaporization(asteroids_map: np.ndarray,
                          location: tuple,
                          vaporized: List[tuple]):
    """
    Returns an interactive plot highlighting and removing the
    vaporized asteroids in order.
    """

    asteroids_map = asteroids_map.copy()

    def demo(i):
        asteroid = vaporized[i]
        fire = np.zeros(asteroids_map.shape)
        fire[asteroid[0], asteroid[1]] = 1
        chart = plot_asteroid_map(asteroids_map,
                                  visible_asteroids=fire,
                                  optimal_point=location,
                                  legend_visible=False,
                                  xlims=(0, asteroids_map.shape[0]-1),
                                  ylims=(-asteroids_map.shape[1]+1, 0),
                                  )
        asteroids_map[asteroid[0], asteroid[1]] = 0
        return chart

    return interact(demo, i=widgets.Play(value=0,
                                         min=0,
                                         max=(len(vaporized)-1),
                                         step=1,
                                         ))
