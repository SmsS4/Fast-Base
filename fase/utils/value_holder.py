from typing import Generic, TypeVar

T = TypeVar("T")


class ValueHolder(Generic[T]):
    def __init__(self, value: T) -> None:
        self.value = value

    def get(self) -> T:
        return self.value

    def set(self, value: T) -> None:
        self.value = value
