from typing import List, Optional

import attr
from any_tx_builder.tendermint.coin import Coin_
from any_tx_builder.tendermint.proto import Fee
from any_tx_builder.tendermint.types import AccAddress


@attr.s
class Fee_:
    gas_limit: int = attr.ib(converter=int)
    amount: List[Coin_] = attr.ib(converter=list)
    payer: Optional[AccAddress] = attr.ib(default=None)
    granter: Optional[AccAddress] = attr.ib(default=None)

    def to_data(self) -> dict:
        return {
            "gas_limit": str(self.gas_limit),
            "amount": [coin.to_data() for coin in self.amount],
            "payer": str(self.payer),
            "granter": str(self.granter),
        }

    def to_proto(self) -> Fee:
        return Fee(
            amount=[coin.to_proto() for coin in self.amount],
            gas_limit=self.gas_limit,
            payer=self.payer,
            granter=self.granter,
        )
