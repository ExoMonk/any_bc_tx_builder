import base64

from pydantic import BaseModel
from tendermint.proto import Any_pb, PubKey
from tendermint.types import AccAddress

class PublicKey(BaseModel):
    type: str
    key: bytes
    type_url: str = "/cosmos.crypto.secp256k1.PubKey"

    def to_data(self) -> dict:
        return {
            "@type": self.type,
            "key": base64.b64encode(self.key),
        }

    def to_proto(self) -> PubKey:
        return PubKey(key=self.key)

    def pack_any(self) -> Any_pb:
        return Any_pb(type_url=self.type_url, value=bytes(self.to_proto()))


class Account:
    chain: str
    acc_address: AccAddress
    public_key: PublicKey
    account_number: int
    sequence: int

    def __init__(self, chain: str, acc_address: AccAddress, pub_key: PublicKey, account_number: int, sequence: int):
        self.chain = chain
        self.acc_address = AccAddress(acc_address)
        self.public_key = PublicKey(type=pub_key["@type"], key=base64.b64decode(pub_key["key"]))
        self.account_number = account_number
        self.sequence = sequence

    @classmethod
    def from_data(cls, data: dict):
        return cls(
            data.get("chain"),
            data.get("address"),
            data.get("pub_key"),
            data.get("account_number"),
            data.get("sequence"),
        )
