from playwright.sync_api import expect

from pages.login_page import LoginPage
from pages.register_page import RegisterPage


def test_can_navigate_to_login_page(home_page):
    """
    Verify a user can navigate from the Home page to the Login page.
    """
    home_page.open()
    home_page.click_sign_in()

    login_page = LoginPage(home_page.page)

    expect(login_page.page_heading).to_have_text("Login")


def test_can_navigate_to_registration_page(home_page):
    """
    Verify a user can navigate from the Login page to the Registration page.
    """
    home_page.open()
    home_page.click_sign_in()

    login_page = LoginPage(home_page.page)
    login_page.is_loaded()

    login_page.register_link.click()

    register_page = RegisterPage(home_page.page)
    register_page.is_loaded()


def test_registered_user_can_login(home_page):
    """
    Verify a registered user can successfully log in.
    """

    login_page = LoginPage(home_page.page)

    home_page.open()
    home_page.click_sign_in()

    login_page.is_loaded()

    login_page.login(
        email="jimmyjohnson@outlook.com",
        password="Password123~^",
    )

    assert home_page.get_signed_in_user() == "Jimmy Johnson"
