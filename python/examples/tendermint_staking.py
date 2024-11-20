import os
from any_tx_builder.tendermint.builder import Wallet
from any_tx_builder.tendermint.client import TendermintClient
from any_tx_builder.tendermint.coin import Coin_
from any_tx_builder.tendermint.messages import MsgDelegate_
from any_tx_builder.tendermint.transactions import CreateTxOptions
from any_tx_builder.tendermint.types import AccAddress, ValAddress
from any_tx_builder.tendermint.config import TENDERMINT_SETUP

from dotenv import load_dotenv

#
# Cosmos Blockchain Example
#

load_dotenv()
SETUP = TENDERMINT_SETUP[os.getenv('TENDERMINT_CHAIN')]


def build_cosmos_delegation_tx(cosmos_address: AccAddress):
    cosmos_client = TendermintClient(
        lcd_url=SETUP.rpc_url,
        denom=SETUP.denom,
        default_price=SETUP.base_gas_price,
        chain_id=SETUP.chain_id,
    )
    wallet = Wallet(cosmos_client, cosmos_address)
    wallet.set_private_key(os.getenv('TENDERMINT_WALLET_PRIVATE_KEY'), SETUP.coin_type, 0, 0)

    # Delegation Transaction Message
    # https://docs.cosmos.network/main/modules/staking/03_msg_delegate.html
    # Staking Amount is 0.1 $ATOM

    msg = MsgDelegate_(
        delegator_address=AccAddress(cosmos_address),
        validator_address=ValAddress(os.getenv('TENDERMINT_VALIDATOR_ADDRESS')),
        amount=Coin_(denom=SETUP.denom, amount=os.getenv('TENDERMINT_STAKING_AMOUNT')),
    )
    tx_options = CreateTxOptions(
        msgs=[msg],
        memo="STAKING MEMO",
    )

    # Build the transaction
    tx = wallet.build_tx(tx_options)
    print("✨ Delegation transaction built")

    # Sign the transaction
    signed_tx = wallet.sign_tx(tx)
    print("✨ Transaction signed:")
    print(signed_tx.to_data())

    # Broadcast the transaction
    sent = wallet.broadcast(signed_tx)
    print("-----------🏃 Transaction Sent-----------------")
    print(sent)
    return signed_tx

if __name__ == "__main__":
    signed_tx = build_cosmos_delegation_tx(os.getenv('TENDERMINT_WALLET_ADDRESS'))
