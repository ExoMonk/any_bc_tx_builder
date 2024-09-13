import os
import json
import requests
from web3.exceptions import ContractLogicError
from web3 import Web3

from evm.config import POLYGON_STAKING_CONTRACT, POLYGON_TOKEN_CONTRACT
from builder_base import BaseTransactionBuilder

class EVMTransactionBuilder(BaseTransactionBuilder):
    def __init__(self, w3_con: Web3):
        self.w3 = w3_con

    def _estimate_gas_price(self):
        # Get the latest block and calculate base fee
        latest_block = self.w3.eth.get_block('latest')
        base_fee = latest_block['baseFeePerGas']

        # Calculate max priority fee (tip)
        max_priority_fee_wei = self.w3.eth.max_priority_fee
        
        # Calculate max fee per gas
        max_fee_per_gas = base_fee + max_priority_fee_wei
        
        return {
            'maxFeePerGas': max_fee_per_gas,
            'maxPriorityFeePerGas': max_priority_fee_wei
        }

    def _estimate_gas(self, transaction: dict) -> int:
        try:
            estimated_gas = self.w3.eth.estimate_gas(transaction)
            return int(estimated_gas * 1.1)
        except ContractLogicError as e:
            print(f"Gas estimation failed: {str(e)}")
            raise ContractLogicError(f"Gas estimation failed due to contract logic error: {str(e)}")
    
    def get_contract_abi(self, contract_address: str) -> list:
        local_file_path = f"./abi/{contract_address}.json"
        if os.path.exists(local_file_path):
            with open(local_file_path, 'r') as file:
                return json.load(file)
        # If local file doesn't exist, fetch ABI from API
        etherscan_api_key = os.getenv('ETHERSCAN_API_KEY')
        if os.getenv('ENV') == 'dev':
            api_url = f"https://api-sepolia.etherscan.io/api?module=contract&action=getabi&address={contract_address}&apikey=YourApiKeyToken"
        else:
            api_url = f"https://api.etherscan.io/api?module=contract&action=getabi&address={contract_address}&apikey={etherscan_api_key}"
        response = requests.get(api_url)
        if response.status_code == 200:
            data = response.json()
            if data['status'] == '1':
                abi = json.loads(data['result'])
                # Save ABI to local file for future use
                if not os.path.exists('./abi'):
                    os.makedirs('./abi')
                with open(local_file_path, 'w') as file:
                    json.dump(abi, file)
                
                return abi
            else:
                raise Exception(f"API Error: {data['message']}")
        else:
            raise Exception(f"HTTP Error: {response.status_code}")

    def list_contract_functions(self, contract_address: str) -> list:
        # Get the contract ABI
        abi = self.get_contract_abi(contract_address)
        # Filter out function entries from the ABI
        functions = [item['name'] for item in abi if item['type'] == 'function']
        return functions
    
    def call_contract_abi(self, contract_address: str, function_name: str, function_args: list) -> dict:
        # Create contract instance
        contract = self.w3.eth.contract(address=contract_address, abi=self.get_contract_abi(contract_address))
        # Get the contract function
        contract_function = getattr(contract.functions, function_name)
        # Call the contract function
        return contract_function(*function_args).call()

    def build_allowance_transaction(self, from_address: str, token_address: str, spender: str, amount: int) -> dict:
        # Create contract instance
        contract = self.w3.eth.contract(address=token_address, abi=self.get_contract_abi(token_address))
        # Get the approve function
        allowance_function = contract.functions.approve(spender, amount)
        # Estimate gas
        gas_price = self._estimate_gas_price()
        max_fee_per_gas = gas_price['maxFeePerGas']
        max_priority_fee_per_gas = gas_price['maxPriorityFeePerGas']    
        # Build the transaction
        transaction = allowance_function.build_transaction({
            'from': from_address,
            'maxFeePerGas': max_fee_per_gas,
            'maxPriorityFeePerGas': max_priority_fee_per_gas,
            'nonce': self.w3.eth.get_transaction_count(from_address),
        })
        gas = self._estimate_gas(transaction)
        transaction['gas'] = gas

        return transaction 

    def build_contract_transaction(self, from_address: str, contract_address: str, function_name: str, function_args: list, value: int = 0) -> dict:
        # Create contract instance
        contract = self.w3.eth.contract(address=contract_address, abi=self.get_contract_abi(contract_address))
        # Get the contract function
        contract_function = getattr(contract.functions, function_name)

        # Estimate gas
        gas_price = self._estimate_gas_price()
        max_fee_per_gas = gas_price['maxFeePerGas']
        max_priority_fee_per_gas = gas_price['maxPriorityFeePerGas']    
        # Build the transaction
        transaction = contract_function(*function_args).build_transaction({
            'from': from_address,
            'value': value,
            'maxFeePerGas': max_fee_per_gas,
            'maxPriorityFeePerGas': max_priority_fee_per_gas,
            'nonce': self.w3.eth.get_transaction_count(from_address),
        })
        gas = self._estimate_gas(transaction)
        transaction['gas'] = gas
        return transaction

    def sign_transaction(self, transaction: dict, private_key: str) -> Web3.Transaction:
        account: Web3.Account = self.w3.eth.account.from_key(private_key)
        signed_txn: Web3.Transaction = account.sign_transaction(transaction)
        return signed_txn
    
    def broadcast_transaction(self, signed_raw_transaction: str) -> str:
        tx_hash = self.w3.eth.send_raw_transaction(signed_raw_transaction)
        print(f" ✅ Transaction sent: {tx_hash}")
        return self.w3.to_hex(tx_hash)

    def is_transaction_broadcasted(self, tx_hash: str) -> bool:
        """
        Check if a transaction has been successfully broadcasted to the network.
        
        :param tx_hash: The transaction hash to check.
        :return: Boolean indicating whether the transaction was broadcasted successfully.
        """
        try:
            tx_receipt = self.w3.eth.get_transaction_receipt(tx_hash)
            if tx_receipt is not None:
                return tx_receipt.status == 1
        except Exception as e:
            print(e)
            return False
            

class PolygonStakingTransactionBuilder(EVMTransactionBuilder):
    def __init__(self, w3_con):
        super().__init__(w3_con)

    def build_POL_allowance_transaction(self, from_address: str, amount: int) -> dict:
        return self.build_allowance_transaction(from_address, POLYGON_TOKEN_CONTRACT, POLYGON_STAKING_CONTRACT, amount)

    def build_staking_transaction(self, from_address: str, amount: int, validator_address: int) -> dict:
        # Create contract instance
        abi = self.get_contract_abi(validator_address)
        contract = self.w3.eth.contract(address=validator_address, abi=abi)
        
        # Get the staking function
        delegation_deposit_function = contract.functions.buyVoucherPOL(
            amount,
            0
        )

        # Estimate gas
        gas_price = self._estimate_gas_price()
        max_fee_per_gas = gas_price['maxFeePerGas']
        max_priority_fee_per_gas = gas_price['maxPriorityFeePerGas']    
        # Build the transaction
        transaction = delegation_deposit_function.build_transaction({
            'from': from_address,
            'maxFeePerGas': max_fee_per_gas,
            'maxPriorityFeePerGas': max_priority_fee_per_gas,
            'nonce': self.w3.eth.get_transaction_count(from_address),
        })
        gas = self._estimate_gas(transaction)
        transaction['gas'] = gas
        return transaction

    def build_unstaking_transaction(self, from_address: str, validator_address: int, amount: int) -> dict:
        # Create contract instance
        abi = self.get_contract_abi(validator_address)
        contract = self.w3.eth.contract(address=validator_address, abi=abi)
        
        # Get the unstake function
        unstake_function = contract.functions.sellVoucher_newPOL(amount, amount)

        # Estimate gas
        gas_price = self._estimate_gas_price()
        max_fee_per_gas = gas_price['maxFeePerGas']
        max_priority_fee_per_gas = gas_price['maxPriorityFeePerGas']    
    
        # Build the transaction
        transaction = unstake_function.build_transaction({
            'from': from_address,
            'maxFeePerGas': max_fee_per_gas,
            'maxPriorityFeePerGas': max_priority_fee_per_gas,
            'nonce': self.w3.eth.get_transaction_count(from_address),
        })
        gas = self._estimate_gas(transaction)
        transaction['gas'] = gas
        return transaction
    
    def build_restaking_transaction(self, from_address: str, validator_address: int) -> dict:
        # Create contract instance
        abi = self.get_contract_abi(validator_address)
        contract = self.w3.eth.contract(address=validator_address, abi=abi)
        
        # Get the restake function
        restake_function = contract.functions.restake()

        # Estimate gas
        gas_price = self._estimate_gas_price()
        max_fee_per_gas = gas_price['maxFeePerGas']
        max_priority_fee_per_gas = gas_price['maxPriorityFeePerGas']
    
        # Build the transaction
        transaction = restake_function.build_transaction({
            'from': from_address,
            'maxFeePerGas': max_fee_per_gas,
            'maxPriorityFeePerGas': max_priority_fee_per_gas,
            'nonce': self.w3.eth.get_transaction_count(from_address),
        })
        gas = self._estimate_gas(transaction)
        transaction['gas'] = gas
        return transaction
    
    def build_withdraw_rewards_transaction(self, from_address: str, validator_address: int) -> dict:
        # Create contract instance
        abi = self.get_contract_abi(validator_address)
        contract = self.w3.eth.contract(address=validator_address, abi=abi)
        
        # Get the withdrawRewards function
        withdraw_rewards_function = contract.functions.withdrawRewardsPOL()

        # Estimate gas
        gas_price = self._estimate_gas_price()
        max_fee_per_gas = gas_price['maxFeePerGas']
        max_priority_fee_per_gas = gas_price['maxPriorityFeePerGas']
    
        # Build the transaction
        transaction = withdraw_rewards_function.build_transaction({
            'from': from_address,
            'maxFeePerGas': max_fee_per_gas,
            'maxPriorityFeePerGas': max_priority_fee_per_gas,
            'nonce': self.w3.eth.get_transaction_count(from_address),
        })
        gas = self._estimate_gas(transaction)
        transaction['gas'] = gas
        return transaction
