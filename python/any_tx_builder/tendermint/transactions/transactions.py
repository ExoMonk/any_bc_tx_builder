import base64
import hashlib
from typing import List, Optional

import attr
from any_tx_builder.tendermint.coin import Coin_
from any_tx_builder.tendermint.transactions.fee import Fee_
from any_tx_builder.tendermint.key import PublicKey
from any_tx_builder.tendermint.messages import BaseTendermintData
from any_tx_builder.tendermint.proto import (
    AuthInfo,
    ModeInfo,
    ModeInfoSingle,
    SignerInfo,
    SignMode,
    Tx,
    TxBody,
)


@attr.s
class ModeInfoSingle_:
    mode: SignMode = attr.ib()

    def to_data(self) -> dict:
        return {"mode": self.mode.name}

    def to_proto(self) -> ModeInfoSingle:
        return ModeInfoSingle(mode=self.mode)


@attr.s
class ModeInfo_:
    single: Optional[ModeInfoSingle_] = attr.ib(default=None)

    def to_data(self) -> dict:
        return {"single": self.single.to_data()}

    def to_proto(self) -> ModeInfo:
        return ModeInfo(single=self.single.to_proto())


@attr.s
class SignerInfo_:
    sequence: int = attr.ib(converter=int)
    public_key: PublicKey = attr.ib()
    mode_info: ModeInfo_ = attr.ib()

    def to_data(self) -> dict:
        return {
            "public_key": self.public_key.to_data(),
            "mode_info": self.mode_info.to_data(),
            "sequence": self.sequence,
        }

    def to_proto(self) -> SignerInfo:
        return SignerInfo(
            public_key=self.public_key.pack_any(),
            mode_info=self.mode_info.to_proto(),
            sequence=self.sequence,
        )


@attr.s
class CreateTxOptions:
    msgs: List[BaseTendermintData] = attr.ib()
    fee: Optional[Fee_] = attr.ib(default=None)
    memo: Optional[str] = attr.ib(default=None)
    gas: Optional[str] = attr.ib(default=None)
    gas_prices: Optional[Coin_] = attr.ib(default=None)
    gas_adjustment: Optional[float] = attr.ib(default=0)
    fee_denoms: Optional[List[str]] = attr.ib(default=None)
    account_number: Optional[int] = attr.ib(default=None)
    sequence: Optional[int] = attr.ib(default=None)
    timeout_height: Optional[int] = attr.ib(default=None)
    sign_mode: Optional[SignMode] = attr.ib(default=None)


@attr.s
class TxBody_:
    messages: List[BaseTendermintData] = attr.ib()
    memo: Optional[str] = attr.ib(default="")
    timeout_height: int = attr.ib(default=0, converter=int)

    def to_data(self) -> dict:
        return {
            "messages": [m.to_data() for m in self.messages],
            "memo": self.memo,
            "timeout_height": self.timeout_height,
        }

    def to_proto(self) -> TxBody:
        return TxBody(
            messages=[m.pack_any() for m in self.messages],
            memo=self.memo,
            timeout_height=self.timeout_height,
        )

    @classmethod
    def from_data(cls, data: dict):
        return cls(
            [BaseTendermintData.from_data(m) for m in data["messages"]],
            data["memo"] if data["memo"] else "",
            data["timeout_height"] if data["timeout_height"] else 0,
        )

    def to_fireblocks_hex(self):
        return bytes(self.to_proto()).hex()

    def to_fireblocks_hash(self):
        return hashlib.sha256(bytes(self.to_proto())).hexdigest()


@attr.s
class AuthInfo_:
    signer_infos: List[SignerInfo_] = attr.ib(converter=list)
    fee: Fee_ = attr.ib()

    def to_data(self) -> dict:
        return {
            "signer_infos": [si.to_data() for si in self.signer_infos],
            "fee": self.fee.to_data(),
        }

    def to_proto(self) -> AuthInfo:
        return AuthInfo(
            signer_infos=[signer.to_proto() for signer in self.signer_infos],
            fee=self.fee.to_proto(),
        )

    def to_fireblocks_hex(self):
        return bytes(self.to_proto()).hex()

    def to_fireblocks_hash(self):
        return hashlib.sha256(bytes(self.to_proto())).hexdigest()


@attr.s
class Tx_:
    body: TxBody_ = attr.ib()
    auth_info: AuthInfo_ = attr.ib()
    signatures: List[bytes] = attr.ib(converter=list)

    def to_data(self) -> dict:
        return {
            "body": self.body.to_data(),
            "auth_info": self.auth_info.to_data(),
            "signatures": [base64.b64encode(sig).decode("ascii") for sig in self.signatures],
        }

    def append_empty_signatures(self, signers: List[SignerInfo_]):
        for signer_info in signers:
            self.auth_info.signer_infos.append(signer_info)
            self.signatures.append(b" ")

    def to_proto(self) -> Tx:
        return Tx(
            body=self.body.to_proto(),
            auth_info=self.auth_info.to_proto(),
            signatures=self.signatures,
        )

    def to_string_bytes(self) -> str:
        return base64.b64encode(bytes(self.to_proto())).decode()
