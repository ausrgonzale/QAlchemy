"""
Module: test_registration_page.py

Purpose:
    Contains UI tests for the ToolShop registration page.

Responsibilities:
    - Verify a new customer can successfully register.
    - Validate integration between CustomerFactory and RegisterPage.
    - Verify successful registration redirects the user to the Login page.

Design Notes:
    Customer data is generated dynamically to ensure each test registers
    a unique user.
"""

from playwright.sync_api import Page, expect

from data.customer_factory import CustomerFactory
from pages.register_page import RegisterPage


def test_user_can_register(page: Page) -> None:
    """
    Verify a new customer can successfully register.
    """
    register_page = RegisterPage(page)

    register_page.open()

    register_page.is_loaded()

    customer = CustomerFactory.create()

    register_page.register(customer)

    expect(page).to_have_url("https://practicesoftwaretesting.com/auth/login")
