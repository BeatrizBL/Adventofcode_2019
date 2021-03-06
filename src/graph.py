
class Graph:

    def __init__(self, directed: bool = True):
        self._graph_dict = {}
        self.directed = directed

    def add_edge(self, node, neighbor):
        if node not in self._graph_dict:
            self._graph_dict[node] = [neighbor]
        else:
            self._graph_dict[node].append(neighbor)
        
        if neighbor not in self._graph_dict:
            self._graph_dict[neighbor] = []

        # Add edge back for non-directed graphs
        if not self.directed:
            self._graph_dict[neighbor].append(node)

    def get_nodes(self):
        return list(self._graph_dict.keys())

    def get_neighbors(self, node):
        if node not in self.get_nodes():
            raise ValueError('Node not available in the graph!')
        return self._graph_dict[node]

    def print_edges(self):
        for node in self._graph_dict:
            for neighbor in self._graph_dict[node]:
                print('(', node, ', ', neighbor, ')')

    def count_edges(self):
        return sum([len(ngs) for ngs in self._graph_dict.values()])

    def find_path_DFS(self, start, end):
        if start not in self.get_nodes() or end not in self.get_nodes():
            raise ValueError('Node not available in the graph!')

        stack = [(start, [start])]
        while stack:
            (node, path) = stack.pop()
            for next in set(self.get_neighbors(node)) - set(path):
                if next == end:
                    return path + [next]
                else:
                    stack.append((next, path + [next]))
