from decimal import Decimal
from typing import Any, List, Optional
from abc import ABC, abstractmethod
from .connection import TendermintConnection
from decimal import Decimal
from typing import Any, Optional
from cosmos_sdk.core.bank import MsgSend
from cosmos_sdk.core.staking import MsgDelegate, MsgUndelegate, MsgBeginRedelegate
from pyinjective.wallet import Address
from pyinjective.transaction import Transaction

from tendermint.connection import InjectiveConnection

class TendermintTxBuilder(ABC):
    def __init__(self, connection: TendermintConnection):
        self.connection = connection

    @abstractmethod
    async def create_send_tx(self, 
                             sender: str, 
                             recipient: str, 
                             amount: Decimal, 
                             denom: str, 
                             memo: Optional[str] = None) -> Any:
        pass

    @abstractmethod
    async def create_delegate_tx(self,
                                 delegator: str,
                                 validator: str,
                                 amount: Decimal,
                                 denom: str,
                                 memo: Optional[str] = None) -> Any:
        pass

    @abstractmethod
    async def create_undelegate_tx(self,
                                   delegator: str,
                                   validator: str,
                                   amount: Decimal,
                                   denom: str,
                                   memo: Optional[str] = None) -> Any:
        pass

    @abstractmethod
    async def create_redelegate_tx(self,
                                   delegator: str,
                                   validator_src: str,
                                   validator_dst: str,
                                   amount: Decimal,
                                   denom: str,
                                   memo: Optional[str] = None) -> Any:
        pass

#
# Cosmos Tx Builder
#

class CosmosTxBuilder(TendermintTxBuilder):
    async def create_send_tx(self, 
                             sender: str, 
                             recipient: str, 
                             amount: Decimal, 
                             denom: str, 
                             memo: Optional[str] = None) -> Any:
        msg = MsgSend(
            from_address=sender,
            to_address=recipient,
            amount=f"{amount}{denom}"
        )
        return self._create_tx([msg], memo)

    async def create_delegate_tx(self,
                                 delegator: str,
                                 validator: str,
                                 amount: Decimal,
                                 denom: str,
                                 memo: Optional[str] = None) -> Any:
        msg = MsgDelegate(
            delegator_address=delegator,
            validator_address=validator,
            amount=f"{amount}{denom}"
        )
        return self._create_tx([msg], memo)

    async def create_undelegate_tx(self,
                                   delegator: str,
                                   validator: str,
                                   amount: Decimal,
                                   denom: str,
                                   memo: Optional[str] = None) -> Any:
        msg = MsgUndelegate(
            delegator_address=delegator,
            validator_address=validator,
            amount=f"{amount}{denom}"
        )
        return self._create_tx([msg], memo)

    async def create_redelegate_tx(self,
                                   delegator: str,
                                   validator_src: str,
                                   validator_dst: str,
                                   amount: Decimal,
                                   denom: str,
                                   memo: Optional[str] = None) -> Any:
        msg = MsgBeginRedelegate(
            delegator_address=delegator,
            validator_src_address=validator_src,
            validator_dst_address=validator_dst,
            amount=f"{amount}{denom}"
        )
        return self._create_tx([msg], memo)

    def _create_tx(self, msgs: List[Any], memo: Optional[str] = None) -> Any:
        return self.connection.client.tx.create(msgs, memo=memo)

#
# Injective Tx Builder
#

class InjectiveTxBuilder(TendermintTxBuilder):
    def __init__(self, connection: InjectiveConnection):
        self.connection = connection

    async def create_send_tx(self, 
                             sender: Address, 
                             recipient: str, 
                             amount: Decimal, 
                             denom: str, 
                             memo: Optional[str] = None):
        if not self.connection.is_connected:
            await self.connection.connect()

        tx = Transaction()
        tx.with_messages(
            tx.msg_send(
                sender.to_acc_bech32(),
                recipient,
                amount,
                denom
            )
        )
        if memo:
            tx.with_memo(memo)

        account = await self.connection.client.get_account(sender.to_acc_bech32())
        tx.with_account_num(account.account_number)
        tx.with_sequence(account.sequence)
        tx.with_chain_id(self.connection.network.chain_id)

        return tx
