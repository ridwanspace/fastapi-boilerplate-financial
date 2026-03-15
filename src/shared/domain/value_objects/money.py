from dataclasses import dataclass
from decimal import ROUND_HALF_EVEN, Decimal

from src.shared.domain.base_value_object import ValueObject


class InvalidMoneyAmountError(Exception):
    pass


class CurrencyMismatchError(Exception):
    pass


QUANTIZE_EXP = Decimal("0.0001")  # 4 decimal places for financial precision


@dataclass(frozen=True)
class Money(ValueObject):
    """
    Immutable monetary value.
    Uses Decimal with ROUND_HALF_EVEN (banker's rounding) for financial precision.
    Currency is stored as ISO 4217 code (e.g. "USD", "EUR").
    """

    amount: Decimal
    currency: str

    def __post_init__(self) -> None:
        if not isinstance(self.amount, Decimal):
            object.__setattr__(self, "amount", Decimal(str(self.amount)))
        if self.amount < Decimal("0"):
            raise InvalidMoneyAmountError(f"Money amount cannot be negative: {self.amount}")
        if not self.currency or len(self.currency) != 3:
            raise InvalidMoneyAmountError(f"Invalid currency code: {self.currency!r}")
        object.__setattr__(
            self,
            "amount",
            self.amount.quantize(QUANTIZE_EXP, rounding=ROUND_HALF_EVEN),
        )
        object.__setattr__(self, "currency", self.currency.upper())

    def add(self, other: "Money") -> "Money":
        self._assert_same_currency(other)
        return Money(amount=self.amount + other.amount, currency=self.currency)

    def subtract(self, other: "Money") -> "Money":
        self._assert_same_currency(other)
        result = self.amount - other.amount
        if result < Decimal("0"):
            raise InvalidMoneyAmountError(f"Subtraction would result in negative amount: {result}")
        return Money(amount=result, currency=self.currency)

    def multiply(self, factor: Decimal | int | str) -> "Money":
        factor = Decimal(str(factor))
        result = (self.amount * factor).quantize(QUANTIZE_EXP, rounding=ROUND_HALF_EVEN)
        return Money(amount=result, currency=self.currency)

    def is_zero(self) -> bool:
        return self.amount == Decimal("0")

    def is_greater_than(self, other: "Money") -> bool:
        self._assert_same_currency(other)
        return self.amount > other.amount

    def is_greater_than_or_equal(self, other: "Money") -> bool:
        self._assert_same_currency(other)
        return self.amount >= other.amount

    def _assert_same_currency(self, other: "Money") -> None:
        if self.currency != other.currency:
            raise CurrencyMismatchError(
                f"Cannot operate on different currencies: {self.currency} vs {other.currency}"
            )

    def __repr__(self) -> str:
        return f"Money({self.amount} {self.currency})"

    def __str__(self) -> str:
        return f"{self.amount:.4f} {self.currency}"

    @classmethod
    def zero(cls, currency: str) -> "Money":
        return cls(amount=Decimal("0"), currency=currency)

    @classmethod
    def of(cls, amount: str | int | float | Decimal, currency: str) -> "Money":
        return cls(amount=Decimal(str(amount)), currency=currency)
