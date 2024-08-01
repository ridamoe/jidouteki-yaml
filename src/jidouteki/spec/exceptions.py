class SpecError(Exception):
    pass

class PropertyExpected(SpecError):
    pass

class MissingParseParameter(SpecError):
    pass

class PropertyTypeMismatch(SpecError):
    pass