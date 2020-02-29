import networkx as nx
from typing import List
import math

def parse_reaction(reaction: str) -> dict:
    """ We can't use a regular expression because each reaction
    has a different number of components"""
    inputs = reaction.split(' => ')[0]
    output = reaction.split(' => ')[1]
    reaction = {'out': (output.split(' ')[1], int(output.split(' ')[0]))}
    input_list = []
    for inp in inputs.split(', '):
        input_list.append((inp.split(' ')[1], int(inp.split(' ')[0])))
    reaction['in'] = input_list
    return reaction


def construct_tree(reactions: List[str]):
    """ Cronstructs a directed graph to represent the provided
    reactions """
    reactions = [parse_reaction(r) for r in reactions]
    G = nx.DiGraph()

    # Add nodes
    chemicals = [r['out'] for r in reactions]
    for c in chemicals:
        G.add_node(c[0], n=c[1], left=0)

    # Add edges
    for reaction in reactions:
        out = reaction['out'][0]
        edges = [(e[0], out, e[1]) for e in reaction['in']]
        G.add_weighted_edges_from(edges)

    return G


def DFS_ORE(graph): 
    """ Depth First Search algorithm to count the number of
    required ORE to produce 1 unit of FUEL.
    It accounts for the left overs in each reaction.
    """
    G = graph.copy()
    def _DFSUtil(v, n: int): 
        if v == 'ORE':
            return n
        
        # How many v's I need using the leftovers
        needed = n - G.nodes[v]['left']

        # Remove the v's used from the leftovers
        G.nodes[v]['left'] = max(0, G.nodes[v]['left'] - n)

        # Produce the needed ones
        total = 0
        if needed > 0:
            # How many times the reaction has to be executed
            n_react = math.ceil(needed/G.nodes[v]['n'])

            for i in G.predecessors(v): 
                needed_i = n_react*G[i][v]['weight']
                total += _DFSUtil(i, needed_i)
            G.nodes[v]['left'] += n_react*G.nodes[v]['n'] - needed
        return total
    
    return _DFSUtil('FUEL', 1) 
