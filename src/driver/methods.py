import os

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from .driver import Driver

TIMEOUT = int(os.environ.get('TIMEOUT', 10))

JS_BUILD_CSS_SELECTOR = """for(var e=arguments[0],n=[],i=function(e,n){if(!e||!n)return 0;for(var i=0,
a=e.length;a>i;i++)if(-1==n.indexOf(e[i]))return 0;re turn 1};e&&1==e.nodeType&&'HTML'!=e.nodeName;e=e.parentNode){
if( e.id){n.unshift('#'+e.id);break}for(var a=1,r=1,o=e.localName,l= e.className&&e.className.trim().split(/[\\s,
]+/g),t=e.previousSi bling;t;t=t.previousSibling)10!=t.nodeType&&t.nodeName==e.nodeNa me&&(i(l,t.className)&&(
l=null),r=0,++a);for(var t=e.nextSibling ;t;t=t.nextSibling)t.nodeName==e.nodeName&&(i(l,t.className)&&(l =null),
r=0);n.unshift(r?o:o+(l?'.'+l.join('.'):':nth-child('+a+' )'))}return n.join(' > '); """


def wait_for_url_changes(url: str, key: str | None = None):
    try:
        WebDriverWait(Driver.get(key), TIMEOUT * 2).until(
            EC.url_changes(url)
        )

        return True
    except:
        return False


def wait_for_fetch(key: str | None = None):
    WebDriverWait(Driver.get(key), TIMEOUT).until(
        lambda driver: driver.execute_script("return (window.fetch && fetch.active === 0) || !window.fetch")
    )


def wait_for_ajax(key: str | None = None):
    WebDriverWait(Driver.get(key), TIMEOUT).until(
        lambda driver: driver.execute_script("return jQuery.active == 0")
    )


def wait_for_element(by: str, name: str, key: str | None = None):
    WebDriverWait(Driver.get(key), TIMEOUT).until(
        EC.presence_of_element_located((by, name))
    )


def option_text_in_select(select: Select, option_text: str):
    def _predicate(driver):
        return option_text in [opt.text for opt in select.options]

    return _predicate


def option_value_in_select(select: Select, option_value: str):
    def _predicate(driver):
        return option_value in [opt.get_attribute('value') for opt in select.options]

    return _predicate
