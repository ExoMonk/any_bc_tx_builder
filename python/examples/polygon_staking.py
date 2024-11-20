import os
from web3.exceptions import ContractLogicError
from any_tx_builder.evm.connection import setup_web3_connection
from any_tx_builder.evm.builder import PolygonStakingTransactionBuilder
from dotenv import load_dotenv

# Import the contract address
from any_tx_builder.evm.config import VALIDATOR_ADDRESS, POLYGON_STAKING_CONTRACT

# Load environment variables
load_dotenv()

def main():
    # Setup Web3 connection
    w3 = setup_web3_connection()
    builder = PolygonStakingTransactionBuilder(w3)
    
    from_address = os.getenv('EVM_WALLET_ADDRESS')
    account = w3.eth.account.from_key(os.getenv('EVM_PRIVATE_KEY'))
    assert account.address == from_address

    functions = builder.list_contract_functions(POLYGON_STAKING_CONTRACT)

    # 
    # Polygon Staking Module
    #

    # Delegation
    validator_address = VALIDATOR_ADDRESS
    staking_amount = 1000000000000000
    unstaking_amount = int(staking_amount / 2)

    allowance_tx = builder.build_POL_allowance_transaction(
        from_address,
        staking_amount 
    )
    print("✨ Allowance transaction built")
    print(allowance_tx)
    
    # Build the transaction
    try:
        staking_transaction = builder.build_staking_transaction(
            from_address,
            staking_amount,
            validator_address
        )
        print("✨ Stake Transaction built")
        print(staking_transaction)
    except ContractLogicError as e:
        print(f" ❌ Couldn't build staking transaction: {str(e)}")

    # Unstake
    try:
        part_unstake_transaction = builder.build_unstaking_transaction(
            from_address,
            validator_address,
            unstaking_amount
        )
        print("✨ Unstake Transaction built")
        print(part_unstake_transaction)
    except ContractLogicError as e:
        print(f" ❌ Couldn't build unstaking transaction: {str(e)}")
    
    # Restake
    try:
        restake_transaction = builder.build_restaking_transaction(
            from_address,
            validator_address
        )
        print("✨ RestakeTransaction built")
        print(restake_transaction)
    except ContractLogicError as e:
        print(f" ❌ Couldn't build restaking transaction: {str(e)}")

    # Withdraw Rewards
    try:
        withdraw_rewards_transaction = builder.build_withdraw_rewards_transaction(
            from_address,
            validator_address
        )
        print("✨ Withdraw Rewards Transaction built")
        print(withdraw_rewards_transaction)
    except ContractLogicError as e:
        print(f" ❌ Couldn't build withdraw rewards transaction: {str(e)}")

    # Check if the transaction has been broadcasted

    signed_txn = w3.eth.account.sign_transaction(allowance_tx, account.key)
    print("-----------🏃 TX SENT-----------------")
    print(bytes.fromhex(signed_txn.raw_transaction.hex()))
    sent = w3.eth.send_raw_transaction(bytes.fromhex(signed_txn.raw_transaction.hex()))
    tx_hash = w3.to_hex(w3.keccak(signed_txn.raw_transaction))
    print(f"✨ Transaction hash: {tx_hash}")
    print("-------------------------------------")

    is_broadcasted = builder.is_transaction_broadcasted(signed_txn.hash)
    print(f"✨ Transaction broadcasted: {is_broadcasted}")

    liq_rew = builder.call_contract_abi(validator_address, "getLiquidRewards", [from_address])
    print(f"💸 Liquid Rewards: {liq_rew}")

if __name__ == "__main__":
    main()
