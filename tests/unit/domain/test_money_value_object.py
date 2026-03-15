from dataclasses import FrozenInstanceError
from decimal import Decimal

import pytest

from src.shared.domain.value_objects.money import (
    CurrencyMismatchError,
    InvalidMoneyAmountError,
    Money,
)


@pytest.mark.unit
class TestMoneyCreation:
    def test_creates_with_valid_values(self):
        m = Money.of("100.50", "USD")
        assert m.amount == Decimal("100.5000")
        assert m.currency == "USD"

    def test_normalizes_currency_to_uppercase(self):
        m = Money.of(100, "usd")
        assert m.currency == "USD"

    def test_stores_4_decimal_places(self):
        m = Money.of("99.999999", "EUR")
        assert m.amount == Decimal("100.0000")  # rounds HALF_EVEN

    def test_rejects_negative_amount(self):
        with pytest.raises(InvalidMoneyAmountError):
            Money.of("-1", "USD")

    def test_rejects_invalid_currency_code(self):
        with pytest.raises(InvalidMoneyAmountError):
            Money(amount=Decimal("10"), currency="US")

    def test_zero_factory(self):
        m = Money.zero("GBP")
        assert m.is_zero()
        assert m.currency == "GBP"


@pytest.mark.unit
class TestMoneyArithmetic:
    def test_add_same_currency(self):
        result = Money.of(100, "USD").add(Money.of(50, "USD"))
        assert result.amount == Decimal("150.0000")
        assert result.currency == "USD"

    def test_add_different_currency_raises(self):
        with pytest.raises(CurrencyMismatchError):
            Money.of(100, "USD").add(Money.of(50, "EUR"))

    def test_subtract_same_currency(self):
        result = Money.of(100, "USD").subtract(Money.of(30, "USD"))
        assert result.amount == Decimal("70.0000")

    def test_subtract_resulting_in_negative_raises(self):
        with pytest.raises(InvalidMoneyAmountError):
            Money.of(10, "USD").subtract(Money.of(20, "USD"))

    def test_multiply_by_factor(self):
        result = Money.of(100, "USD").multiply(Decimal("1.05"))
        assert result.amount == Decimal("105.0000")

    def test_is_greater_than(self):
        assert Money.of(100, "USD").is_greater_than(Money.of(50, "USD"))
        assert not Money.of(50, "USD").is_greater_than(Money.of(100, "USD"))

    def test_equality_by_value(self):
        assert Money.of(100, "USD") == Money.of(100, "USD")
        assert Money.of(100, "USD") != Money.of(100, "EUR")

    def test_immutability(self):
        m = Money.of(100, "USD")
        with pytest.raises(FrozenInstanceError):
            m.amount = Decimal("200")  # type: ignore[misc]
