from sol.connection import setup_solana_connection
from sol.builder import SolanaStakingTransactionBuilder
from dotenv import load_dotenv
import os
import json
from solders.keypair import Keypair # type: ignore

# Import the contract address

# Load environment variables
load_dotenv()

def main():
    # Setup Web3 connection
    w3 = setup_solana_connection()
    builder = SolanaStakingTransactionBuilder(w3)
    
    from_address = os.environ.get("SOL_FROM_ADDRESS")
    validator_vote = "ECuwzjAEg7kPVBmmW7xa6Wz9xkK5pbN8cTn4SCdp5PPp"
    sol_private_key = os.environ.get("SOL_PRIVATE_KEY")

    # 
    # Solana Staking Module
    #

    transaction, stake_account_keypair = builder.build_staking_transaction(from_address, validator_vote, 1)
    signed_tx = builder.sign_transaction(transaction, sol_private_key, stake_account_keypair)
    sent_tx = builder.broadcast_transaction(signed_tx, sol_private_key, stake_account_keypair)
    print(sent_tx)
    print(builder.is_transaction_broadcasted(sent_tx))

if __name__ == "__main__":
    main()
