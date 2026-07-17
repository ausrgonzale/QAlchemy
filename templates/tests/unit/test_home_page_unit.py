"""Unit tests for HomePage logic that does not require a live browser session."""

import pytest

from pages.home_page import HomePage


class _FakeLocator:
    """Simple locator stub used for unit tests."""

    def __init__(self, *, count_value=1, attrs=None):
        self._count_value = count_value
        self._attrs = attrs or {}

    def locator(self, _selector):
        return self

    def count(self):
        return self._count_value

    def get_attribute(self, name):
        return self._attrs.get(name)


class _FakePage:
    """Simple page stub that always returns a fake locator."""

    def locator(self, _selector):
        return _FakeLocator()


def _build_home_page():
    return HomePage(_FakePage())


def test_set_price_range_calls_min_then_max(monkeypatch):
    """set_price_range should apply the lower bound before the upper bound."""
    home_page = _build_home_page()
    calls = []

    def _set_min(value):
        calls.append(("min", value))

    def _set_max(value):
        calls.append(("max", value))

    monkeypatch.setattr(home_page, "set_min_price", _set_min)
    monkeypatch.setattr(home_page, "set_max_price", _set_max)

    home_page.set_price_range(25, 90)

    assert calls == [("min", 25), ("max", 90)]


def test_filter_by_brands_applies_each_brand(monkeypatch):
    """filter_by_brands should invoke filter_by_brand for every brand provided."""
    home_page = _build_home_page()
    applied = []

    monkeypatch.setattr(
        home_page, "filter_by_brand", lambda brand: applied.append(brand)
    )

    home_page.filter_by_brands(["A", "B", "C"])

    assert applied == ["A", "B", "C"]


def test_has_next_page_returns_false_when_button_missing():
    """has_next_page should be False when next-page control is absent."""
    home_page = _build_home_page()
    home_page.next_page = _FakeLocator(count_value=0)

    assert home_page.has_next_page() is False


def test_has_next_page_returns_false_when_disabled():
    """has_next_page should be False when pagination is disabled."""
    home_page = _build_home_page()
    home_page.next_page = _FakeLocator(count_value=1)
    home_page.next_page_container = _FakeLocator(attrs={"class": "page-item disabled"})

    assert home_page.has_next_page() is False


def test_has_next_page_returns_true_when_enabled():
    """has_next_page should be True when pagination control is enabled."""
    home_page = _build_home_page()
    home_page.next_page = _FakeLocator(count_value=1)
    home_page.next_page_container = _FakeLocator(attrs={"class": "page-item"})

    assert home_page.has_next_page() is True


def test_get_price_range_raises_when_slider_value_missing():
    """get_price_range should raise ValueError if either slider value is unavailable."""
    home_page = _build_home_page()
    home_page.min_price_slider = _FakeLocator(attrs={"aria-valuenow": None})
    home_page.max_price_slider = _FakeLocator(attrs={"aria-valuenow": "100"})

    with pytest.raises(ValueError, match="Could not read slider values"):
        home_page.get_price_range()
