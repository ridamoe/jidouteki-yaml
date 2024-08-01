from jidouteki.parsers import EnumerateParser, NetworkParser, RequestParser, LiveParser
from jidouteki.spec import ListSpec
from jidouteki.spec.exceptions import PropertyTypeMismatch, MissingParseParameter

class ParserList(ListSpec):
    _parser_index = 0
    
    def __init__(self, arglist, **kwargs):
        parsed_arglist = []
        for val in arglist:
            match val['type']:
                case 'enumerate': parsed_arglist.append(EnumerateParser(val, **kwargs))
                case 'network': parsed_arglist.append(NetworkParser(val, **kwargs))
                case 'live': parsed_arglist.append(LiveParser(val, **kwargs))
                case 'request': parsed_arglist.append(RequestParser(val, **kwargs))
                case _: raise PropertyTypeMismatch(val['type'])
                    
        super().__init__(parsed_arglist, **kwargs)
            
    def parse_next(self, *args, **kwargs):
        from jidouteki.spec.website import Parsable
        if isinstance(self._parent, Parsable):
            for i, key in enumerate(self._parent.params):
                if key not in kwargs.keys():
                    if len(args) <= i: raise MissingParseParameter(f"Key {key}")
                    kwargs[key] = args[i]
        
        if len(self) > self._parser_index:
            self._parser_index += 1
            return self[self._parser_index-1].parse(*args, **kwargs)
        raise StopIteration()

    def parse(self, *args, **kwargs):        
        self._parser_index = 0
        while len(self) > self._parser_index:
                parsed = self.parse_next(*args, **kwargs)
                if parsed != None: return parsed
        return None