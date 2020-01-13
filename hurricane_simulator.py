import re
from configurator import Configurator
from random import choice as rand_choice
from utils.data_structures import Edge, Node
from environment import FloodBNNode, EdgeBNNode, SmartGraph, BayesNetwork

fraction_re = re.compile("(1(?:\.0)?|0\.[0-9]+)")
leakage = 0.001
T = 3


class Simulator:
    """Hurricane evacuation simulator"""

    def __init__(self):
        G, BN = self.get_graph()
        self.G: SmartGraph = G
        self.BN: BayesNetwork = BN
        # self.G.env = self.env

    @staticmethod
    def get_graph():
        if Configurator.graph_path is 'random':
            return Configurator.randomize_config()
        else:
            return Simulator.parse_graph(Configurator.graph_path)

    @staticmethod
    def parse_graph(path):
        """Parse and create graph from tests file, syntax same as in assignment instructions"""
        num_v_pattern = re.compile("#N\s+(\d+)")
        node_pattern = re.compile("#V(\d+)\s+F\s+"+fraction_re.pattern)
        edge_pattern = re.compile("#(E\d+)\s+(\d+)\s+(\d+)\s+W(\d+)")
        persistence_pattern = re.compile("#Ppersistence\s+"+fraction_re.pattern)

        p_persistence = 0
        bn_node_dict = {}
        node_dict = {}
        bn_nodes = []
        bn_edges = []
        E = []

        with open(path, 'r') as f:
            for line in f.readlines():
                if not line.startswith('#'):
                    continue
                # parse Ppersistence
                match = persistence_pattern.match(line)
                if match:
                    p_persistence = float(match.group(1))
                    FloodBNNode.P_PERSISTENCE = p_persistence
                # parse number of nodes
                match = num_v_pattern.match(line)
                if match:
                    n_vertices = int(match.group(1))
                    for i in range(1, n_vertices+1):
                        t = 0
                        index = str(i)
                        new_node = Node('V'+index)
                        node_dict[index] = new_node
                        new_bn_node = FloodBNNode(new_node, t, chance=0, p_persistence=p_persistence)
                        bn_nodes.append(new_bn_node)
                        bn_node_dict[index, t] = new_bn_node
                # parse nodes
                match = node_pattern.match(line)
                if match:
                    index, chance = match.groups()
                    bn_node_dict[index, 0].chance = float(chance)
                # parse edges
                match = edge_pattern.match(line)
                if match:
                    name, v1_index, v2_index, weight = match.groups()
                    v1 = node_dict[v1_index]
                    v2 = node_dict[v2_index]
                    new_edge = Edge(v1, v2, int(weight), name)
                    E.append(new_edge)
                    bn_edges.append(EdgeBNNode(new_edge, 0))

        V = list(node_dict.values())

        # generate the rest of the Bayes Network nodes after parsing is done
        for t in range(1, T):
            for v in V:
                bn_nodes.append(FloodBNNode(v, t))
            for e in E:
                bn_edges.append(EdgeBNNode(e, t))

        return SmartGraph(V, E), BayesNetwork(bn_nodes, bn_edges)

    def query_network(self):
        #TODO
        self.G.display('Initial Graph')
