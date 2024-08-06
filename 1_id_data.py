import requests
import pandas as pd
import yaml
from application_logging.logger import logger
from web3 import Web3
from utils.helpers import read_params

# Params
params_path = 'params.yaml'
params = read_params(params_path)
fusion_api = params['api']['fusion_api']
provider_urls = params['web3']['provider_urls']
id_abi = params['web3']['id_abi']
id_data = params['files']['id_data']

try:
    logger.info('ID Data Started')
    
    existing_df = pd.read_csv(id_data)

    response = requests.get(url=fusion_api)
    data = response.json()['data']
    id_df = pd.json_normalize(data)[['symbol', 'address', 'type', 'gauge.address', 'gauge.fee', 'gauge.bribe']]
    id_df.columns = ['symbol', 'address', 'type', 'gauges', 'fees', 'bribes']
    
    if not existing_df.empty:
        id_df = id_df.merge(existing_df[['address', 'algebra_pool']], on='address', how='left')
    
    cl_df = id_df[id_df.type.isin(['Narrow', 'Wide', 'ICHI', 'DefiEdge', 'Correlated', 'CL_Stable'])]

    algebra_pool = []
    for idx, row in cl_df.iterrows():
        if pd.isna(row['algebra_pool']):
            for rpc_endpoint in provider_urls:
                try:
                    web3 = Web3(Web3.HTTPProvider(rpc_endpoint, request_kwargs={'timeout': 2}))
                    contract = web3.eth.contract(address=Web3.to_checksum_address(row['address']), abi=id_abi)
                    pool_address = contract.functions.pool().call()
                    algebra_pool.append(pool_address)
                    break
                except Exception as e:
                    logger.error("Error occurred during ID Data process for address %s. Error: %s" % (row['address'], e))
                    algebra_pool.append(None)
        else:
            algebra_pool.append(row['algebra_pool'])
    
    cl_df.loc[:, 'algebra_pool'] = algebra_pool
    id_df.update(cl_df[['address', 'algebra_pool']])

    # Save updated data
    id_df.to_csv('data/id_data.csv', index=False)
    
    logger.info('ID Data Ended')
except Exception as e:
    logger.error('Error occurred during ID Data process. Error: %s' % e)
