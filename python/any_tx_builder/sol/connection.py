from solana.rpc.api import Client
import os

def setup_solana_connection():
    provider_url = os.getenv('SOLANA_PROVIDER_URL')
    return Client(provider_url)
