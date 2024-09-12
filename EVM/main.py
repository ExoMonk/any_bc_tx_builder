from web3 import Web3
from eth_account import Account
from eth_account.signers.local import LocalAccount
from web3.middleware import construct_sign_and_send_raw_middleware

def setup_web3_connection(provider_url: str) -> Web3:
    return Web3(Web3.HTTPProvider(provider_url))

def create_and_sign_transaction(w3: Web3, account: LocalAccount, to_address: str, value: int, gas: int, gas_price: int) -> dict:
    transaction = {
        'to': to_address,
        'value': value,
        'gas': gas,
        'gasPrice': gas_price,
        'nonce': w3.eth.get_transaction_count(account.address),
    }
    signed_txn = account.sign_transaction(transaction)
    return signed_txn

def main():
    # Setup Web3 connection
    w3 = setup_web3_connection('https://mainnet.infura.io/v3/YOUR-PROJECT-ID')

    # Create an account (in production, you'd use a secure way to manage private keys)
    private_key = '0x...'  # Your private key here
    account = Account.from_key(private_key)

    # Add the account to the middleware
    w3.middleware_onion.add(construct_sign_and_send_raw_middleware(account))

    # Example transaction parameters
    to_address = '0x742d35Cc6634C0532925a3b844Bc454e4438f44e'
    value = w3.to_wei(0.1, 'ether')
    gas = 21000
    gas_price = w3.eth.gas_price

    # Create and sign the transaction
    signed_txn = create_and_sign_transaction(w3, account, to_address, value, gas, gas_price)

    # Send the transaction
    tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
    print(f"Transaction sent: {tx_hash.hex()}")

    # Wait for the transaction receipt
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    print(f"Transaction mined in block: {tx_receipt['blockNumber']}")

if __name__ == "__main__":
    main()