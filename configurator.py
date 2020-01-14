import argparse

class Configurator:
    """static configurator class"""
    @staticmethod
    def get_user_config():
        parser = argparse.ArgumentParser(description='''
        Environment simulator for the Hurricane Evacuation Problem
        example: python3 test.py -V 1 -K 5 -g tests/23-11__18-08-25.config -a AStar Vandal''')
        parser.add_argument('-g', '--graph_path',    default='tests/basic.config',       help='path to graph initial configuration file')
        parser.add_argument('-T', type=int,          default=2,                          help='nubmer of time units for the Bayes Network')
        parser.add_argument('-N', '--sample_size',   default=300,   type=int,            help='nubmer of time units for the Bayes Network')
        # debug command line arguments
        parser.add_argument('-d', '--debug',         default=True,  action='store_true', help='run in debug mode')
        parser.add_argument('-i', '--interactive',   default=True,  action='store_true', help='run interactively (with graph displays)')
        parser.add_argument('-s', '--view_strategy', default=True,  action='store_true', help='plot search agents strategy trees')

        args = vars(parser.parse_args())
        for k, v in args.items():
            setattr(Configurator, k, v)
        print("Environment Configured.")


def debug(s):
    if Configurator.debug:
        print(s)

