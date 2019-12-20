from typing import List
import os
from src.graph import Graph


def create_graph(orbits_path: str = None,
                 orbits: List[str] = None,
                 root_path: str = 'data/raw'
                 ) -> Graph:
    """
    Creates an orbits graph. The orbit information can be provided as 
    a list of strings, like ['A)B', 'B)C'] or as the path of a file
    containing one orbit per line
    """

    if orbits_path is not None:
        # Check the parameters
        path = os.path.join(root_path, orbits_path)
        if not os.path.exists(path):
            raise ValueError('Orbit information not available at {}'.format(path))
        
        if orbits is not None:
            raise ValueError('WARNING: Using orbits from file')

        # Read and format the orbits file
        f = open(path, 'r')
        orbits = f.readlines()
        orbits = [o.replace('\n', '') for o in orbits]

    elif orbits is None:
        raise ValueError('Provide some orbits')

    # Create the graph
    g = Graph()
    for orbit in orbits:
        objects = orbit.split(')')
        g.add_edge(objects[0], objects[1])

    return g


def count_orbits(g: Graph, center: str = 'COM') -> int:
    """
    Counts the total number of direct and indirect orbits in the graph.
    
    Note:  This implementation is quite inefficient, since it uses DFS 
    starting always with "COM". Then, the same path is computed a lot 
    of different times for big graphs. It could be optimized moving also
    the starting point.
    """
    objs = g.get_nodes()
    objs.remove(center)

    n = 0
    for obj in objs:
        n = n + len(g.find_path_DFS(center, obj)) - 1
    return n
