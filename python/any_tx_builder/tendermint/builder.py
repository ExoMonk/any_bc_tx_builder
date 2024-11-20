import base64
import copy
import hashlib
from typing import List

from ecdsa import SECP256k1, SigningKey
from ecdsa.util import sigencode_string_canonize
from bip32utils import BIP32_HARDEN, BIP32Key
from mnemonic import Mnemonic
from tendermint.client import TendermintClient
from tendermint.key import PublicKey
from tendermint.transactions.signature import (
    Descriptor,
    SignatureV2,
    SignDoc_,
    SignOptions,
    Single,
)
from tendermint.transactions import (
    AuthInfo_,
    CreateTxOptions,
    ModeInfo_,
    ModeInfoSingle_,
    SignerInfo_,
    Tx_,
    TxBody_,
)
from tendermint.proto import SignMode
from tendermint.types import AccAddress
from tendermint.key import Account


class Wallet:
    def __init__(self, chain: str, client: TendermintClient, acc_address: AccAddress):
        self.client: TendermintClient = client
        self.key: Account = Account.from_data(self.client.get_account_info(acc_address))
        self.private_key = None

    def set_private_key(self, mnemonic: str, coin_type: int, account: int, index: int):
        seed = Mnemonic("english").to_seed(mnemonic)
        root = BIP32Key.fromEntropy(seed)
        child = (
            root.ChildKey(44 + BIP32_HARDEN)
            .ChildKey(coin_type + BIP32_HARDEN)
            .ChildKey(account + BIP32_HARDEN)
            .ChildKey(0)
            .ChildKey(index)
        )
        self.private_key = child.PrivateKey()
        self.key.public_key = PublicKey(
            type="/cosmos.crypto.secp256k1.PubKey",
            key=SigningKey.from_string(self.private_key, curve=SECP256k1).get_verifying_key().to_string("compressed")
        )

    def account_number_and_sequence(self) -> dict:
        account_info = self.client.get_account_info(self.key.acc_address)
        return {
            "account_number": account_info.get("account_number"),
            "sequence": account_info.get("sequence"),
        }

    def sign(self, payload: bytes) -> bytes:
        sk = SigningKey.from_string(self.private_key, curve=SECP256k1)
        return sk.sign_deterministic(
            payload,
            hashfunc=hashlib.sha256,
            sigencode=sigencode_string_canonize,
        )

    def build_tx(self, tx_options: CreateTxOptions) -> dict:
        signer_data: List[SignerInfo_] = [
            SignerInfo_(
                self.key.sequence, self.key.public_key, ModeInfo_(single=ModeInfoSingle_(SignMode.SIGN_MODE_DIRECT))
            )
        ]

        if tx_options.fee is None:
            tx_options.fee = self.client.estimate_fee(signer_data, tx_options)

        return Tx_(
            TxBody_(tx_options.msgs, tx_options.memo or "", tx_options.timeout_height or 0),
            AuthInfo_([], tx_options.fee),
            [],
        )

    def sign_tx(self, tx: Tx_):
        sign_options = SignOptions(
            account_number=self.key.account_number,
            sequence=self.key.sequence,
            chain_id=self.chain_id,
            sign_mode=SignMode.SIGN_MODE_DIRECT,
        )
        signedTx = Tx_(
            body=tx.body,
            auth_info=AuthInfo_(signer_infos=[], fee=tx.auth_info.fee),
            signatures=[],
        )
        sign_doc = SignDoc_(
            chain_id=sign_options.chain_id,
            account_number=sign_options.account_number,
            sequence=sign_options.sequence,
            auth_info=signedTx.auth_info,
            tx_body=signedTx.body,
        )

        si_backup = copy.deepcopy(sign_doc.auth_info.signer_infos)
        sign_doc.auth_info.signer_infos = [
            SignerInfo_(
                public_key=self.key.public_key,
                sequence=sign_doc.sequence,
                mode_info=ModeInfo_(single=ModeInfoSingle_(mode=SignMode.SIGN_MODE_DIRECT)),
            )
        ]
        signature = self.sign(sign_doc.to_bytes())
        # restore
        sign_doc.auth_info.signer_infos = si_backup
        final_signature = SignatureV2(
            public_key=self.key.public_key,
            data=Descriptor(single=Single(mode=SignMode.SIGN_MODE_DIRECT, signature=signature)),
            sequence=sign_doc.sequence,
        )

        sig_data: Single = final_signature.data.single
        for sig in tx.signatures:
            signedTx.signatures.append(sig)
        signedTx.signatures.append(sig_data.signature)
        for infos in tx.auth_info.signer_infos:
            signedTx.auth_info.signer_infos.append(infos)
        signedTx.auth_info.signer_infos.append(
            SignerInfo_(
                public_key=final_signature.public_key,
                sequence=final_signature.sequence,
                mode_info=ModeInfo_(single=ModeInfoSingle_(mode=sig_data.mode)),
            )
        )
        return signedTx

    def broadcast(self, tx: Tx_):
        return self.client._broadcast(tx)
