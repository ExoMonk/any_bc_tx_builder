from typing import Optional

import attr
from any_tx_builder.tendermint.key import PublicKey
from any_tx_builder.tendermint.transactions.transactions import AuthInfo_, TxBody_
from any_tx_builder.tendermint.proto import SignDoc, SignMode


@attr.s
class SignOptions:
    account_number: int = attr.ib(converter=int)
    sequence: int = attr.ib(converter=int)
    sign_mode: SignMode = attr.ib()
    chain_id: str = attr.ib()


@attr.s
class SignDoc_:
    chain_id: str = attr.ib()
    account_number: int = attr.ib(converter=int)
    sequence: int = attr.ib(converter=int)
    auth_info: AuthInfo_ = attr.ib()
    tx_body: TxBody_ = attr.ib()

    def to_data(self) -> dict:
        return {
            "chain_id": self.chain_id,
            "account_number": self.account_number,
            "sequence": self.sequence,
            "auth_info": self.auth_info.to_data(),
            "tx_body": self.tx_body.to_data(),
        }

    def to_proto(self) -> SignDoc:
        return SignDoc(
            body_bytes=bytes(self.tx_body.to_proto()),
            auth_info_bytes=bytes(self.auth_info.to_proto()),
            chain_id=self.chain_id,
            account_number=self.account_number,
        )

    def to_bytes(self) -> bytes:
        return bytes(self.to_proto())


@attr.s
class Single:
    mode: SignMode = attr.ib()
    signature: bytes = attr.ib()

    def to_data(self) -> dict:
        return {"mode": self.mode, "signature": self.signature}


@attr.s
class Descriptor:
    single: Optional[Single] = attr.ib(default=None)

    def to_data(self) -> dict:
        typ = "single"
        dat = self.single.to_data()
        return {typ: dat}


@attr.s
class SignatureV2:
    public_key: PublicKey = attr.ib()
    data: Descriptor = attr.ib()
    sequence: int = attr.ib(converter=int)

    def to_data(self) -> dict:
        return {
            "public_key": self.public_key.to_data(),
            "data": self.data.to_data(),
            "sequence": self.sequence,
        }
