import yaml


def load_config():
    filename = './config/osc_config.yml'
    with open(filename, 'r') as ymlfile:
        data = yaml.load_all(ymlfile, Loader=yaml.FullLoader)
        cfg = {}
        for docs in data:
            cfg = docs
    return cfg


config = load_config()


def get_address(name):
    return config['ip'][name], config['port'][name]
