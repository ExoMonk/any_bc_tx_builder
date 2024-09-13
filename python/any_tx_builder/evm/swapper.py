from .builder import EVMTransactionBuilder
from typing import Optional, Dict, Any

class Swapper:
    def __init__(self, tx_builder: EVMTransactionBuilder, private_key: str):
        self.tx_builder = tx_builder
        self.account = self.w3.eth.account.from_key(private_key)

    def sign_and_send_transaction(self, transaction: Dict[str, Any]) -> str:
        signed_txn = self.sign_transaction(transaction, self.account.private_key)
        tx_hash = self.broadcast_transaction(signed_txn.rawTransaction)
        print(f" ✅ Transaction sent: {tx_hash}")
        return self.w3.to_hex(tx_hash)

    def swap(self, 
             token_in: str, 
             token_out: str, 
             amount_in: int, 
             min_amount_out: int, 
             recipient: Optional[str] = None,
             aggregator: str = "1inch",  # Default to 1inch, but can be changed
             slippage: float = 0.005) -> str:
        
        # 1. Get a quote from the aggregator
        quote = self.get_quote(token_in, token_out, amount_in, aggregator)
        
        # 2. Approve token spending if necessary
        if token_in != "0x0000000000000000000000000000000000000000":  # Not ETH
            sent_allowance_tx = self.approve_token(self.account.address, token_in, amount_in, quote['router'])
            tx_receipt = self.w3.eth.wait_for_transaction_receipt(sent_allowance_tx)

        # 3. Build the swap transaction
        swap_data = quote['data']  # Assuming the quote returns the calldata
        swap_tx = self.tx_builder.build_contract_transaction(
            from_address=self.account.address,
            contract_address=quote['router'],
            function_name="swap",  # This might vary depending on the aggregator
            function_args=[],  # The swap_data already contains all necessary arguments
            value=amount_in if token_in == "0x0000000000000000000000000000000000000000" else 0
        )
        
        # Modify the transaction data with the swap_data from the quote
        swap_tx['data'] = swap_data
        return self.sign_and_send_transaction(swap_tx)

    def get_quote(self, token_in: str, token_out: str, amount_in: int, aggregator: str) -> Dict[str, Any]:
        # Implement quote fetching logic here
        # This will involve calling the aggregator's API to get a quote
        # Return a dictionary with at least 'router' and 'data' keys
        pass

    def approve_token(self, from_address: str, token: str, amount: int, spender: str) -> Dict[str, Any]:
        allowance_tx = self.tx_builder.build_allowance_transaction(
            from_address=from_address,
            token_address=token,
            spender=spender,
            amount=amount
        )
        return self.sign_and_send_transaction(allowance_tx)