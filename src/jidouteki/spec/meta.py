from abc import ABCMeta

class _Meta(list):
    def __or__(self, other):
        if isinstance(other, str):
            self.append(other)

class Meta():
    REQUIRED = _Meta(["required"])


class SpecMeta(ABCMeta):
    def __new__(mcls, name, bases, namespace, /, **kwargs):
        extra = {}
        for key in list(namespace.keys()):
            val = namespace[key]
            if isinstance(val, _Meta):
                for tags in val:
                    cvar = "__" + tags
                    
                    if cvar not in extra:
                        extra[cvar] = []
                    extra[cvar].append(key)
                namespace[key] = None
                    
        cls = super().__new__(mcls, name, bases, {**namespace, **extra}, **kwargs)
        return cls