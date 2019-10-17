import yaml


def load_config():
    filename = './config/output_config.yml'
    with open(filename, 'r') as ymlfile:
        data = yaml.load_all(ymlfile, Loader=yaml.FullLoader)
        cfg = {}
        for docs in data:
            for key, value in docs.items():
                cfg[key] = value
    return cfg


config = load_config()
