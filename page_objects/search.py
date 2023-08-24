from playwright.sync_api import Page, Locator


class SearchPage:
    def __init__(self, page: Page):
        self.page = page
        self.page.on('dialog', lambda dialog: dialog.accept())

    def search(self, date_from: str = None, date_to: str = None,
               time_from: str = None, time_to: str = None,
               price_from: int = None, price_to: int = None,
               keyword: str = None):
        def parse_time(str_time: str) -> str:
            hours, minutes = str_time.split(':')
            return str(int(hours) * 60 + int(minutes))

        if date_from is not None:
            self.page.locator('#id_date_from').type(date_from)
        if date_to is not None:
            self.page.locator('#id_date_to').type(date_to)
        if time_from is not None:
            slider = self.page.locator('.timeRangeGroup .slider')
            slider.click(position={'x': _get_position_by_time(time_from, slider.bounding_box()['width']), 'y': 0})
        if time_to is not None:
            slider = self.page.locator('.timeRangeGroup .slider')
            slider.click(position={'x': _get_position_by_time(time_from, slider.bounding_box()['width']), 'y': 0})
        if price_from is not None:
            slider = self.page.locator('.priceRangeGroup .slider')
            slider.click(position={'x': _get_position_by_price(price_from, slider.bounding_box()['width']), 'y': 0})
        if price_to is not None:
            slider = self.page.locator('.priceRangeGroup .slider')
            slider.click(position={'x': _get_position_by_price(price_to, slider.bounding_box()['width']), 'y': 0})
        if keyword is not None:
            self.page.locator('#id_keyword').type(keyword)
        self.page.click('.defBtn')

    def list_results(self) -> Locator:
        return self.page.locator('.rTbody .rRow')

    def add_tickets(self, performance_locator: Locator, tickets: int) -> None:
        if tickets > 0:
            for i in range(tickets):
                performance_locator.locator('.itemsAmountPlus').click()
        else:
            for i in range(-tickets):
                performance_locator.locator('.itemsAmountMinus').click()

    def book(self):
        self.page.locator('.bookBtn').click()


def _get_position_by_time(time_str: str, width: float) -> float:
    hours, minutes = time_str.split(':')
    x = (int(hours) * 60 + int(minutes)) - 7 * 60
    return (x / 960) * width


def _get_position_by_price(price: int, width: float) -> float:
    return (price / 2000) * width
