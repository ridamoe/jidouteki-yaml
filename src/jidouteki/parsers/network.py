from __future__ import annotations
import typing
if typing.TYPE_CHECKING:
    from jidouteki.spec.website import Website

from jidouteki.parsers import Parser
from jidouteki.spec.filters import FilterList
from jidouteki.driver import DriverManager, WebDriver, utils as driver_utils
import requests
from urllib.parse import urljoin

class NetworkParser(Parser):
    urls: list
    filters: FilterList
    _url_index = 0
    
    def __init__(self, arglist, **kwargs) -> None:
        super().__init__(arglist, **kwargs)
        self._root: Website
        
        urls = []
        for child_url in self.urls:
            urls.append(urljoin(self._root.metadata.base, child_url))
        self.urls = urls
    
    def next_url(self, series='', chapter='', check=True):
        url = None
        while True:
            url = self.urls[self._url_index]
            url = str.format(url, series=series, chapter=chapter)
            self._url_index += 1
            if check:
                if not requests.get(url).ok:
                    continue
            break
        return url
    
    def network_filter(self, net_data, **fvalues):
        out = []
        for net_object in net_data:
            object = {
                'url': net_object['name']
            }
            if self.filters.match(object, **fvalues):
                out.append(object['url'])
        return out
    
    def filter_network_resources(self, driver: WebDriver, fvalues: dict, quiet=150, target=2):
        state_ticks = 0
        state_len = 0
        
        output = set()
        
        HEIGHT = driver.get_window_size()['height']
        while True:
            driver_utils.scroll(driver, HEIGHT)
            net_data = driver_utils.get_net_data(driver)
            output.update(self.network_filter(net_data, **fvalues))
            
            if target:
                if len(output) >= target:
                    break
            else:
                if state_len == len(output):
                    if state_ticks >= quiet:
                        break
                    else: state_ticks += 1
                else: state_ticks = 0
                state_len = len(output)
            
        return list(output)
    
    def parse(self, *args, **kwargs):
        while True:
            url = self.next_url(**kwargs)
            if url == None: break
            driver = DriverManager.get()
            driver.get(url)
            substrs = {
                'series': kwargs.get("series", ""),
                'chapter': kwargs.get("chapter", "")
            }
            target = kwargs.get("max_count", None)
            resources = self.filter_network_resources(driver, kwargs, target=target)
            if resources and len(resources) != 0:
                return resources