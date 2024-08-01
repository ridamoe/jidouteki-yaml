from jidouteki.driver import WebDriver
from selenium import webdriver


def get_net_data(driver: WebDriver) -> list:
    script = "var performance = window.performance || window.mozPerformance || window.msPerformance || window.webkitPerformance || {}; var network = performance.getEntriesByType('resource') || {}; return network;"
    return driver.execute_script(script)

def scroll(driver: WebDriver, y: int): 
    webdriver.ActionChains(driver).scroll_by_amount(0, y).perform()
