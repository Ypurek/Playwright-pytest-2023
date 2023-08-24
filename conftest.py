import pytest
import tomllib
import os
from pytest import fixture, FixtureRequest, Parser, hookimpl
from playwright.sync_api import sync_playwright, Playwright, Browser
from settings import BROWSER_OPTIONS
from helpers import Connector
from page_objects import App
import datetime as dt


@fixture(scope="session")
def get_playwright() -> Playwright:
    with sync_playwright() as playwright:
        yield playwright


@fixture(scope='session')
def get_browser(get_playwright: Playwright, request: FixtureRequest) -> Browser:
    request.config.cache
    get_playwright.devices.get('')
    # monkeypatch.setenv('PWBROWSER', 'chromium')
    headless = request.config.getoption('--headless') == 'True'

    match request.config.getoption('--browser'):
        case 'chromium':
            browser = get_playwright.chromium.launch(headless=headless)
        case 'webkit':
            browser = get_playwright.webkit.launch(headless=headless)
        case 'firefox':
            browser = get_playwright.firefox.launch(headless=headless)
        case _:
            pytest.exit('unsupported browser type')

    yield browser
    browser.close()
    # monkeypatch.delenv('PWBROWSER')


@fixture(scope='session')
def app(get_playwright: Playwright, get_browser: Browser, request: FixtureRequest) -> App:
    device = request.config.getoption('--device')
    device_config = get_playwright.devices.get(device)
    if device_config is not None:
        device_config.update(BROWSER_OPTIONS)
    url = request.config.getoption('--url')
    app = App(get_browser, base_url=url, **BROWSER_OPTIONS)
    yield app


@fixture(scope='session')
def users(request: FixtureRequest):
    project_path = request.node.fspath.strpath
    with open(os.path.join(project_path, 'users.toml'), 'rb') as f:
        yield tomllib.load(f)


@fixture(scope='session')
def rest(request: FixtureRequest):
    url = request.config.getoption('--url')
    connector = Connector(url)
    yield connector
    connector.close()


# -----HOOKS SECTION-----

def pytest_addoption(parser: Parser) -> None:
    parser.addoption("--headless", action="store", default="True", help="headless or headed")
    parser.addoption("--browser", action="store", default="chromium", help="browser type")
    parser.addoption("--device", action="store", default="desktop", help="device type")
    parser.addoption("--url", action="store", default="http://circus.qamania.org", help="url to test")


@hookimpl(tryfirst=True)
def pytest_runtest_makereport(item, call):
    used_fixture_ids = set()
    if call.when == 'call' and call.excinfo is not None:
        artifact_urls = list()
        for i, fixture_name in enumerate(item.fixturenames):
            app = item.funcargs.get(fixture_name)
            if not isinstance(app, App):
                continue
            if app.uid in used_fixture_ids:
                continue
            used_fixture_ids.add(app.uid)
            screenshot = app.screenshot()
            timestamp = dt.datetime.now().strftime('%d-%m-%Y_%H-%M-%S-%f')
            key = f'{timestamp}-{fixture_name}-{i}.png'
            artifact_urls.append(pytest.s3_connector.upload_file_object(screenshot, key))

        setattr(item, 'testomatio_artifacts', artifact_urls)
