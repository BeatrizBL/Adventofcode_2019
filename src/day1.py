import pandas as pd
import math
import os


def compute_fuel_requirements(mass_file: str,
                              data_path: str = 'data/raw/day1',
                              ) -> int:
    """
    The Fuel Counter-Upper needs to know the total fuel requirement. 
    To find it, individually calculate the fuel needed for the mass of 
    each module (your puzzle input), then add together all the fuel values.

    Fuel required to launch a given module is based on its mass. 
    Specifically, to find the fuel required for a module, take its mass, 
    divide by three, round down, and subtract 2.
    """

    # Read the file
    file_path = os.path.join(data_path, mass_file)
    df_mass = pd.read_csv(file_path)

    # Check the content
    if len(df_mass.columns) > 1:
        raise ValueError('One column expected!')
    mass_col = list(df_mass.columns)[0]

    mass = list(df_mass[mass_col].values)
    fuel = [(math.floor(m/3)-2) for m in mass]

    return sum(fuel)


def compute_fuel_mass(mass: int) -> int:
    """
    Computes the fuel required for a specific mass, taking
    into account that the fuel has mass itself.
    """
    # Stopping condition
    if mass <= 0:
        return 0

    fuel = (math.floor(mass/3)-2)
    fuel = fuel if fuel > 0 else 0

    return fuel + compute_fuel_mass(fuel)


def compute_all_fuel_requirements(mass_file: str,
                                  data_path: str = 'data/raw/day1',
                                  ) -> int:
    """
    Computes what is the sum of the fuel requirements for all the 
    modules on your spacecraft. Taking into account the mass of 
    the added fuel.
    """

    # Read the file
    file_path = os.path.join(data_path, mass_file)
    df_mass = pd.read_csv(file_path)

    # Check the content
    if len(df_mass.columns) > 1:
        raise ValueError('One column expected!')
    mass_col = list(df_mass.columns)[0]

    mass = list(df_mass[mass_col].values)
    fuel = [compute_fuel_mass(m) for m in mass]

    return sum(fuel)
