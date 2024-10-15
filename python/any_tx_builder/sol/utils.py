from construct import Switch  # type: ignore
from construct import Int32ul, Pass, Int64ul  # type: ignore
from construct import Bytes, Struct, Container
from enum import IntEnum
from solders.pubkey import Pubkey # type: ignore
from typing import NamedTuple, Dict


class Authorized(NamedTuple):
    """Define who is authorized to change a stake."""
    staker: Pubkey
    withdrawer: Pubkey

    def as_bytes_dict(self) -> Dict:
        return {
            'staker': bytes(self.staker),
            'withdrawer': bytes(self.withdrawer),
        }

class Lockup(NamedTuple):
    """Lockup for a stake account."""
    unix_timestamp: int
    epoch: int
    custodian: Pubkey

    @classmethod
    def decode_container(cls, container: Container):
        return Lockup(
            unix_timestamp=container['unix_timestamp'],
            epoch=container['epoch'],
            custodian=Pubkey(container['custodian']),
        )

    def as_bytes_dict(self) -> Dict:
        self_dict = self._asdict()
        self_dict['custodian'] = bytes(self_dict['custodian'])
        return self_dict

class InstructionType(IntEnum):
    """Stake Instruction Types."""

    INITIALIZE = 0
    AUTHORIZE = 1
    DELEGATE_STAKE = 2
    SPLIT = 3
    WITHDRAW = 4
    DEACTIVATE = 5
    SET_LOCKUP = 6
    MERGE = 7
    AUTHORIZE_WITH_SEED = 8
    INITIALIZE_CHECKED = 9
    AUTHORIZED_CHECKED = 10
    AUTHORIZED_CHECKED_WITH_SEED = 11
    SET_LOCKUP_CHECKED = 12


PUBLIC_KEY_LAYOUT = Bytes(32)


LOCKUP_LAYOUT = Struct(
    "unix_timestamp" / Int64ul,
    "epoch" / Int64ul,
    "custodian" / PUBLIC_KEY_LAYOUT,
)

AUTHORIZED_LAYOUT = Struct(
    "staker" / PUBLIC_KEY_LAYOUT,
    "withdrawer" / PUBLIC_KEY_LAYOUT,
)

INITIALIZE_LAYOUT = Struct(
    "authorized" / AUTHORIZED_LAYOUT,
    "lockup" / LOCKUP_LAYOUT,
)


AUTHORIZE_LAYOUT = Struct(
    "new_authority" / PUBLIC_KEY_LAYOUT,
    "stake_authorize" / Int32ul,
)


INSTRUCTIONS_LAYOUT = Struct(
    "instruction_type" / Int32ul,
    "args"
    / Switch(
        lambda this: this.instruction_type,
        {
            InstructionType.INITIALIZE: INITIALIZE_LAYOUT,
            InstructionType.AUTHORIZE: AUTHORIZE_LAYOUT,
            InstructionType.DELEGATE_STAKE: Pass,
            InstructionType.SPLIT: Pass,
            InstructionType.WITHDRAW: Pass,
            InstructionType.DEACTIVATE: Pass,
            InstructionType.SET_LOCKUP: Pass,
            InstructionType.MERGE: Pass,
            InstructionType.AUTHORIZE_WITH_SEED: Pass,
            InstructionType.INITIALIZE_CHECKED: Pass,
            InstructionType.AUTHORIZED_CHECKED: Pass,
            InstructionType.AUTHORIZED_CHECKED_WITH_SEED: Pass,
            InstructionType.SET_LOCKUP_CHECKED: Pass,
        },
    ),
)
