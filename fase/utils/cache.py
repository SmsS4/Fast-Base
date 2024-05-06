import time
from datetime import timedelta
from typing import Any
from typing import Generic
from typing import TypeVar

import fastapi

T = TypeVar("T")


class __UNSET:
    pass


UNSET = __UNSET()


class Cache(Generic[T]):
    def __init__(self, ttl: timedelta | None) -> None:
        self.ttl = ttl.seconds if ttl else None
        self.data: dict[str, tuple[T, float]] = {}

    def put(self, key: str, value: T) -> None:
        self.data[key] = (value, time.time())

    def get(self, key: str, default: Any = UNSET) -> T:
        value_time = self.data.get(key, None)
        if value_time is None:
            if default != UNSET:
                return default
            raise KeyError(key)
        value, create_time = value_time
        if self.ttl and time.time() - create_time > self.ttl:
            self.data.pop(key)
            if default != UNSET:
                return default
            raise KeyError(key)
        return value

    def dep(self):
        async def dependency():
            yield self

        return fastapi.Depends(dependency)
