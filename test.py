from hurricane_simulator import Simulator
from configurator import Configurator

if __name__ == '__main__':
    Configurator.get_user_config()
    sim = Simulator()
    sim.query_network()
