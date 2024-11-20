from typing import NewType

AccAddress = NewType("AccAddress", str)
AccAddress.__doc__ = """Tendermint Bech32 Account Address -- type alias of str."""

ValAddress = NewType("ValAddress", str)
ValAddress.__doc__ = """Tendermint Bech32 Validator Address -- type alias of str."""
