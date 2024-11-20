import re
from typing import Union

import attr
from any_tx_builder.tendermint.proto import Coin


@attr.s(frozen=True)
class Coin_:
    denom: str = attr.ib()
    amount: str = attr.ib()

    def parse(arg: Union[str, dict]):
        if isinstance(arg, Coin_):
            return arg
        elif isinstance(arg, str):
            return Coin_.from_str(arg)
        else:
            return Coin_.from_data(arg)

    @classmethod
    def from_data(cls, data: dict):
        return cls(data["denom"], data["amount"])

    @classmethod
    def from_str(cls, string: str):
        pattern = r"^(\-?[0-9]+(\.[0-9]+)?)([0-9a-zA-Z/]+)$"
        match = re.match(pattern, string)
        if match is None:
            raise ValueError(f"failed to parse Coin: {string}")
        else:
            return cls(match.group(3), match.group(1))

    def to_dec_coin(self):
        return Coin_(self.denom, self.amount)

    def to_data(self) -> dict:
        return {"denom": self.denom, "amount": str(self.amount)}

    def to_proto(self) -> Coin:
        return Coin(denom=self.denom, amount=str(self.amount))

    def div(self, divisor: float):
        return Coin_(self.denom, str(int(float(self.amount) // float(divisor))))

    def mul(self, multiplier: float):
        return Coin_(self.denom, str(int(float(self.amount) * float(multiplier))))
