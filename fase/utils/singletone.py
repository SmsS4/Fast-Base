from typing import Type, TypeVar

T = TypeVar("T", bound="Singleton")


class InstanceAlreadyCreated(Exception):
    pass


class Singleton:
    """
    Why this is class instead of metaclass?
    - I think metaclass is overengineer for singletone
    - I had some problems for type hints for
        `instance` method if this class is metaclass
    """

    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Singleton, cls).__new__(cls, *args, **kwargs)
            return cls._instance
        raise InstanceAlreadyCreated("You have to call `instance` method")

    @classmethod
    def instance(cls: Type[T]) -> T:
        return cls._instance
