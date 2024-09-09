from bs4 import BeautifulSoup
from jidouteki.spec import ListSpec, DictSpec
from jidouteki.spec.exceptions import PropertyTypeMismatch
import re
from typing import Literal
import urllib.parse
import json

import typing
if typing.TYPE_CHECKING:
    from jidouteki import Website

class Pipeline(ListSpec):
    def process(self, items_to_process: list):
        saved = {}
        items = items_to_process
        for step in self:
            key = list(step.keys())
            if len(key) > 1: raise PropertyTypeMismatch(f"Pipeline steps should only have one key this has {len(key)}: {key}, {self}, {list(self)}")
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
                        return prop
                case 'prop':
                    def _process(item):
                        prop = None
                        if value == "text" and callable(getattr(item, "get_text", None)):
                                prop = item.get_text()
                        else:    
                            prop = item.get(value, None)
                        return prop
                case 'has':
                    def _process(item):
                        for requirements in value:
                            req_key = requirements["key"]
                            req_value = requirements["value"]
                            if item.get(req_key) != req_value: return None 
                        return item
                case 'filter':
                    assert isinstance(value, list)
                    inner_pipeline =  Pipeline(value, _parent=self, _context=self._context)
                    def _process(item):
                        filtered = inner_pipeline.process([item])
                        return item if filtered else None
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
                        if isinstance(item, dict):
                            return value.format(**item, **saved)
                        elif isinstance(item, list):
                            return value.format(*item, **saved)
                        elif isinstance(item, str):
                            print(item)
                            return value.format(item, **saved)
                case 'proxy':
                    def _process(item):
                        params = []
                        if "headers" in value:
                            for key,val in value["headers"].items():
                                header = ''.join([w.capitalize() for w in key.split('-')])
                                params.append(('header', f"{header}: {val}"))
                        
                        params.append(("url", item))
                        query_string = urllib.parse.urlencode(params)
                            
                        return f"{self._context.proxy}?{query_string}"
                case 'reset':
                    items = items_to_process
                    continue
                case 'save':
                    if len(items) == 1:
                        saved[value] = items[0]
                    elif len(items) == 0:
                        saved[value] = ""
                    continue
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
    output: Literal["multiple", "single"] = "multiple"
    pipeline: Pipeline
    
    def match(self, document: BeautifulSoup):
        matches = []
        match self.type:
            case 'css': 
                matches.extend(document.select(self.query))
            case 'regex':
                matches.extend(re.findall(self.query, str(document)))
            case 'xpath': raise NotImplementedError()
            case 'json':
                matches.extend([json.loads(document.text)])
            case _: raise PropertyTypeMismatch(self.type)
        if self.pipeline:
            matches = self.pipeline.process(matches)
        
        # Extract single-valued properties from list
        if self.output == "single":
            return "" if len(matches) == 0 else matches[0]
        else:
            return matches