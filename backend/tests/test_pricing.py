from decimal import Decimal

import pytest

from app.services.pricing import get_strategy
from app.services.pricing.cheque import ChequeStrategy
from app.services.pricing.duplicata import DuplicataStrategy


class TestDuplicataStrategy:
    def setup_method(self):
        self.strategy = DuplicataStrategy()

    def test_spread_is_one_point_five_percent(self):
        assert self.strategy.get_spread() == Decimal("0.015")

    def test_present_value_12_months(self):
        # PV = 10000 / 1.025^12 = 10000 / 1.34488882... = 7435.55...
        pv = self.strategy.calculate_present_value(
            face_value=Decimal("10000"),
            base_rate=Decimal("0.01"),
            term_months=12,
        )
        expected = (Decimal("10000") / Decimal("1.025") ** 12).quantize(
            Decimal("0.00000001")
        )
        assert pv == expected

    def test_present_value_1_month(self):
        # PV = 1000 / 1.025 = 975.60975609...
        pv = self.strategy.calculate_present_value(
            face_value=Decimal("1000"),
            base_rate=Decimal("0.01"),
            term_months=1,
        )
        expected = (Decimal("1000") / Decimal("1.025")).quantize(
            Decimal("0.00000001")
        )
        assert pv == expected

    def test_present_value_zero_term(self):
        # PV = 1000 / 1.025^0 = 1000.00000000
        pv = self.strategy.calculate_present_value(
            face_value=Decimal("1000"),
            base_rate=Decimal("0.01"),
            term_months=0,
        )
        assert pv == Decimal("1000.00000000")


class TestChequeStrategy:
    def setup_method(self):
        self.strategy = ChequeStrategy()

    def test_spread_is_two_point_five_percent(self):
        assert self.strategy.get_spread() == Decimal("0.025")

    def test_present_value_6_months(self):
        # PV = 5000 / 1.045^6 = 5000 / 1.30226012... = 3838.77...
        pv = self.strategy.calculate_present_value(
            face_value=Decimal("5000"),
            base_rate=Decimal("0.02"),
            term_months=6,
        )
        expected = (Decimal("5000") / Decimal("1.045") ** 6).quantize(
            Decimal("0.00000001")
        )
        assert pv == expected

    def test_higher_spread_means_lower_pv(self):
        """Cheque (2.5%) should give lower PV than Duplicata (1.5%) for same inputs."""
        duplicata = DuplicataStrategy()
        face_value = Decimal("10000")
        base_rate = Decimal("0.01")
        term = 6

        pv_duplicata = duplicata.calculate_present_value(face_value, base_rate, term)
        pv_cheque = self.strategy.calculate_present_value(face_value, base_rate, term)

        assert pv_cheque < pv_duplicata


class TestGetStrategy:
    def test_returns_duplicata_strategy(self):
        strategy = get_strategy("Duplicata Mercantil")
        assert isinstance(strategy, DuplicataStrategy)

    def test_returns_cheque_strategy(self):
        strategy = get_strategy("Cheque Pré-datado")
        assert isinstance(strategy, ChequeStrategy)

    def test_unknown_type_raises_value_error(self):
        with pytest.raises(ValueError, match="Unknown receivable type"):
            get_strategy("Tipo Inexistente")
