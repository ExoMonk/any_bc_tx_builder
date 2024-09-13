from abc import ABC, abstractmethod

class BaseTransactionBuilder(ABC):
    @abstractmethod
    def _estimate_gas_price(self):
        pass

    @abstractmethod
    def _estimate_gas(self, transaction: dict) -> int:
        pass

    @abstractmethod
    def list_contract_functions(self, contract_address: str) -> list:
        pass

    @abstractmethod
    def get_contract_abi(self, contract_address: str) -> list:
        pass

    @abstractmethod
    def build_contract_transaction(self, from_address: str, contract_address: str, function_name: str, function_args: list, value: int = 0, gas: int = None, gas_price: int = None) -> dict:
        pass

    @abstractmethod
    def is_transaction_broadcasted(self, tx_hash: str) -> bool:
        pass

    @abstractmethod
    def call_contract_abi(self, function_name: str, function_args: list) -> dict:
        pass