from abc import ABC, abstractmethod

class BaseTransactionBuilder(ABC):

    @abstractmethod
    def build_contract_transaction(self, from_address: str, contract_address: str, function_name: str, function_args: list, value: int = 0, gas: int = None, gas_price: int = None) -> dict:
        pass

    @abstractmethod
    def sign_transaction(self, transaction, private_key):
        pass

    @abstractmethod
    def broadcast_transaction(self, transaction):
        pass

    @abstractmethod
    def is_transaction_broadcasted(self, tx_hash: str) -> bool:
        pass
