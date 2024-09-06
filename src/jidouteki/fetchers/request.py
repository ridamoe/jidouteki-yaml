import typing
if typing.TYPE_CHECKING:
    from jidouteki.spec.website import Website 

from jidouteki.fetchers import Fetcher

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

"""
    type: request
    urls:
        - /manga/{series}-chapter-{chapter}
"""

class RequestFetcher(Fetcher):
    urls: list
    
    def __init__(self, arglist, **kwargs) -> None:
        super().__init__(arglist, **kwargs)
        self._root: Website
        
        urls = []
        for child_url in self.urls:
            urls.append(urljoin(self._root.metadata.base, child_url))
        self.urls = urls
    
    def _fetch(self, **kwargs):
        ret = []
        for url in self.urls:
            url = str.format(url, **kwargs)
            resp = requests.get(url)
            if not resp.ok: continue
            soup = BeautifulSoup(resp.content, features="lxml")
            ret.append(soup)
        return ret
    
    def _key(self):
        return (self.urls,)