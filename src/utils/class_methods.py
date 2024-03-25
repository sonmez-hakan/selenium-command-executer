def singleton(cls):
    instances = {}

    def getinstance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return getinstance


def staticclass(cls):
    def new_init_blocked(*args, **kwargs):
        raise TypeError(f"{cls.__name__} is a static class and can not be instanced")

    setattr(cls, "__new__", staticmethod(new_init_blocked))
    setattr(cls, "__init__", staticmethod(new_init_blocked))

    return cls
