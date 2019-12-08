from typing import List
import pandas as pd
from scipy import sparse as sp
import streamlit as st


def get_panel_dimension(path: List[str]) -> int:
    """
    Gets the maximum number of steps the wire takes in any
    of the four directions.
    """

    def _sum_steps(direction) -> int:
        steps = [int(s[1:]) for s in path if s[0] == direction]
        return sum(steps)

    right = _sum_steps('R')
    left = _sum_steps('L')
    up = _sum_steps('U')
    down = _sum_steps('D')

    return max(right, left, up, down)


def check_point_in_interval(start: tuple,
                            end: tuple,
                            points: pd.DataFrame = None
                            ) -> pd.DataFrame:

    if points is None:
        return None

    if start[0] == end[0]:

        # Vertical segment
        points = points[points['x'] == start[0]]
        lower = min(start[1], end[1])
        upper = max(start[1], end[1])
        points = points[(points['y'] >= lower) & (points['y'] <= upper)]

        points['dist_to_start'] = (points['y'] - start[1]).abs()

    elif start[1] == end[1]:

        # Horizontal segment
        points = points[points['y'] == start[1]]
        left = min(start[0], end[0])
        right = max(start[0], end[0])
        points = points[(points['x'] >= left) & (points['x'] <= right)]

        points['dist_to_start'] = (points['x'] - start[0]).abs()

    else:
        return None

    # Sort the points depending on the distance to the starting point
    points = points.sort_values('dist_to_start')

    return points.drop(columns='dist_to_start')


def get_wire_path(path: List[str],
                  size_x: int,
                  size_y: int,
                  central_port: tuple,
                  central_port_id: int = 2,
                  mark_points: pd.DataFrame = None
                  ) -> dict:
    """
    Computes a matrix with the given dimensions for which:
    - The central port is marked as central_port_id
    - The path of the wire is marked as 1's
    - The rest are 0's

    The list of mark_points is used to insert those points
    into the turn_points dataframe, although there was no
    turn. It is used for Part 2.
    The mark_points dataframe has two columns, x and y.

    Note: If there are any knots in the path, they are still
    marked as 1's

    Return:
    A dictionary containing:
    - matrix: int matrix with the path (to compute the distance)
    - turn_points: dataframe contining the turning points, with
      columns x and y (for visualization)
    """

    # Initialize the matrix and the dataframe
    matrix = sp.lil_matrix((size_x, size_y), dtype='uint8')
    turn_points = pd.DataFrame({'x': [central_port[0]],
                                'y': [central_port[1]]})

    # Write 1's in the path
    start = central_port
    for step in path:
        direction = step[0]
        n = int(step[1:])

        # Find the ending point
        if direction == 'U':
            end = (start[0], start[1] + n)
        elif direction == 'D':
            end = (start[0], start[1] - n)
        elif direction == 'R':
            end = (start[0] + n, start[1])
        elif direction == 'L':
            end = (start[0] - n, start[1])
        else:
            raise ValueError('Invalid path!')

        # Check if a mark_point is in the path
        point = check_point_in_interval(start, end, mark_points)
        if point is not None:
            turn_points = pd.concat([turn_points, point])

        # Mark the path
        step_x = list(range(min(start[0], end[0]),
                            max(start[0], end[0])+1))
        step_y = list(range(min(start[1], end[1]),
                            max(start[1], end[1])+1))
        for x in step_x:
            matrix[x, step_y] = 1

        # Move to the next point
        point = pd.DataFrame({'x': [end[0]], 'y': [end[1]]})
        turn_points = pd.concat([turn_points, point])
        start = end

    # Mark the central port
    matrix[central_port[0], central_port[1]] = central_port_id

    turn_points = turn_points.reset_index(drop=True)
    return {'matrix': matrix, 'turn_points': turn_points}


def get_minimum_Manhattan(matrix,
                          knot_id: int
                          ) -> dict:
    """
    Computes the Manhattan distance of the wire knots to the
    central port. The knots are marked in the matrix with the
    knot_id, and the central port is assumed to have a higher
    value than the knots.

    Return:
    A dictionary containing:
    - position: tuple with the position of the closest knot
    - distance: minimum Manhattan distance
    """

    # Get the crossing points
    knots = sp.find(matrix == knot_id)
    df_knots = pd.DataFrame({'x': knots[0], 'y': knots[1]})

    # Get the central port
    pos = sp.find(matrix > knot_id)
    central_port = (pos[0][0], pos[1][0])

    # Compute Manhattan distance
    df_knots['dis_x'] = (df_knots['x']-central_port[0]).apply(abs)
    df_knots['dis_y'] = (df_knots['y']-central_port[1]).apply(abs)
    df_knots['dis'] = df_knots['dis_x'] + df_knots['dis_y']

    # Return position and distance
    idx = df_knots['dis'].idxmin()
    knot = (df_knots.loc[idx]['x'], df_knots.loc[idx]['y'])
    dis = df_knots.loc[idx]['dis']

    return {'position': knot, 'distance': dis}


def get_minimum_combined_steps(paths: List[List[str]],
                               size_x: int,
                               size_y: int,
                               central_port: tuple,
                               matrix,
                               knot_id: int
                               ) -> dict:
    """
    Computes the sum of combined steps from the central port to
    the wire knots. The knots are marked in the matrix with the
    knot_id, and the central port is assumed to have a higher
    value than the knots.

    Return:
    A dictionary containing:
    - position: tuple with the position of the closest knot
    - distance: minimum sum of combined steps
    """

    # Get the crossing points
    knots = sp.find(matrix == knot_id)
    df_knots_part1 = pd.DataFrame({'x': knots[0], 'y': knots[1]})

    # Get the dataframes of the turning points + knots
    df_list = []
    i = 1

    for path in paths:    
        res = get_wire_path(path,
                            size_x,
                            size_y,
                            central_port,
                            mark_points=df_knots_part1)
        points = res['turn_points']

        # Merge with knots dataframe
        df_knots = df_knots_part1.copy()
        df_knots['knot'] = 1
        df = pd.merge(points, df_knots, how='left')
        df = df.fillna(0)
        df['knot'] = df['knot'].astype(int)

        # Compute length of steps
        df['x_length'] = df['x'].diff().abs()
        df['x_cum'] = df['x_length'].cumsum()

        df['y_length'] = df['y'].diff().abs()
        df['y_cum'] = df['y_length'].cumsum()
        
        df['steps'+str(i)] = df['x_cum'] + df['y_cum']

        # Filter the dataset
        df = df[df['knot']==1]
        df = df[['x', 'y', 'steps'+str(i)]]
        df_list.append(df)
        i = i+1

    # Merge the datasets for the diferent wires
    df_wires = None
    for df in df_list:
        if df_wires is None:
            df_wires = df.copy()
        else:
            df_wires = pd.merge(df, df_wires, on=['x','y'])

    # Compute combined sum
    step_cols = [c for c in df_wires.columns if c not in ['x', 'y']]
    df_wires['combined'] = df_wires[step_cols].apply(sum, axis=1)

    # Return position and distance
    idx = df_wires['combined'].idxmin()
    knot = (df_wires.loc[idx]['x'], df_wires.loc[idx]['y'])
    dis = int(df_wires.loc[idx]['combined'])

    return {'position': knot, 'distance': dis}