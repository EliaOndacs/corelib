from typing import Any

def datamodel(model: dict[str, type]):
    """
    allows you to make datamodel's that you can use later
    to make structured data
    """
    def __call__(**kwargs) -> dict:
        new: dict[str, Any] = {}
        for key in model:
            value = kwargs.get(key, None)
            if not value:
                raise KeyError(f"key {key!r} not found in the provided data")
            if type(value).__name__ != model[key].__name__:
                raise TypeError(
                    f"key {key!r} should be a type of {model[key].__name__!r}, found {type(value).__name__!r} instead"
                )
            new[key] = value
        return new

    return __call__
