
from jidouteki.spec import DictSpec, ListSpec, Root
from jidouteki.fetchers import *
from jidouteki.spec.selectors import Selector
from jidouteki.spec.meta import Meta
from jidouteki.spec.exceptions import UnfetchableParser
import re

class Metadata(DictSpec):
    base: str
    key: str = Meta.REQUIRED
    display_name: str = Meta.REQUIRED
    languages: list

class Fetchable(DictSpec):
    fetcher: RequestFetcher | NetworkFetcher
    
class Parsable(Fetchable):
    selector: Selector = Meta.REQUIRED
    
    def __init__(self, arglist, **kwargs):
        super().__init__(arglist, **kwargs)
        if not self.fetcher: 
            self.fetcher = self._parent.fetcher
        if not self.fetcher: raise UnfetchableParser()

    def parse(self, **kwargs):
        data = self.fetcher.fetch(**kwargs)
        for soup in data:
            result = self.selector.match(soup)
            if result: return result
        return None
    
class Static(DictSpec):
    static: dict | list | str

    def parse(self, *args, **kwargs):
        return self.static

class Series(Fetchable):
    title: Parsable | Static
    cover: Parsable | Static
    chapters: Parsable | Static

class Match(ListSpec):
    def parse(self, url):
        for regex in self:
            if (m := re.match(regex, url)):
                return m.groupdict()

class Search(Fetchable):
    series: Parsable

class Website(Root):    
    metadata: Metadata
    match: Match
    
    series: Series
    images: Parsable
    search: Search