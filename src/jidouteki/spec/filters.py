import re
from jidouteki.spec import ListSpec

class Filter():
    conditions = {}
    def __init__(self, arglist):
        self.conditions = arglist
    
    def match(self, dict, **format_values):
        for key, filter in self.conditions.items():
            filter = str.format(filter, **format_values)
            if not re.match(filter, dict[key]):
                return False
        return True

class FilterList(ListSpec):
    def __init__(self, arglist, **kwargs):
        super().__init__([Filter(f) for f in arglist], **kwargs)
    
    def match(self, dict, **fvalues):
        return any(f.match(dict, **fvalues) for f in self) 