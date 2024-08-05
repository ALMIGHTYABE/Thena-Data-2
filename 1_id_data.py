import requests
import pandas as pd
import yaml
from application_logging.logger import logger
from web3 import Web3
from web3.middleware import validation


# Params
params_path = 'params.yaml'


def read_params(config_path):
    with open(config_path) as yaml_file:
        config = yaml.safe_load(yaml_file)
    return config


params = read_params(params_path)

try:
    logger.info('ID Data Started')

    # Params Data
    fusion_api = params['api']['fusion_api']

    # Request
    response = requests.get(url=fusion_api)
    data = response.json()['data']
    id_df = pd.json_normalize(response.json()['data'])[['symbol', 'address', 'type', 'gauge.address', 'gauge.fee', 'gauge.bribe']]
    id_df.columns = ['symbol', 'address', 'type', 'gauges', 'fees', 'bribes']
    id_df['algebra_pool'] = 0

    id_df.to_csv('data/id_data.csv', index=False)

    logger.info('ID Data Ended')
except Exception as e:
    logger.error('Error occurred during ID Data process. Error: %s' % e)
