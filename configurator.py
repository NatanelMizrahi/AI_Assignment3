import argparse


class Configurator:
    """static configurator class"""
    @staticmethod
    def get_user_config():
        parser = argparse.ArgumentParser(description='''
        Bayes Network for the Hurricane Evacuation Problem
        example: python3 test.py -T 2 --graph_path tests/basic.config --seed 3 --sample_size 300''')
        parser.add_argument('-g', '--graph_path',    default='tests/basic.config',       help='path to graph initial configuration file')
        parser.add_argument('-T', type=int,          default=2,                          help='nubmer of time units for the Bayes Network')
        parser.add_argument('-N', '--sample_size',   default=1000,  type=int,            help='nubmer of samples used for the Bayes Network sampling')
        parser.add_argument('-s', '--seed',          default=0,     type=int,            help='random seed for the sampling. Used for debugging')
        parser.add_argument('-c',  '--compact',      default=False, action='store_true', help='print a short version of probabilities as a table')

        args = vars(parser.parse_args())
        for k, v in args.items():
            setattr(Configurator, k, v)
        print("Bayes Network and graph configured.")
