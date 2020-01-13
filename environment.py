from utils.data_structures import Node, Edge, Graph
from typing import List, Set, Union, Dict, Tuple

def rnd(frac):
    return round(frac, 4)


def bool2str(b):
    return str(b)[0]


COMPACT = False
leakage = 0.001


class BNNode(Node):
    """Represents a node in the Bayes-Network, with probability for being flooded or blocked"""
    def __init__(self,
                 label:     str,
                 element:   Union[Node, Edge],
                 time:      Union[str, int],
                 chance:    Union[str, float]=0,
                 parents:   List=[]):
        super().__init__(label)
        self.element = element
        self.time = int(time)
        self.chance = float(chance)
        self.flooded = False # or blocked
        self.parents: List[BNNode] = parents
        self.P = self.get_conditional_probabilities()

    def get_conditional_probabilities(self):
        return {}

    def has_parents(self):
        return len(self.parents) != 0

    def __str__(self):
        return self.label

    def __lt__(self, other):
        return (self.time, self.element.label) < (other.time, other.element.label)

    @staticmethod
    def get_all_bn_nodes() -> List[Node]:
        return sorted(FloodBNNode.NODES.values()) + sorted(EdgeBNNode.EDGES.values())


class FloodBNNode(BNNode):
    """Represents a node in the Bayes-Network, with probability for being flooded"""
    NODES: Dict[Tuple[Node, int], BNNode] = {}
    P_PERSISTENCE = 0

    @staticmethod
    def get_bn_edge_parents(e, t) -> List[BNNode]:
        return [FloodBNNode.NODES[e.v1, t], FloodBNNode.NODES[e.v2, t]]

    def __init__(self, v: Node, time, chance: Union[str, float]=0, p_persistence=0):
        FloodBNNode.NODES[v, time] = self
        self.p_persistence = p_persistence
        parent_bn_nodes = [] if time == 0 else [FloodBNNode.NODES[v, time - 1]]
        super().__init__('Fl({},{})'.format(v, time), v, time, chance, parents=parent_bn_nodes)
        self.v = v

    def get_conditional_probabilities(self):
        original_chance = FloodBNNode.NODES[self.element, 0].chance
        flooded_last_tick = True
        return {
                flooded_last_tick:  FloodBNNode.P_PERSISTENCE,
            not flooded_last_tick:  original_chance
        }

    def print_probability_table(self, compact=COMPACT):
        print("{}, time {}".format(self.v, self.time))
        if self.has_parents():
            for parent_flooded in [False, True]:
                chance = rnd(self.P[parent_flooded])
                if compact:
                    print("\tT | {} = {}".format(bool2str(parent_flooded), chance))
                else:
                    print("\tP({} = T | {} = {}) = {}".format(self,
                                                                 self.parents[0],
                                                                 bool2str(parent_flooded), chance))
        else:
            for flooded in [False, True]:
                chance = rnd(self.chance if flooded else 1 - self.chance)
                if compact:
                    print("\t{} | {}".format(bool2str(flooded), chance))
                else:
                    print("\tP({} = {}) = {}".format(self, bool2str(flooded), chance))


class EdgeBNNode(BNNode):
    EDGES: Dict[Tuple[Edge, int], BNNode] = {}

    def __init__(self, e: Edge, time):
        EdgeBNNode.EDGES[e, time] = self
        parent_bn_nodes = FloodBNNode.get_bn_edge_parents(e, time)
        super().__init__('B({},{})'.format(e.label, time), e, time, parents=parent_bn_nodes)
        self.e = e

    def get_conditional_probabilities(self):
            qi = 1 - 0.6 / self.element.w
            return {
                (False, False): leakage,
                (False, True):  1 - qi,
                (True, False):  1 - qi,
                (True, True):   1 - qi ** 2
            }

    def print_probability_table(self, compact=COMPACT):
        print("{}, time {}".format(self.e.label, self.time))
        for flooded_v1 in [False, True]:
            for flooded_v2 in [False, True]:
                chance = rnd(self.P[flooded_v1, flooded_v2])
                if compact:
                    print("\t{} {} | {}".format(bool2str(flooded_v1), bool2str(flooded_v2), chance))
                else:
                    print("\tP({} = T | {} = {} , {} = {}) = {}".format(self.label,
                                                                        self.parents[0], bool2str(flooded_v1),
                                                                        self.parents[1], bool2str(flooded_v2),
                                                                        chance))


class BayesNetwork:
    def __init__(self, V, E):
        self.V = V
        self.E = E
        self.print_net()

    @staticmethod
    def print_net():
        for bn in BNNode.get_all_bn_nodes():
            bn.print_probability_table()


class SmartGraph(Graph):
    """A variation of a graph that accounts for edge and node deadlines when running dijkstra"""

    def __init__(self, V: List[Node]=[], E: List[Edge]=[], env=None):
        """:param env: the enclosing environment in which the graph "lives". Used to access the environment's time."""
        super().__init__(V, E)
        self.env = env

    def is_blocked(self, u, v):
        e = self.get_edge(u, v)
        return e.blocked or self.env.time + e.w > e.deadline


class Environment:
    def __init__(self, G: SmartGraph):
        self.time = 0
        self.G = G
        self.blocked_edges: Set[Edge] = set([])
