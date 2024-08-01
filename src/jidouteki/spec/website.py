
from jidouteki.spec import DictSpec, ListSpec, Root
from jidouteki.parsers import ParserList
from jidouteki.spec.meta import Meta
import re

class Metadata(DictSpec):
    base: str
    key: str = Meta.REQUIRED
    display_name: str = Meta.REQUIRED
    languages: list
    
class Parsable(DictSpec):
    params: list
    parsers: ParserList = Meta.REQUIRED
    
    def parse(self, *args, **kwargs) -> list:
        return self.parsers.parse(*args, **kwargs)

class Static(DictSpec):
    static: dict | list | str

    def parse(self, *args, **kwargs):
        return self.static

class Series(DictSpec):
    title: Parsable | Static
    cover: Parsable
    chapters: Parsable

class Match(ListSpec):
    def parse(self, url):
        for regex in self:
            match = next((m.groupdict() for m in re.finditer(regex, url)), None)
            if match != None: return match

class Chapter(DictSpec):
    pages: Parsable

class Search(DictSpec):
    series: Parsable

class Website(Root):    
    metadata: Metadata
    match: Match
    series: Series
    chapter: Chapter
    search: Search