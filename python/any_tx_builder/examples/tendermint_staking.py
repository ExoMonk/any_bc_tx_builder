from any_tx_builder.tendermint.builder import Wallet
from any_tx_builder.tendermint.client import TendermintClient
from any_tx_builder.tendermint.coin import Coin_
from any_tx_builder.tendermint.messages import MsgDelegate_
from any_tx_builder.tendermint.transactions import CreateTxOptions
from any_tx_builder.tendermint.proto import TxBody
from any_tx_builder.tendermint.types import AccAddress, ValAddress
from any_tx_builder.tendermint.config import TENDERMINT_SETUP

#
# Cosmos Blockchain Example
#

COSMOS_SETUP = TENDERMINT_SETUP["cosmos"]


def build_cosmos_tx(cosmos_address: AccAddress):
    cosmos_client = TendermintClient(COSMOS_SETUP.rpc_url, COSMOS_SETUP.denom, COSMOS_SETUP.base_gas_price)
    wallet = Wallet(COSMOS_SETUP.chain, cosmos_client, cosmos_address)

    # Delegation Transaction Message
    # https://docs.cosmos.network/main/modules/staking/03_msg_delegate.html
    # Staking Amount is 0.1 $ATOM

    msg = MsgDelegate_(
        delegator_address=AccAddress(cosmos_address),
        validator_address=ValAddress("cosmosvaloper1svwt2mr4x2mx0hcmty0mxsa4rmlfau4lwx2l69"),
        amount=Coin_(denom=COSMOS_SETUP.denom, amount=100000),
    )
    tx_options = CreateTxOptions(
        msgs=[msg],
        memo="STAKING MEMO",
    )

    # Build the transaction
    tx = wallet.build_tx(tx_options)

    # Reconstruct the transaction to verify the memo
    # tx_body_hex is the required hex representation of the tx body
    # for Fireblocks Raw Signing
    tx_body_hex = bytes.fromhex(tx.body.to_fireblocks_hex())
    tx_reconstructed = TxBody().parse(tx_body_hex)
    assert tx_reconstructed.memo == "STAKING MEMO"
    return tx

if __name__ == "__main__":
    build_cosmos_tx("cosmos1qyqszqgpqyqszqgpqyqszqgpqyqszqgpqyqsz")
