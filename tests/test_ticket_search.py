from pytest import mark
import time
import pytest
import datetime as dt
from datetime import timedelta
from playwright.sync_api import expect
performance = {'name': ''}


@pytest.fixture(scope='module')
def set_performance(rest, request):
    extra_day = request.config.cache.get('extra_day', default=None)
    if extra_day is None:
        extra_day = 0
    else:
        extra_day += 1
    request.config.cache.set('extra_day', extra_day)
    performance['name'] = f'automation testing {extra_day}'
    today = dt.date.today()
    response = rest.post('/ws/performances', json={'date': (today.replace(year=today.year + 1) + timedelta(days=extra_day)).strftime('%d-%m-%Y'), 'time': '13:30', 'price': 123,
                         'name': performance['name'], 'description': 'This is a real magic! You will be surprised how cool pytest and playwright works and how awesome test results are reported', 'features': ['testing', 'automation'], 'ticketsNumber': 1})
    print('performance create status code:', response.status_code)


@pytest.fixture(scope='module')
def auth(set_performance, app, users):
    user = users['user1']
    app.login(user['name'], user['password'])
    yield app


@pytest.fixture(scope='function')
def search(auth):
    auth.goto('/booking')
    yield auth


def test_search_without_parameters(search):
    assert False
    search.search_page.search()
    locators = search.search_page.list_results()
    created = locators.filter(has_text=performance['name'])
    expect(created).to_be_visible()


def test_search_date_from(search):
    search.search_page.search(date_from='01/01/2020')
    locators = search.search_page.list_results()
    created = locators.filter(has_text=performance['name'])
    expect(created).not_to_be_empty()


def test_search_date_to(search):
    search.search_page.search(date_to='01/01/2030')
    locators = search.search_page.list_results()
    created = locators.filter(has_text=performance['name'])
    expect(created).not_to_be_empty()


def test_search_dates_from_to(search):
    search.search_page.search(date_from='01/01/2022', date_to='01/01/2030')
    locators = search.search_page.list_results()
    created = locators.filter(has_text=performance['name'])
    expect(created).not_to_be_empty()


def test_search_time_from(search):
    search.search_page.search(time_from='08:00')
    locators = search.search_page.list_results()
    created = locators.filter(has_text=performance['name'])
    expect(created).not_to_be_empty()


def test_search_time_to(search):
    search.search_page.search(time_from='20:00')
    locators = search.search_page.list_results()
    created = locators.filter(has_text=performance['name'])
    expect(created).not_to_be_empty()


def test_search_price_from(search):
    search.search_page.search(price_from=0)
    locators = search.search_page.list_results()
    created = locators.filter(has_text=performance['name'])
    expect(created).not_to_be_empty()


def test_search_price_to(search):
    search.search_page.search(price_to=1500)
    locators = search.search_page.list_results()
    created = locators.filter(has_text=performance['name'])
    expect(created).not_to_be_empty()


def test_search_keyword(search):
    search.search_page.search(keyword='automation')
    locators = search.search_page.list_results()
    created = locators.filter(has_text=performance['name'])
    expect(created).not_to_be_empty()
