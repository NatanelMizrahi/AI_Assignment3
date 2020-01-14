from utils.data_structures import Node, Edge, DirectedGraph
from typing import List, Union, Dict, Tuple
from configurator import Configurator
import random


def rnd(frac):
    return round(frac, 4)


def bool2str(b):
    return str(b)[0]


COMPACT = False
UNASSIGNED = None
RAND_SEED = 42
LEAKAGE = 0.001

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
        self.value = UNASSIGNED  # flooded or blocked - None | True | False
        self.temp = UNASSIGNED
        self.parents: List[BNNode] = parents
        self.children = []
        for p in self.parents:
            p.children.append(self)
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

    @staticmethod
    def get_all_bn_vertex() -> List[Node]:
        return sorted(FloodBNNode.NODES.values())

    def get_node_probability(self):
        '''Implemented by child classes'''
        pass


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

    def get_node_probability(self):
        if not self.has_parents():
            return self.chance
        else:
            parent_flooded = self.parents[0].temp  # parent's assignment for the current sample) - treated as a fact
            return self.P[parent_flooded]
            # pf = self.parents[0].get_node_probability()  # prob his parent is flooded
            # return rnd(pf * self.P[True] + (1 - pf) * self.P[False])

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
                (False, False): LEAKAGE,
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

    def get_node_probability(self):
        # parents' assignments for the current sample) - treated as a fact
        v1_flooded = self.parents[0].temp
        v2_flooded = self.parents[1].temp
        return self.P[v1_flooded, v2_flooded]


class BayesNetwork:
    def __init__(self, V: List[BNNode]):
        E = []
        for p in V:
            for c in p.children:
                E.append(Edge(p, c, directed=True))
        self.V: List[BNNode] = V
        self.E: List[Edge] = []
        self.G: DirectedGraph = DirectedGraph(V, E)
        self.nodes: Dict[Tuple[str, int], BNNode] = {}
        for bn_node in V:
            label, t = bn_node.element.label, bn_node.time
            self.nodes[label, t] = bn_node
        self.top_sorted_V: List[BNNode] = self.G.topological_sort()

    def get_nodes(self):
        return sorted(self.V)

    def print_net(self):
        for bn in self.get_nodes():
            bn.print_probability_table()
        self.G.display('Bayes Network')

    def reset_evidence(self):
        for bn in self.get_nodes():
            bn.value = UNASSIGNED

    def get_node(self, label, t):
        return self.nodes.get((label, t))

    """SAMPLING"""
    def get_evidence(self):
        return {v: v.value for v in self.get_nodes() if v.value is not UNASSIGNED}

    def get_single_weighted_sample(self):
        """Weighted likelihood sampling - generate a single sample"""
        sample = {}
        weight = 1
        for v in self.top_sorted_V:
            v.temp = UNASSIGNED
            conditional_prob = v.get_node_probability()
            if v.value is not UNASSIGNED:
                # v is an evidence var. it is fixed and accounted for by re-weighting with it's probability as a factor
                v.temp = v.value
                weight *= conditional_prob
            else:
                # assign a "True" value to the node with this probability
                v.temp = random.random() < conditional_prob
            sample[v] = v.temp
        return sample, weight

    def generate_weighted_samples(self):
        """Weighted likelihood sampling - generate a set of samples"""
        random.seed(RAND_SEED)
        weighted_samples: List[Tuple[Dict[BNNode,bool]], float] = \
            [self.get_single_weighted_sample() for i in range(Configurator.sample_size)]
        return weighted_samples

    def sample_consistant_with_assignment(self, sw, a):
        s, _ = sw
        for v in a.keys():
            if s[v] != a[v]:
                return False
        return True

    def filter_samples(self, weighted_samples, assignment):
        return [s for s in weighted_samples if self.sample_consistant_with_assignment(s, assignment)]

    def filter_by_evidence(self, weighted_samples):
        evidence: Dict[BNNode, bool] = self.get_evidence()
        return self.filter_samples(weighted_samples, evidence)

    def sample(self, weighted_samples, query: Dict[BNNode, bool]):
        """
        Weighted likelihood sampling
        :param query: a dict of {BNNode(BayerNetworkNode):value(True/False)} pairs
        :param weighted_samples: a list of tuples containing: a dict ({BNNode:value} pairs) and weight for each sample
        :return: a sampling based probability for the query given the evidence
        """
        matching_samples = self.filter_samples(weighted_samples, query)
        total_weight = sum([weight for sample, weight in weighted_samples])
        match_weight = sum([weight for sample, weight in matching_samples])
        return match_weight/total_weight

    def query_results(self, query, prob, evidence):
        def join(q):
            return ','.join(['{}={}'.format(v, bool2str(val)) for v, val in q.items()])

        return 'P({}{}{}) = {}'.format(join(query), '| ' if evidence else '', join(evidence), rnd(prob))

    def sample_queries(self, queries: List[Dict[BNNode, bool]]):
        weighted_samples = self.generate_weighted_samples()
        evidence = self.get_evidence()
        # weighted_samples = self.filter_by_evidence(weighted_samples)  # redundant in Likelihood Weighting
        queries_results = [(query, self.sample(weighted_samples, query)) for query in queries]
        query_results_str = [self.query_results(query, prob, evidence) for query, prob in queries_results]
        print('\n'.join(query_results_str))

