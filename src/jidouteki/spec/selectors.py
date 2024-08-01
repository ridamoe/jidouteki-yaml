from bs4 import BeautifulSoup
from jidouteki.spec import ListSpec, DictSpec
from jidouteki.spec.exceptions import PropertyTypeMismatch
import re
from collections import OrderedDict

import typing
if typing.TYPE_CHECKING:
    from jidouteki import Website

class Pipeline(ListSpec):
    def process(self, items_to_process: list):
        items = items_to_process
        for step in self:
            key = list(step.keys())
            if len(key) > 1: raise PropertyTypeMismatch("Pipeline steps should only have one key")
            key = key[0]
            value = step[key]
            
            match key:
                case 'reverse':
                    items = list(reversed(items))
                    continue
                case 'props':
                    def _process(item):
                        for p in value:
                            if p == "text"  and callable(getattr(item, "get_text", None)):
                                 prop = item.get_text()
                            else:    
                                prop = item.get(p, None)
                            if not prop: continue
                            return prop
                        return None
                case 'match':
                    self._root: Website
                    def _process(item):
                        return self._root.match.parse(item)
                case 'regex':
                    def _process(item):
                        return re.findall(value, item)
                case 'replace':
                    def _process(item):
                        curr = item 
                        for orig,repl in value:
                            curr = curr.replace(orig, repl)
                        return curr
                case 'format':
                    def _process(item):
                        return value.format(item)
                case 'proxy':
                    def _process(item):
                        return self._context.proxy + item

                case _: raise PropertyTypeMismatch(f"Unknown pipeline step {key}")
            
            items = [_process(item) for item in items]
            items = [item for item in items if item != None]
            items = [item for sublist in items for item in (sublist if isinstance(sublist, (list, tuple)) else [sublist])]
            
            # Remove duplicates
            items = [item for i, item in enumerate(items) if item not in items[i + 1:]]
                
        return items
        
class Selector(DictSpec):
    """
    type: css
    query: .thumbook .thumb img
    pipeline:
        - props:
           - src
    """
    type: str
    query: str
    pipeline: Pipeline
    
    def match(self, document: BeautifulSoup):
        matches = []
        match self.type:
            case 'css': 
                matches.extend(document.select(self.query))
            case 'regex':
                matches.extend(re.findall(self.query, str(document)))
            case 'xpath': raise NotImplementedError()
            case _: raise PropertyTypeMismatch(self.type)
        if self.pipeline:
            matches = self.pipeline.process(matches)
        return matches
        
class SelectorList(ListSpec):
    def __init__(self, arglist, **kwargs):
        super().__init__([Selector(f, **kwargs) for f in arglist], **kwargs)
    
    def match(self, document):
        matches = []
        for s in self:
            s: Selector
            matches.extend(s.match(document))
        
        # Extract single-valued properties from list
        if self._parent.output == "single":
            return matches[0]
        else:
            return matches