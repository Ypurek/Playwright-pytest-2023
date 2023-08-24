# Pytest Playwright Template project with Testomat.io integration

Goals of this project:

- update my [previous template](https://github.com/Ypurek/playwright-automation) with the latest Python and Playwright
  features
- add [Testomat.io integration](https://github.com/Ypurek/pytest-analyzer) and try it
- stop using Allure report

## Tools

- [Playwright](https://playwright.dev/) - browser automation library
- [Pytest](https://docs.pytest.org/en/stable/) - test framework
- [Testomat.io](https://testomat.io/) - test management tool

## Installation

- install [Python](https://www.python.org/downloads/) 3.11 or higher
- clone this repository
- install dependencies

```bash
pip install -r requirements.txt
```

## Usage

Tests are testing **Circus Ticket App** application designed for QA students.  
Source Code, API, hints: https://github.com/Ypurek/Circus-Ticket-App  
There are 2 option of usage (Please read recommendations in GitHub first):  
- run tests online with http://circus.qamania.org/ 
- run tests locally (run Circus Ticket App locally first)

## Testomat.io integration
Integration works with [pytest-analyzer](https://github.com/Ypurek/pytest-analyzer) plugin.  
To install it separately use:
```bash
pip install pytest-analyzer
```
To integrate with Testomat.io you need to:
- create account on https://testomat.io/
- Create project and get API key
  - Create environment variable **TESTOMATIO** with your API key
  - Optional: [Create S3 bucket](https://docs.testomat.io/usage/test-artifacts/) to store artifacts (like screenshots)
  - Optional: on testomat.io allow to share S3 credentials with test runner
- sync tests with testomat.io
```bash
pytest --analyzer add 
```
- run your tests and save results to testomat.io
```bash
pytest --analyzer sync
```

## Test implementation details
- global fixtures and putest hooks are in [conftest.py](conftest.py)
- tests are in [tests](tests) folder
- page objects are in [page_objects](page_objects) folder
- To save artifacts next hook is used:
- all tests use locator Playwright object and assert test results with Playwright expect
```python
@hookimpl(tryfirst=True)
def pytest_runtest_makereport(item, call):
    # to avoid of calling nested fixtures checking distingush them by uid
    used_fixture_ids = set()
    # save artifacts ONLY during test execution (not setup or teardown) and ONLY if test failed
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
            # save screenshot to S3 bucket, save url to artifact_urls
            artifact_urls.append(pytest.s3_connector.upload_file_object(screenshot, key))

        # testomatio_artifacts property is used by pytest-analyzer plugin in pytest_runtest_makereport hook
        setattr(item, 'testomatio_artifacts', artifact_urls)
```

