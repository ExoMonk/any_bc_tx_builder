from abc import ABC, abstractmethod
from typing import Any, Optional
from cosmos_sdk.client.lcd import LCDClient
from cosmos_sdk.core.auth import TxInfo
from pyinjective.async_client import AsyncClient
from pyinjective.constant import Network

class TendermintConnection(ABC):
    def __init__(self, network: str, chain_id: str):
        self.network = network
        self.chain_id = chain_id
        self.client = None

    @abstractmethod
    async def connect(self):
        pass

    @abstractmethod
    async def close(self):
        pass

    @property
    @abstractmethod
    def is_connected(self) -> bool:
        pass

    @abstractmethod
    async def get_account(self, address: str) -> Any:
        pass

    @abstractmethod
    async def broadcast_tx_sync(self, tx: Any) -> Any:
        pass


#
# Cosmos Connection
#

class CosmosConnection(TendermintConnection):
    def __init__(self, network: str, chain_id: str):
        super().__init__(network, chain_id)
        self.client = LCDClient(chain_id=chain_id, url=network)

    async def connect(self):
        # LCDClient doesn't require explicit connection
        pass

    async def close(self):
        # LCDClient doesn't require explicit closing
        pass

    @property
    def is_connected(self) -> bool:
        return self.client is not None

    async def get_account(self, address: str) -> Any:
        return self.client.auth.account_info(address)

    async def broadcast_tx_sync(self, tx: Any) -> TxInfo:
        return self.client.tx.broadcast_sync(tx)

#
# Injective Connection
#

class InjectiveConnection:
    def __init__(self, network: Optional[Network] = None):
        self.network = network or Network.mainnet()
        self.client = None

    async def connect(self):
        self.client = AsyncClient(self.network)
        await self.client.compose_market_streams()

    async def close(self):
        if self.client:
            await self.client.close()

    @property
    def is_connected(self):
        return self.client is not None
