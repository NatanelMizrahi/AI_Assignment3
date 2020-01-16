import re
from configurator import Configurator
from utils.data_structures import Edge, Node, Graph
from bayes_network import FloodBNNode, EdgeBNNode, BayesNetwork

fraction_re = re.compile("(1(?:\.0)?|0\.[0-9]+)")
TEST_MODE = True


def get_list_input(prompt):
    return input(prompt+'\n').upper().replace(' ', '').split(',')


class Simulator:
    """Hurricane evacuation simulator"""

    def __init__(self):
        G, BN = self.get_graph()
        self.G: Graph = G
        self.BN: BayesNetwork = BN

    @staticmethod
    def get_graph():
        return Simulator.parse_graph(Configurator.graph_path)

    @staticmethod
    def parse_graph(path):
        """Parse and create graph from tests file, syntax same as in assignment instructions"""
        num_v_pattern = re.compile("#N\s+(\d+)")
        edge_pattern = re.compile("#(E\d+)\s+(\d+)\s+(\d+)\s+W(\d+)")
        node_pattern = re.compile("#V(\d+)\s+F\s+" + fraction_re.pattern)
        persistence_pattern = re.compile("#Ppersistence\s+" + fraction_re.pattern)

        p_persistence = 0
        bn_node_dict = {}
        node_dict = {}
        bn_nodes = []  # list of nodes for the Bayer Network. Each node represents either an edge/vertex at some time t
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
                        new_bn_node = FloodBNNode(v=new_node, time=t, chance=0, p_persistence=p_persistence)
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
                    bn_nodes.append(EdgeBNNode(e=new_edge, time=0))

        V = list(node_dict.values())

        # generate the rest of the Bayes Network nodes after parsing the initial state is done
        # order matters: vertices in each time unit must be created before edges
        for t in range(1, Configurator.T):
            for v in V:
                bn_nodes.append(FloodBNNode(v, t))
            for e in E:
                bn_nodes.append(EdgeBNNode(e, t))

        return Graph(V, E), BayesNetwork(bn_nodes)

    def add_evidence(self):
        if TEST_MODE:
            block_pattern = re.compile("(~)?B\(E(\d+),\s*(\d+)\)")
            flood_pattern = re.compile("(~)?F\(V(\d+),\s*(\d+)\)")
            evidence_prompt = 'type in evidence e.g. "~B(E1,0)","F(V1,1)". ^C or type "end" to return to menu\n'
        else:
            block_pattern = re.compile("(No\s+)?blockage reported at edge (\d+) at time (\d+)", re.IGNORECASE)
            flood_pattern = re.compile("(No\s+)?Flood reported at vertex (\d+) at time (\d+)", re.IGNORECASE)
            evidence_prompt = """type in reading one piece of evidence at a time 
            (e.g. "Flood reported at vertex 2 at time 0", and then "No blockage reported at edge 1 at time 0" etc.)
            type ^C or "end" to return to menu
            """.replace('  ', '')
        try:
            while True:
                raw_evidence = input(evidence_prompt)
                if raw_evidence == 'end':
                    break
                block_evidence = block_pattern.match(raw_evidence)
                if block_evidence:
                    blocked_prefix, edge_idx, time = block_evidence.groups()
                    is_blocked_or_flooded = blocked_prefix is None
                    edge_label = 'E' + edge_idx
                    time = int(time)
                    bn_node = self.BN.get_node(edge_label, time)
                else:
                    flood_evidence = flood_pattern.match(raw_evidence)
                    if flood_evidence:
                        flooded_prefix, node_idx, time = flood_evidence.groups()
                        is_blocked_or_flooded = flooded_prefix is None
                        node_label = 'V' + node_idx
                        time = int(time)
                        bn_node = self.BN.get_node(node_label, time)
                    else:
                        print("invalid evidence string")
                        continue

                if bn_node is None:
                    print("invalid (edge/vertex, time) pair")
                    continue

                bn_node.value = is_blocked_or_flooded
                print('fixed {} = {}'.format(bn_node, bn_node.value))

        except KeyboardInterrupt:  # ^C pressed
            return

    def query_vertex_flood_probability(self):
        flood_queries = [{v: True} for v in self.BN.V if isinstance(v, FloodBNNode)]
        self.BN.sample_queries(flood_queries)

    def query_edge_block_probability(self):
        block_queries = [{e: True} for e in self.BN.V if isinstance(e, EdgeBNNode)]
        self.BN.sample_queries(block_queries)

    def query_free_path_probability_helper(self, edges, t, verbose=True):
        edge_bn_nodes = [self.BN.get_node(e, t) for e in edges]
        block_query = [{e: False for e in edge_bn_nodes}]
        return self.BN.sample_queries(block_query, verbose=verbose)

    def query_free_path_probability(self):
        try:
            t = int(input('choose time for query:\n'))
            edges_raw = get_list_input('type in comma separated edge indices. e.g. for E1,E5,E3 type "1,5,3"')
            edges = ['E' + i for i in edges_raw]
            self.query_free_path_probability_helper(edges, t)
        except:
            print("invalid time or edge indeces")

    def query_best_probable_path(self):
        try:
            t = int(input('choose time for query:\n'))
            nodes_raw = get_list_input('type in comma separated vertex indeces, e.g. "1,3" for V1,V3')
            src, tgt = ['V' + i for i in nodes_raw]
            path_str = '\n{0}->{{}}->{1}:'.format(src, tgt)
            simple_paths = self.G.get_simple_paths(src, tgt)
            paths_blockage_queries_results = []
            for path_edges_list in simple_paths:
                path_query, evidence, probability = self.query_free_path_probability_helper(path_edges_list, t, verbose=False)[0]
                paths_blockage_queries_results.append((path_query, evidence, probability))
            path_result_pairs = list(zip(simple_paths, paths_blockage_queries_results))
            for path_edges, query in path_result_pairs:
                print(path_str.format('->'.join(path_edges)))
                self.BN.print_query_result(query)
            best_path, unblocked_prob = max(path_result_pairs, key=lambda pq: pq[1][2])
            print('\nThe best option is: {}\nP(Path is unblocked)={}\n'
                  .format(path_str.format('->'.join(best_path)), unblocked_prob[2]))
        except:
            print("invalid time or vertices")


    def print_graph(self):
        self.BN.print_net()
        self.G.display('Initial Graph')

    def reset_evidence(self):
        self.BN.reset_evidence()
        print('Evidence reset.')

    def view_evidence(self):
        for var, val in self.BN.get_evidence().items():
            print(var, '=', val)

    def quit(self):
        exit(0)

    def query_network(self):
        prompt = """Make your choice:
            1 - Query Vertex Flood Probability
            2 - Query Edge Block Probability
            3 - Query Free Path Probability
            4 - Query Best Probable Path
            5 - Add Evidence
            6 - Reset Evidence
            7 - View Evidence
            8 - Print Graph
            9 - Quit\n"""

        ops = {
            1: self.query_vertex_flood_probability,
            2: self.query_edge_block_probability,
            3: self.query_free_path_probability,
            4: self.query_best_probable_path,
            5: self.add_evidence,
            6: self.reset_evidence,
            7: self.view_evidence,
            8: self.print_graph,
            9: self.quit
        }
        while True:
            i = int(input(prompt))
            if i in ops:
                ops[i]()
            else:
                print("Command not found")

