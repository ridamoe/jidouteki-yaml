
from jidouteki.spec.exceptions import PropertyExpected, PropertyTypeMismatch
from jidouteki.spec.meta import SpecMeta

import typing
from typing import Self
if typing.TYPE_CHECKING:
    from jidouteki.main import Jidouteki

class Spec(metaclass=SpecMeta):
    def __init__(self, arglist, **kwargs):
        """Parse argument list and initialize properties
        
        By default this relies on typed annotations. Subclasses should overload this if this is unfeasable.

        Args:
            arglist (dict): The list of arguments.

        Raises:
            SpecError: Raised on parsing failure.
        """
        
        self._context: Jidouteki = kwargs.get("_context", None)
        
        # If self is set as root, access its lowercase name as the first value of the dictionary
        self._parent: Self = kwargs.get("_parent", None)
        
        if self._parent == None:
            if not self._name in arglist:
                raise PropertyExpected(self._name)
            arglist = arglist[self._name]
            
        hints = typing.get_type_hints(self.__class__, include_extras=True)
        for hint, _type in hints.items():
            if not hint.startswith("_"):
                is_required =  hint in getattr(self, "__required", [])
                value = self._parse_value(arglist, hint, _type, is_required)
                setattr(self, hint, value)
    @property
    def _name(self) -> str:
        return self.__class__.__name__.lower()
        
    def _getattrs(self):
        return [var for var in vars(self) if var[0] != "_"]
    
    def __eq__(self, value: Self) -> bool:
        # Dumb comparison
        if value == None: return False
        return self._name == value._name
    
    @property
    def _root(self):
        if self._parent == None:
            return self
        
        parent = self._parent
        while parent._parent != None:
            parent = parent._parent
        
        return parent
    
    def __bool__(self) -> bool:
        return True
    
    def __repr__(self) -> str:
        return f"Spec[{self._name}]"
    
    def _parse_value(self, dictionary: dict, value: str, _type: typing.Type, required: bool=False):
        """Parse a single value from a dictionary

        Args:
            dictionary (dict): The input dictionary.
            value (str): The name of the value.
            type (Type): The type of the value.
            required (bool, optional): Whenether the value is required. Defaults to False.

        Raises:
            PropertyExpected: Raised when a required propety is absent.
            PropertyTypeMismatch: Raised when property type doesn't match ``type``. 

        Returns:
            type: The object of type ``type``
        """
        
        if value not in dictionary:
            if required: 
                raise PropertyExpected(self._root.metadata.key, self, self._parent, value)
            else: return None
        
        _type_origin = typing.get_origin(_type) 
        
        if _type_origin == None:
            if isinstance(dictionary[value], _type):
                return dictionary[value]
        
        if _type_origin == typing.Literal:
            allowed = typing.get_args(_type)
            if dictionary[value] in allowed:
                return dictionary[value]
            else: raise PropertyTypeMismatch(f"Literal property not allowed. Only allows {allowed}")
        
        _types = typing.get_args(_type) or (_type,)
        for _type2 in _types:
            if issubclass(_type2, type(dictionary[value])):
                extra = {}
                if issubclass(_type2, Spec):
                    extra = { '_parent': self, '_context': self._context }
                    if (isinstance(dictionary[value], dict)):
                        type_keys = set(typing.get_type_hints(_type2).keys())
                        dict_keys = set(dictionary[value].keys())
                        if not dict_keys.issubset(type_keys):
                            continue
                return _type2(dictionary[value], **extra)
            
        raise PropertyTypeMismatch(value, _type)
    
class DictSpec(Spec, dict):
    pass

class ListSpec(Spec, list):
    def __init__(self, arglist, **kwargs):
        self.extend(arglist)
        super().__init__(arglist, **kwargs)

class Root(DictSpec):
    def __init__(self, arglist, **kwargs):
        super().__init__(arglist, **kwargs)