import os
from typing import Self, Tuple
from dataclasses import dataclass, field
from selenium.common import NoSuchElementException
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec

from src.driver.methods import option_value_in_select, option_text_in_select, JS_BUILD_CSS_SELECTOR

SELECT = 'select'
INPUT = 'input'
TEXT = 'text'
TIMEOUT: int = os.environ.get('TIMEOUT', 10)


class ByMapperException(Exception):
    """Raised when the key is not in the ByMap"""
    pass


class ByMapper:
    _dictionary = {
        'id': By.ID,
        'class': By.CLASS_NAME,
        'css-selector': By.CSS_SELECTOR,
        'name': By.NAME,
        'xpath': By.XPATH,
        "link-text": By.LINK_TEXT,
        "partial-link-text": By.PARTIAL_LINK_TEXT,
        "tag-name": By.TAG_NAME,
    }

    @staticmethod
    def transform(key):
        if key in ByMapper._dictionary:
            return ByMapper._dictionary[key]

        raise ByMapperException(f'{key} is not in the map')


@dataclass
class HtmlElement:
    element: WebElement | Select = field(init=False, default=None)
    driver: WebDriver
    by: str
    name: str

    def __post_init__(self):
        self.by = ByMapper.transform(self.by)

    def locator(self) -> Tuple[str, str]:
        return self.by, self.name

    def exists(self) -> bool:
        try:
            self.find()
            return True
        except NoSuchElementException:
            return False

    def find(self) -> WebElement:
        if self.element is None:
            self.element = self.driver.find_element(self.by, self.name)

        return self.element

    def set_element(self, element: WebElement) -> Self:
        self.element = element

        return self

    def get_attribute(self, attribute: str) -> str | None:
        element = self.find()
        attribute = attribute.lower()
        if attribute == TEXT:
            return element.text

        return element.get_attribute(attribute)

    def set_attribute(self, attribute, value) -> None:
        self.driver.execute_script(f"arguments[0].setAttribute('{attribute}', '{value}')", self.find())

    def find_selector_name(self) -> Self:
        self.name = self.driver.execute_script(JS_BUILD_CSS_SELECTOR, self.find())

        return self

    def wait(self, waits: list):
        for method_name in waits:
            method = getattr(self, method_name, None)
            method()

    def wait_until_exists(self) -> Self:
        WebDriverWait(self.driver, TIMEOUT).until(
            ec.presence_of_element_located(self.locator())
        )

        return self

    def child(self, by: str, name: str) -> Self:
        return HtmlElement(self.driver, 'css-selector', '').set_element(
            self.find().find_element(ByMapper.transform(by), name)
        )

    def children(self, by: str, name: str) -> list[Self]:
        return HtmlElementFactory.convert(self.driver, self.find().find_elements(ByMapper.transform(by), name))

    def parent(self) -> Self:
        return HtmlElement(self.driver, 'css-selector', '').set_element(
            self.find().find_element(By.XPATH, '..')
        )

    def click(self) -> None:
        self.driver.execute_script("arguments[0].click();", self.find())


@dataclass
class HtmlInput(HtmlElement):
    value: str | None = None

    def _value_to_set(self, value: str | None = None) -> str | None:
        return value if value is not None else self.value

    def set(self, value: str | None = None) -> None:
        self.find().send_keys(self._value_to_set(value))

    def wait_until_value(self, value: str | None = None) -> Self:
        value = self._value_to_set(value)
        if value is None:
            return self

        WebDriverWait(self.driver, TIMEOUT).until(
            ec.text_to_be_present_in_element_value(self.locator(), value)
        )

        return self


@dataclass
class HtmlSelect(HtmlInput):
    setter: str = 'value'

    def index_to_set(self, value: int | str | None) -> int:
        if value is not None and value.isnumeric():
            return int(value)

        if self.value is not None and self.value.isnumeric():
            return int(self.value)

        raise ValueError(f'value: {value} and self.value: {self.value} is not an integer')

    def find(self) -> Select:
        if self.element is None:
            self.element = Select(self.driver.find_element(self.by, self.name))

        return self.element

    def set_element(self, element: Select) -> Self:
        self.element = element

        return self

    def set(self, value: int | str | None = None) -> None:
        setter = self.setter.lower()
        if setter == 'index':
            self.set_by_index(value)
        elif setter == 'text':
            self.set_by_text(value)
        else:
            self.set_by_value(value)

    def set_by_value(self, value: str | None = None) -> None:
        self.find().select_by_value(self._value_to_set(value))

    def set_by_text(self, value: str | None = None) -> None:
        self.find().select_by_visible_text(self._value_to_set(value))

    def set_by_index(self, value: int | str | None = None) -> None:
        self.find().select_by_index(self.index_to_set(value))

    def wait_until_value(self, value: str | None = None) -> Self:
        value = self._value_to_set(value)
        if value is None:
            return self

        WebDriverWait(self.driver, TIMEOUT).until(
            option_value_in_select(self.find(), value)
        )

    def wait_until_text(self, value: str | None = None) -> Self:
        value = self._value_to_set(value)
        if value is None:
            return self

        WebDriverWait(self.driver, TIMEOUT).until(
            option_text_in_select(self.find(), value)
        )


class HtmlElementFactory:
    @staticmethod
    def input(driver: WebDriver, data: dict) -> HtmlInput | HtmlSelect:
        if 'type' in data and data.get('type').lower() == SELECT:
            return HtmlSelect(driver, data.get('by'), data.get('name'), data.get('value'), data.get('setter', 'value'))

        return HtmlInput(data.get('by'), data.get('name'), data.get('value'))

    @staticmethod
    def element(driver: WebDriver, data: dict) -> HtmlElement:
        return HtmlElement(driver, data.get('by'), data.get('name'))

    @staticmethod
    def find(driver: WebDriver, by: str, name: str) -> list[HtmlElement]:
        return HtmlElementFactory.convert(driver, driver.find_elements(ByMapper().transform(by), name))

    @staticmethod
    def convert(driver: WebDriver, elements: list) -> list[HtmlElement]:
        html_elements = []
        for element in elements:
            tag_name = element.tag_name.lower()
            if tag_name == SELECT:
                html_elements.append(HtmlSelect(driver, 'css-selector', '').set_element(Select(element)))
            elif tag_name == INPUT:
                html_elements.append(HtmlInput(driver, 'css-selector', '').set_element(element))
            else:
                html_elements.append(HtmlElement(driver, 'css-selector', '').set_element(element))

        return html_elements
