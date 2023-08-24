from playwright.sync_api import Browser
from page_objects.search import SearchPage


class App:
    def __init__(self, browser: Browser, base_url: str, **kwargs):
        self.uid = id(self)
        self.browser = browser
        self.base_url = base_url
        self.context = browser.new_context(**kwargs)
        self.context.set_default_timeout(10_000)
        self.page = self.context.new_page()
        self.kwargs = kwargs
        self.search_page = SearchPage(self.page)

    def goto(self, url: str, use_base_url=True, wait_until='networkidle') -> None:
        if use_base_url:
            self.page.goto(self.base_url + url, wait_until=wait_until)
        else:
            self.page.goto(url, wait_until=wait_until)

    def login(self, username: str, password: str) -> None:
        self.goto('/login')
        self.page.fill('input[name="username"]', username)
        self.page.fill('input[name="password"]', password)
        with self.page.expect_navigation(wait_until='networkidle'):
            self.page.click('.loginBtn')

    def login_anonymous(self) -> None:
        self.goto('/login')
        with self.page.expect_navigation(wait_until='networkidle'):
            self.page.click('.anonBtn')

    def logout(self) -> None:
        self.goto('/logout')

    def screenshot(self) -> bytes:
        return self.page.screenshot()
