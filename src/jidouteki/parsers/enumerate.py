from __future__ import annotations
import re
from jidouteki.parsers import Parser

import typing
if typing.TYPE_CHECKING:
    from jidouteki.spec.website import Website

import requests

class EnumerateParser(Parser):
    def parse(self, *args, **kwargs):
        kwargs['max_count'] = 2
        s1, s2 = self._parent.parse_next(**kwargs)[0:2]
        
        indices = [i for i,v in enumerate(ord(a) ^ ord(b) for a,b in zip(s1,s2)) if v != 0]
        
        end_idx = indices[-1]+1
        
        regex = r"^(.*?)(\d+)" + f"({re.escape(s1[end_idx:])})"
        m = re.match(regex, s1)
        if not m: return None
         
        begin, decimal, end = m.groups()
        if not decimal.isdigit(): return None
            
        initial = int(decimal)
        urls = []
        backwards = True
        counter = initial
        while True:
            url = f"{begin}{counter}{end}"
            if requests.get(url).ok:
                urls.append(url)
            else:
                if backwards:
                    backwards = False 
                    counter = initial+1
                else: break
            counter += -1 if backwards else 1
        return urls
