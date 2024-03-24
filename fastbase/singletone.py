class Singleton(object):
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "_singleton_instance"):
            cls._singleton_instance = super(Singleton, cls).__new__(cls)
        return cls._singleton_instance
