import configparser
import os

config_path = os.path.join(os.path.dirname(__file__), '.cfg')
config = configparser.ConfigParser()
config.read(config_path)
token = config.get('Configuration', 'Token')