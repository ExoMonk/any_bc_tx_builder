import copy
from typing import List, Optional
import requests

from any_tx_builder.tendermint.coin import Coin_
from any_tx_builder.tendermint.transactions.fee import Fee_
from any_tx_builder.tendermint.transactions import (
    AuthInfo_,
    CreateTxOptions,
    SignerInfo_,
    Tx_,
    TxBody_,
)
from any_tx_builder.tendermint.types import AccAddress


class TendermintClient:
    def __init__(
        self, lcd_url: str, default_price: str, denom: str, chain_id: str = "cosmoshub-4", gas_adjustment: float = 1.2
    ):
        self.lcd_url = lcd_url
        self.denom = denom
        self.chain_id = chain_id
        self.default_price = default_price
        self.default_adjustment = gas_adjustment

    def get_account_info(self, acc_address: AccAddress) -> int:
        result = requests.get(f"{self.lcd_url}/cosmos/auth/v1beta1/accounts/{acc_address}")
        return result.json().get("account")

    def estimate_gas(self, tx: Tx_, options: Optional[CreateTxOptions]) -> int:
        gas_adjustment = options.gas_adjustment if options else self.default_adjustment
        res = requests.post(
            f"{self.lcd_url}/cosmos/tx/v1beta1/simulate",
            json={"tx_bytes": tx.to_string_bytes()},
        )
        return int(gas_adjustment * int(res.json()["gas_info"].get("gas_used", 0)))

    def estimate_fee(self, signer_data: List[SignerInfo_], tx_options: CreateTxOptions) -> Fee_:
        gas_prices = tx_options.gas_prices or self.default_price
        gas_adjustment = tx_options.gas_adjustment or self.default_adjustment
        gas_prices_coins = Coin_.from_str(gas_prices)

        tx_body = TxBody_(messages=tx_options.msgs, memo=tx_options.memo or "")
        emptyFee = Fee_(0, [Coin_(denom=self.denom, amount=0)])
        auth_info = AuthInfo_([], emptyFee)

        tx = Tx_(tx_body, auth_info, [])
        tx.append_empty_signatures(signer_data)

        gas = tx_options.gas
        if gas is None or gas == "auto" or int(gas) == 0:
            opt = copy.deepcopy(tx_options)
            opt.gas_adjustment = gas_adjustment
            gas = self.estimate_gas(tx, opt)

        fee_amount = gas_prices_coins.mul(gas) if gas_prices_coins else Coin_.from_str(f"3000{self.denom}")
        return Fee_(gas, [fee_amount], "", "")

    def _broadcast(self, tx: Tx_):
        result = requests.post(
            f"{self.lcd_url}/cosmos/tx/v1beta1/txs",
            json={"tx_bytes": tx.to_string_bytes(), "mode": "BROADCAST_MODE_SYNC"},
        )
        return result.json()
