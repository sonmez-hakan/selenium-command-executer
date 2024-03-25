from abc import ABC, abstractmethod
from . import Driver, HtmlElement


class Pagination(ABC):
    @abstractmethod
    def page_forward(self, pagination: dict, page: int) -> None:
        pass

    @staticmethod
    def _get_url(url: str, page: int, func_def: str):
        func = eval(func_def)

        return func(url, page)


class LinkPagination(Pagination):
    def page_forward(self, pagination: dict, page: int):
        until: int = pagination.get('until')
        if 0 < until < page:
            raise PageLimitExceeded(f'The allowed number of pages has been exceeded. {page}')

        driver = Driver().get()
        url = driver.current_url
        if "link" in pagination:
            driver.get(self._get_url(url, page, pagination.get('link')))
        else:
            links = pagination.get('links')
            parent = links.get("parent")
            find = links.get("find")
            try:
                element = HtmlElement(parent.get('by'), parent.get('name')).child(
                    find.get('by'), find.get('text').replace('{{page}}', str(page))
                )
            except Exception:
                raise PageNotFound(f'{page} not found')

            if "click" in find:
                func = eval(find.get('click'))
                func(element)
            else:
                element.click()

        if url == driver.current_url:
            raise SameUrlException("After changing url returned the same")


class SameUrlException(Exception):
    pass


class PageNotFound(Exception):
    pass


class PageLimitExceeded(Exception):
    pass
