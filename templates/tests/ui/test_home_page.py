"""UI tests for Toolshop home page filters, search, and sorting."""

import re

import pytest
from playwright.sync_api import expect

from pages.home_page import HomePage

# Shared brand values used in brand-filtering tests.
SELECTED_BRANDS = ["ForgeFlex Tools", "MightyCraft Hardware"]


# ========== Smoke / Navigation ==========


def test_home_page_title(home_page):
    """Home page should render with the expected title pattern."""
    home_page.open()

    # Accept dynamic semantic version text in the page title.
    expect(home_page.page).to_have_title(
        re.compile(r"Practice Software Testing - Toolshop - v\d+\.\d+")
    )


# ========== Price Filtering ==========


def test_filter_by_price_range(home_page):
    """Keyboard-based price adjustment should update slider values."""
    home_page.open()

    # Drive both slider handles to the target range.
    home_page.set_min_price(50)
    home_page.set_max_price(110)

    # Validate the slider state and product data are both constrained to the range.
    min_price, max_price = home_page.get_price_range()

    assert min_price == 50
    assert max_price == 110


def test_can_drag_min_price_slider(page):
    """Dragging the min slider should increase the minimum slider value."""
    home_page = HomePage(page)

    home_page.open()

    starting_min, _ = home_page.get_price_range()
    home_page.drag_min_price(40)
    ending_min, _ = home_page.get_price_range()

    assert ending_min > starting_min


def test_can_adjust_min_price_with_keyboard(home_page):
    """Arrow-key adjustments should move the min slider by exact increments."""
    home_page.open()

    starting_min, _ = home_page.get_price_range()
    home_page.set_min_price(starting_min + 10)
    ending_min, _ = home_page.get_price_range()

    assert ending_min == starting_min + 10


def test_dragging_min_price_filters_products(home_page):
    """Dragging min slider should constrain visible products by min price."""
    home_page.open()

    home_page.drag_min_price(40)
    home_page.wait_for_products_to_update()

    actual_min, _ = home_page.get_price_range()
    prices = home_page.get_product_prices()

    assert prices
    assert all(price >= actual_min for price in prices)


# ========== Sorting ==========


def test_sort_price_low_high(home_page):
    """Price ascending sort should render products in numeric ascending order."""
    home_page.open()

    home_page.select_sort_option("price,asc")
    prices = home_page.get_product_prices()

    # Verify ascending order exactly matches Python's sorted output.
    assert prices == sorted(prices)


def test_co2_ratings_asc(home_page):
    """CO2 rating ascending sort should render ratings in ascending order."""
    home_page.open()

    home_page.select_sort_option("co2_rating,asc")
    ratings = home_page.get_co2_ratings()

    # CO2 badges should be rendered in ascending label order.
    assert ratings == sorted(ratings)


def test_co2_ratings_desc(home_page):
    """CO2 rating descending sort should render ratings in reverse order."""
    home_page.open()

    home_page.select_sort_option("co2_rating,desc")
    ratings = home_page.get_co2_ratings()

    # CO2 badges should be rendered in descending label order.
    assert ratings == sorted(ratings, reverse=True)


# ========== Search ==========


def test_search_functionality(home_page):
    """Search should narrow product names to the requested term."""
    home_page.open()

    # Trigger server-side search and validate only matching names remain.
    home_page.search_products("hammer")
    products = home_page.get_product_names()

    assert products

    # Every returned product should include the search term.
    assert all("hammer" in product.lower() for product in products)


# ========== Category Filtering ==========


def test_filter_by_category(home_page):
    """Selecting one category should reduce the visible product set."""
    home_page.open()

    all_products = home_page.get_product_names()

    home_page.filter_by_category("Hammer")
    home_page.wait_for_products_to_update()

    expect(home_page.category_checkbox("Hammer")).to_be_checked()

    filtered_products = home_page.get_product_names()

    assert filtered_products
    assert filtered_products != all_products


def test_filter_by_multiple_categories(home_page):
    """Selecting multiple categories should keep those filters checked."""
    home_page.open()

    all_products = home_page.get_all_product_names()

    home_page.filter_by_category("Hammer")
    home_page.filter_by_category("Sander")
    home_page.filter_by_category("Tool Belt")

    home_page.wait_for_products_to_update()

    expect(home_page.category_checkbox("Hammer")).to_be_checked()
    expect(home_page.category_checkbox("Sander")).to_be_checked()
    expect(home_page.category_checkbox("Tool Belt")).to_be_checked()

    filtered_products = home_page.get_all_product_names()

    assert filtered_products
    assert filtered_products != all_products


# ========== Brand Filtering ==========


@pytest.mark.parametrize("brand_name", SELECTED_BRANDS)
def test_filter_by_single_brand(home_page, brand_name):
    """Single brand selection should apply and clear correctly."""
    home_page.open()

    all_products = home_page.get_all_product_names()

    home_page.filter_by_brand(brand_name)
    home_page.wait_for_products_to_update()

    expect(home_page.brand_checkbox(brand_name)).to_be_checked()

    filtered_products = home_page.get_all_product_names()

    assert filtered_products
    assert filtered_products != all_products

    home_page.clear_brand_filter(brand_name)
    home_page.wait_for_products_to_update()

    expect(home_page.brand_checkbox(brand_name)).not_to_be_checked()


def test_filter_by_multiple_brands(home_page):
    """Multiple brand selections should all remain checked after filtering."""
    home_page.open()

    # Ensure list is visible before paginating through all names.
    home_page.wait_for_products()

    all_products = home_page.get_all_product_names()

    home_page.filter_by_brands(SELECTED_BRANDS)
    home_page.wait_for_products_to_update()

    for brand in SELECTED_BRANDS:
        expect(home_page.brand_checkbox(brand)).to_be_checked()

    filtered_products = home_page.get_all_product_names()

    assert filtered_products
    assert len(filtered_products) <= len(all_products)


# ========== Eco-Friendly Filtering ==========


def test_filter_by_eco_friendly(home_page):
    """Eco-friendly filter should be checkable and return at least one product."""
    home_page.open()

    home_page.filter_by_eco_friendly()
    home_page.wait_for_products_to_update()

    expect(home_page.eco_friendly_checkbox).to_be_checked()

    filtered_products = home_page.get_all_product_names()

    assert filtered_products
