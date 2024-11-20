from any_tx_builder.sol.connection import setup_solana_connection
from any_tx_builder.sol.builder import SolanaStakingTransactionBuilder
from dotenv import load_dotenv
import os
import json
from solders.keypair import Keypair # type: ignore
from solders.transaction import VersionedTransaction

# Load environment variables
load_dotenv()

def build_staking_transaction():
    # Setup Web3 connection
    w3 = setup_solana_connection()
    builder = SolanaStakingTransactionBuilder(w3)
    
    from_address = os.environ.get("SOLANA_WALLET_ADDRESS")
    validator_vote = "ECuwzjAEg7kPVBmmW7xa6Wz9xkK5pbN8cTn4SCdp5PPp"
    sol_private_key = os.environ.get("SOLANA_PRIVATE_KEY")

    # 
    # Solana Staking Module
    #

    transaction, stake_account_keypair = builder.build_staking_transaction(from_address, validator_vote, 0.01)
    print("✨ Delegation transaction built")

    signed_tx = builder.sign_transaction(transaction, sol_private_key, stake_account_keypair)
    print("✨ Transaction signed:")

    sent_tx = builder.broadcast_transaction(signed_tx.to_solders())
    print("-----------🏃 Transaction Sent-----------------")
    print(sent_tx)
    print(builder.is_transaction_broadcasted(sent_tx.value))

if __name__ == "__main__":
    build_staking_transaction()
