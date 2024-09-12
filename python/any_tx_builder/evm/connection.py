from web3 import Web3
import os

def setup_web3_connection() -> Web3:
    provider_url = os.getenv('EVM_PROVIDER_URL')
    return Web3(Web3.HTTPProvider(provider_url))
