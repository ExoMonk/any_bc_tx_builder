import json
from abc import abstractmethod
import attr
from betterproto import Message

from tendermint.coin import Coin_
from tendermint.proto import Any_pb, MsgDelegate
from tendermint.types import AccAddress, ValAddress
from tendermint.utils import dict_to_data


class BaseTendermintData(Message):
    type: str
    type_url: str

    def to_data(self) -> dict:
        data = dict_to_data(attr.asdict(self))
        data.update({"@type": self.type_url})
        return data

    def to_json(self) -> str:
        return json.dumps(self.to_data(), sort_keys=True, separators=(",", ":"))

    @abstractmethod
    def to_proto(self):
        pass

    def pack_any(self) -> Any_pb:
        return Any_pb(type_url=self.type_url, value=bytes(self.to_proto()))


@attr.s
class MsgDelegate_(BaseTendermintData):
    type_url = "/cosmos.staking.v1beta1.MsgDelegate"
    action = "delegate"

    delegator_address: AccAddress = attr.ib()
    validator_address: ValAddress = attr.ib()
    amount: Coin_ = attr.ib(converter=Coin_.parse)

    def to_proto(self) -> MsgDelegate:
        return MsgDelegate(
            delegator_address=self.delegator_address,
            validator_address=self.validator_address,
            amount=self.amount.to_proto(),
        )
