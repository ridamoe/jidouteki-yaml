import typing
if typing.TYPE_CHECKING:
    from jidouteki.spec.website import Website 

from jidouteki.parsers import Parser
from jidouteki.spec.selectors import SelectorList

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import lxml

"""
        type: request
        urls:
         - /manga/{series}-chapter-{chapter}
        selector:
          css: '#readerarea img'
        properties:
          - src
"""

class RequestParser(Parser):
    urls: list
    selectors: SelectorList
    properties: list
    
    
    def __init__(self, arglist, **kwargs) -> None:
        super().__init__(arglist, **kwargs)
        self._root: Website
        
        urls = []
        for child_url in self.urls:
            urls.append(urljoin(self._root.metadata.base, child_url))
        self.urls = urls
    
    
    def parse(self, *args, **kwargs):
        for url in self.urls:
            url = str.format(url, **kwargs)
            resp = requests.get(url)
            if not resp.ok: continue
            soup = BeautifulSoup(resp.content, features="lxml")
            ret = self.selectors.match(soup)
            if ret: return ret
        return []