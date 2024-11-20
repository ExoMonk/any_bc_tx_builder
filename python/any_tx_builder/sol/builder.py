from solana.rpc.api import Client
from solana.transaction import Transaction
from solana.constants import SYSTEM_PROGRAM_ID
from solders.keypair import Keypair # type: ignore
from solders.pubkey import Pubkey # type: ignore
from solders.system_program import transfer, TransferParams
from solders.instruction import Instruction, AccountMeta # type: ignore
from solders.system_program import create_account, CreateAccountParams # type: ignore
from spl.token.constants import TOKEN_PROGRAM_ID
from spl.token.instructions import transfer as spl_transfer, TransferParams as SplTransferParams, get_associated_token_address

from typing import Union
from any_tx_builder.builder_base import BaseTransactionBuilder
from any_tx_builder.sol.utils import INSTRUCTIONS_LAYOUT, InstructionType, Authorized, Lockup

class SolanaTransactionBuilder(BaseTransactionBuilder):

    LAMPORTS_PER_SOL = 1_000_000_000

    def __init__(self, client: Client):
        self.client = client

    def _get_recent_blockhash(self):
        # Solana doesn't use gas, but we can get the recent blockhash
        return self.client.get_latest_blockhash()
    
    def _encode_instruction_data(self, function_name: str, function_args: list) -> bytes:
        # This is a simplified encoding. You might need to adjust based on your specific program's requirements
        encoded_name = function_name.encode()
        encoded_args = b''.join(str(arg).encode() for arg in function_args)
        return encoded_name + b':' + encoded_args

    def build_contract_transaction(self, from_address: str, program_id: Union[str, Pubkey], function_name: str, function_args: list, value: int = 0) -> Transaction:
        # Convert addresses to Pubkey objects
        from_pubkey = Pubkey.from_string(from_address)
        if isinstance(program_id, str):
            program_pubkey = Pubkey.from_string(program_id)
        else:
            program_pubkey = program_id

        recent_blockhash = self._get_recent_blockhash()

        # Create transaction
        transaction = Transaction()
        transaction.recent_blockhash = recent_blockhash.value.blockhash

        # Create instruction data
        instruction_data = self._encode_instruction_data(function_name, function_args)
        transaction.add(Instruction(
            program_id=program_pubkey,
            accounts=[AccountMeta(pubkey=from_pubkey, is_signer=True, is_writable=True)],
            data=instruction_data
        ))

        # If value is provided, add a transfer instruction
        if value > 0:
            transfer_instruction = transfer(TransferParams(
                from_pubkey=from_pubkey,
                to_pubkey=program_pubkey,
                lamports=value
            ))
            transaction.add(transfer_instruction)

        return transaction

    def sign_transaction(self, transaction: Transaction, private_key: str, additional_signer: Keypair = None) -> Transaction:
        keypair = Keypair.from_base58_string(private_key)
        if additional_signer:
            transaction.sign_partial(keypair)
            transaction.sign_partial(additional_signer)
        else:
            transaction.sign(keypair)
        return transaction 
    
    def broadcast_transaction(self, transaction: Transaction) -> str:
        tx_sent = self.client.send_transaction(transaction)
        print(f"✅ Transaction sent: {tx_sent}")
        return tx_sent

    def is_transaction_broadcasted(self, tx_signature: str) -> bool:
        try:
            tx_status = self.client.get_transaction(tx_signature)
            return tx_status is not None
        except Exception as e:
            print(e)
            return False

class SolanaStakingTransactionBuilder(SolanaTransactionBuilder):

    def __init__(self, client: Client):
        self.client = client

    def build_staking_transaction(self, from_address: str, validator_address: str, staking_amount: int) -> tuple[Transaction, Keypair]:
        # Generating pubkey for the stake account
        wallet_pubkey = Pubkey.from_string(from_address)
        stake_account_keypair = Keypair()
        stake_account_pubkey = stake_account_keypair.pubkey()

        validator_pubkey = Pubkey.from_string(validator_address)

        amount = int(staking_amount * self.LAMPORTS_PER_SOL)

        # Create transaction
        stake_account_transaction = Transaction()

        # Create account instruction
        create_account_ix = create_account(CreateAccountParams(
            from_pubkey=wallet_pubkey,
            to_pubkey=stake_account_pubkey,
            lamports=amount,
            space=200,  # Stake account size
            owner=Pubkey.from_string("Stake11111111111111111111111111111111111111")
        ))

        # Initialize stake instruction

        init_stake_ix = Instruction(
            accounts=[
                AccountMeta(pubkey=stake_account_pubkey, is_signer=False, is_writable=True),
                AccountMeta(pubkey=Pubkey.from_string("SysvarRent111111111111111111111111111111111"), is_signer=False, is_writable=False),
            ],
            program_id=Pubkey.from_string("Stake11111111111111111111111111111111111111"),
            data=INSTRUCTIONS_LAYOUT.build(
                dict(
                    instruction_type=InstructionType.INITIALIZE,
                    args=dict(
                        authorized=Authorized(staker=wallet_pubkey, withdrawer=wallet_pubkey).as_bytes_dict(),
                        lockup=Lockup(unix_timestamp=0, epoch=0, custodian=SYSTEM_PROGRAM_ID).as_bytes_dict(),
                    ),
                )
            )
        )

        # Deposit stake instruction
        deposit_stake_ix = Instruction(
            accounts=[
                AccountMeta(pubkey=stake_account_pubkey, is_signer=False, is_writable=True),
                AccountMeta(pubkey=validator_pubkey, is_signer=False, is_writable=False),
                AccountMeta(pubkey=Pubkey.from_string("SysvarC1ock11111111111111111111111111111111"), is_signer=False, is_writable=False),
                AccountMeta(pubkey=Pubkey.from_string("SysvarStakeHistory1111111111111111111111111"), is_signer=False, is_writable=False),
                AccountMeta(pubkey=Pubkey.from_string("StakeConfig11111111111111111111111111111111"), is_signer=False, is_writable=False),
                AccountMeta(pubkey=wallet_pubkey, is_signer=True, is_writable=False),
            ],
            program_id=Pubkey.from_string("Stake11111111111111111111111111111111111111"),
            data=INSTRUCTIONS_LAYOUT.build(
                dict(
                    instruction_type=InstructionType.DELEGATE_STAKE,
                    args=None,
                )
            )
        )

        stake_account_transaction.add(create_account_ix)
        stake_account_transaction.add(init_stake_ix)
        stake_account_transaction.add(deposit_stake_ix)

        latest_blockhash = self._get_recent_blockhash()
        stake_account_transaction.recent_blockhash = latest_blockhash.value.blockhash
        stake_account_transaction.fee_payer = wallet_pubkey   

        print(f"Staking {staking_amount} SOL to [{stake_account_pubkey}]")
        #payload = bytes(stake_account_transaction.message()).hex()
        return stake_account_transaction, stake_account_keypair

class SolanaSwapper(SolanaTransactionBuilder):

    RAYDIUM_AMM_PROGRAM_ID = Pubkey.from_string("675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8")

    def __init__(self, client: Client):
        self.client = client

    def get_token_decimals(self, token_address: str) -> int:
        try:
            # Get the mint account info
            mint_info = self.client.get_account_info(Pubkey.from_string(token_address))
            if mint_info.value is None:
                raise ValueError(f"Token mint {token_address} not found")
            decimals = mint_info.value.data[44]
            return decimals
        except Exception as e:
            print(f"Error getting token decimals: {e}")
            raise

    def transfer_sol(self, from_address: str, to_address: str, amount_sol: float) -> Transaction:
        from_pubkey = Pubkey.from_string(from_address)
        to_pubkey = Pubkey.from_string(to_address)
        lamports = int(amount_sol * self.LAMPORTS_PER_SOL)
        transfer_instruction = transfer(TransferParams(
            from_pubkey=from_pubkey,
            to_pubkey=to_pubkey,
            lamports=lamports
        ))
        transaction = Transaction()
        transaction.recent_blockhash = self._get_recent_blockhash().value.blockhash
        transaction.add(transfer_instruction)
        return transaction

    def transfer(self, from_address: str, to_address: str, token_address: str, amount: int) -> Transaction:
        from_pubkey = Pubkey.from_string(from_address)
        # Get the associated token accounts for sender and receiver
        from_token_account = get_associated_token_address(from_pubkey, Pubkey.from_string(token_address))
        to_token_account = get_associated_token_address(Pubkey.from_string(to_address), Pubkey.from_string(token_address))

        decimals = self.get_token_decimals(token_address)
        amount_in_tokens = amount * (10 ** decimals)
        transfer_ix = spl_transfer(
            SplTransferParams(
                source=from_token_account,
                dest=to_token_account,
                program_id=TOKEN_PROGRAM_ID,
                owner=from_pubkey,
                amount=amount_in_tokens
            )
        )
        transaction = Transaction()
        transaction.recent_blockhash = self._get_recent_blockhash().value.blockhash
        transaction.fee_payer = from_pubkey
        transaction.add(transfer_ix)
        return transaction

