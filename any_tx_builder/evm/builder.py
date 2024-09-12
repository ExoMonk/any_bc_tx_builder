class EVMTransactionBuilder:
    def __init__(self, w3_con):
        self.w3 = w3_con

    def build_transaction(self, from_address: str, to_address: str, value: int, gas: int = 21000, gas_price: int = None) -> dict:
        if gas_price is None:
            gas_price = self.w3.eth.gas_price

        transaction = {
            'from': from_address,
            'to': to_address,
            'value': value,
            'gas': gas,
            'gasPrice': gas_price,
            'nonce': self.w3.eth.get_transaction_count(from_address),
        }
        return transaction