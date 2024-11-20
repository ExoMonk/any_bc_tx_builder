from dataclasses import dataclass
from typing import List

from betterproto import (
    Enum,
    Message,
    bytes_field,
    enum_field,
    message_field,
    string_field,
    uint64_field,
)
from betterproto.lib.google.protobuf import Any as Any_pb

#
# Tendermint Tokens
#


@dataclass(eq=False, repr=False)
class Coin(Message):
    denom: str = string_field(1)
    amount: str = string_field(2)


#
# Accounts & Signatures
#


@dataclass(eq=False, repr=False)
class PubKey(Message):
    key: bytes = bytes_field(1)


class SignMode(Enum):
    SIGN_MODE_UNSPECIFIED = 0
    SIGN_MODE_DIRECT = 1
    SIGN_MODE_TEXTUAL = 2
    SIGN_MODE_DIRECT_AUX = 3
    SIGN_MODE_LEGACY_AMINO_JSON = 127
    SIGN_MODE_EIP_191 = 191
    UNRECOGNIZED = -1


@dataclass(eq=False, repr=False)
class ModeInfoSingle(Message):
    mode: "SignMode" = enum_field(1)


@dataclass(eq=False, repr=False)
class ModeInfo(Message):
    single: "ModeInfoSingle" = message_field(1, group="sum")


@dataclass(eq=False, repr=False)
class SignerInfo(Message):
    public_key: Any_pb = message_field(1)
    mode_info: "ModeInfo" = message_field(2)
    sequence: int = uint64_field(3)


@dataclass(eq=False, repr=False)
class SignDoc(Message):
    body_bytes: bytes = bytes_field(1)
    auth_info_bytes: bytes = bytes_field(2)
    chain_id: str = string_field(3)
    account_number: int = uint64_field(4)


#
# Messages
#


@dataclass(eq=False, repr=False)
class MsgDelegate(Message):
    delegator_address: str = string_field(1)
    validator_address: str = string_field(2)
    amount: "Coin" = message_field(3)


#
# Transactions
#


@dataclass(eq=False, repr=False)
class Tip(Message):
    amount: List["Coin"] = message_field(1)
    tipper: str = string_field(2)


@dataclass(eq=False, repr=False)
class Fee(Message):
    amount: List["Coin"] = message_field(1)
    gas_limit: int = uint64_field(2)
    payer: str = string_field(3)
    granter: str = string_field(4)


@dataclass(eq=False, repr=False)
class TxBody(Message):
    messages: List[Any_pb] = message_field(1)
    memo: str = string_field(2)
    timeout_height: int = uint64_field(3)
    extension_options: List[Any_pb] = message_field(1023)
    non_critical_extension_options: List[Any_pb] = message_field(2047)


@dataclass(eq=False, repr=False)
class AuthInfo(Message):
    signer_infos: List["SignerInfo"] = message_field(1)
    fee: "Fee" = message_field(2)
    tip: "Tip" = message_field(3)


@dataclass(eq=False, repr=False)
class Tx(Message):
    body: "TxBody" = message_field(1)
    auth_info: "AuthInfo" = message_field(2)
    signatures: List[bytes] = bytes_field(3)
