from typing import List
import pandas as pd
import numpy as np

import matplotlib.pyplot as plt
import matplotlib.animation
import matplotlib.cm as cm
from mpl_toolkits.mplot3d import Axes3D

#################################################################
# PART 1                                                        #
# Inefficient implementation based on DataFrame transformations #
#################################################################

def update_velocity(positions: pd.DataFrame,
                    velocities: pd.DataFrame
                    ) -> pd.DataFrame:
    """
    Update velocity by applying gravity of the current positions
    """

    velocities = velocities.copy()

    for i in range(len(positions)):
        # Compute gravity
        gravity_pos = (positions.drop(i) > positions.iloc[i]).astype(int)
        gravity_neg = -1*(positions.drop(i) < positions.iloc[i]).astype(int)
        gravity = (gravity_pos + gravity_neg).sum()

        # Apply gravity
        velocities.iloc[i] = velocities.iloc[i]+gravity

    return velocities


def total_energy(positions: pd.DataFrame,
                 velocities: pd.DataFrame
                 ) -> int:
    """
    Computes the total energy of the system for a given position
    """
    pot = positions.abs().sum(axis=1)
    kin = velocities.abs().sum(axis=1)
    return sum(pot*kin)


def compute_system_energy(positions: pd.DataFrame,
                          steps: int = 10
                          ) -> int:
    """
    Computes the total energy of the system after the required
    number of steps
    """

    velocities = pd.DataFrame({'x': [0]*len(positions),
                               'y': [0]*len(positions),
                               'z': [0]*len(positions)})

    for i in range(steps):

        # Apply gravity
        velocities = update_velocity(positions, velocities)

        # Apply velocity
        positions = positions + velocities

    return total_energy(positions, velocities)


def animate_system(positions: pd.DataFrame,
                   steps: int = 10,
                   size: int = 100
                   ) -> int:
    """
    Creates an interactive plot to visualize the positions of the
    moons at each step
    """

    velocities = pd.DataFrame({'x': [0]*len(positions),
                               'y': [0]*len(positions),
                               'z': [0]*len(positions)})

    # Create empty plot
    fig = plt.figure(figsize=(7, 7))
    ax = fig.add_subplot(111, projection='3d')
    x, y, z = [], [], []
    colors = cm.copper(4)
    sc = ax.scatter(x, y, z, s=size)

    # Compute all positions
    step_pos = []

    for i in range(steps):

        # Apply gravity
        velocities = update_velocity(positions, velocities)

        # Apply velocity
        positions = positions + velocities

        step_pos.append(positions)

    # Set plot limits
    allx = [i for sl in [list(p['x']) for p in step_pos] for i in sl]
    ally = [i for sl in [list(p['y']) for p in step_pos] for i in sl]
    allz = [i for sl in [list(p['z']) for p in step_pos] for i in sl]
    ax.set_xlim3d(min(allx), max(allx))
    ax.set_ylim3d(min(ally), max(ally))
    ax.set_zlim3d(min(allz), max(allz))

    # Animation
    def animate(i):
        pos = step_pos[i]
        sc._offsets3d = (pos['x'].values,
                         pos['y'].values,
                         pos['z'].values)

    ani = matplotlib.animation.FuncAnimation(fig, animate,
                                             frames=steps,
                                             interval=200,
                                             repeat=False)
    return ani


################################################################
# PART 2                                                       #
# More efficient implementation based on the thoughts:         #
#                                                              #
#  - If the same positions and velocities are reach, the same  #
#    behavior would be repited -> We are inside a cicle        #
#                                                              #
#  - If we are in a cicle, the first state to be repeated is   #
#    the current state -> No need to store intermediate states #
#                                                              #
#  - The 3 dimensions are independent from each other -> The   #
#    first repetition would be the Least Common Multiple of    #
#    the cicle lengths for each dimension                      #
################################################################


def cicle_length(positions: pd.DataFrame) -> int:
    """
    Computes the number of steps until the first state repetition
    """

    # Initialize velocities
    velocities = pd.DataFrame({'x': [0]*len(positions),
                               'y': [0]*len(positions),
                               'z': [0]*len(positions)})

    # Store first state
    first_pos = positions.copy()
    first_vel = velocities.copy()

    # Loop over each dimension
    cicles = []
    for dim in velocities.keys():
        print(f'Dimension: {dim}')

        # Initialize 
        steps = 0
        reached_initial = False
        pos = first_pos[dim].values
        vel = first_vel[dim].values

        while not reached_initial:
            steps += 1

            if steps % 1000 == 0:
                print(steps)

            # Apply gravity
            vel_change = [sum([(1 if x<y else -1) for y in [p for p in pos if p!=x]]) for x in pos]
            vel = vel + vel_change

            # Apply velocity
            pos = pos + vel

            if all(first_pos[dim].values == pos) & all(first_vel[dim].values == vel):
                cicles.append(steps)
                reached_initial = True

    return np.lcm.reduce(cicles)
