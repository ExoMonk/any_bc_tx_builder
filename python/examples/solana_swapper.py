from dotenv import load_dotenv
import os
from any_tx_builder.sol.connection import setup_solana_connection
from any_tx_builder.sol.builder import SolanaSwapper

# Load environment variables
load_dotenv()

def build_transfer_sol_transaction():
    # Setup Web3 connection
    w3 = setup_solana_connection()
    builder = SolanaSwapper(w3)
    
    from_address = os.environ.get("SOLANA_WALLET_ADDRESS")
    sol_private_key = os.environ.get("SOLANA_PRIVATE_KEY")

    to_address = os.environ.get("SOLANA_WALLET_ADDRESS_2")

    # 
    # Solana Swapper Module
    # Example 1: Transfer SOL
    #

    transaction = builder.transfer_sol(from_address, to_address, 0.1)
    print("✨ Transfer transaction built")
    signed_tx = builder.sign_transaction(transaction, sol_private_key)
    print("✨ Transaction signed:")
    sent_tx = builder.broadcast_transaction(signed_tx.to_solders())
    print("-----------🏃 Transaction Sent-----------------")
    print(sent_tx)
    print(builder.is_transaction_broadcasted(sent_tx.value))

def build_transfer_token_transaction():
    # Setup Web3 connection
    w3 = setup_solana_connection()
    builder = SolanaSwapper(w3)
    
    from_address = os.environ.get("SOLANA_WALLET_ADDRESS")
    sol_private_key = os.environ.get("SOLANA_PRIVATE_KEY")

    to_address = os.environ.get("SOLANA_WALLET_ADDRESS_2")

    transaction = builder.transfer(from_address, to_address, "Gh9ZwEmdLJ8DscKNTkTqPbNwLNNBjuSzaG9Vp2KGtKJr", 100000)
    print("✨ Transfer transaction built")
    signed_tx = builder.sign_transaction(transaction, sol_private_key)
    print("✨ Transaction signed:")
    sent_tx = builder.broadcast_transaction(signed_tx.to_solders())
    print("-----------🏃 Transaction Sent-----------------")
    print(sent_tx)
    print(builder.is_transaction_broadcasted(sent_tx.value))

def test_get_token_decimals():
    w3 = setup_solana_connection()
    builder = SolanaSwapper(w3)
    decimals = builder.get_token_decimals("Gh9ZwEmdLJ8DscKNTkTqPbNwLNNBjuSzaG9Vp2KGtKJr")
    print(decimals)

if __name__ == "__main__":
    #build_transfer_sol_transaction()
    #build_transfer_token_transaction()
    test_get_token_decimals()