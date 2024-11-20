########################################################
#
# Tendermint Constants
#
########################################################
from pydantic import BaseModel


class TendermintChainConfig(BaseModel):
    rpc_url: str
    denom: str
    base_gas_price: str
    chain: str
    chain_id: str
    coin_type: int
#
# Cosmos Constants
#

COSMOS_RPC_URL = "https://cosmos-api.polkachu.com"
COSMOS_DENOM = "uatom"
COSMOS_BASE_GAS_PRICE = "0.006uatom"

TENDERMINT_SETUP = {
    "cosmos": TendermintChainConfig(
        rpc_url=COSMOS_RPC_URL,
        denom=COSMOS_DENOM,
        base_gas_price=COSMOS_BASE_GAS_PRICE,
        chain="cosmos",
        chain_id="cosmoshub-4",
        coin_type=118,
    )
}
