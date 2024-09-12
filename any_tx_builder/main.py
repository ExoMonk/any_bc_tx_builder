from evm.connection import setup_web3_connection
from evm.builder import EVMTransactionBuilder
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

def main():
    # Setup Web3 connection
    w3 = setup_web3_connection()
    builder = EVMTransactionBuilder(w3)
    
    from_address = os.getenv('FROM_ADDRESS')
    to_address = '0x742d35Cc6634C0532925a3b844Bc454e4438f44e'
    value = w3.to_wei(0.1, 'ether')
    gas = 21000
    gas_price = w3.eth.gas_price

    # Build the transaction
    transaction = builder.build_transaction(from_address, to_address, value, gas, gas_price)
    print("Transaction built:")
    print(transaction)

if __name__ == "__main__":
    main()