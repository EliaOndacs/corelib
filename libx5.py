from typing import Protocol


class TypeModel(Protocol):
    def _on_message(self, message: str) -> "TypeModel":...

def update(model: TypeModel, message: str) -> TypeModel:
    return model._on_message(message)
