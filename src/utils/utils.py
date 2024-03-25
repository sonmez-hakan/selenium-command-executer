import json


class Serializer(json.JSONEncoder):
    def default(self, o):
        return o.__dict__


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


def to_json(obj):
    return json.dumps(obj, cls=Serializer)


def to_dict(obj):
    return json.loads(json.dumps(obj, default=lambda o: getattr(o, '__dict__', str(o))))


def safe_json_loads(text, default=None):
    try:
        return json.loads(text)
    except ValueError as e:
        print(e)

    return default


def get(item, keys, default=None):
    keys = keys if type(keys) == list else [keys]
    value = item.copy()
    for key in keys:
        value = safe_list_get(value, key) if type(value) == list else value.get(key)
        if value is None:
            return default

    return value if value is not None else default


def safe_list_get(array: list, key):
    if not isinstance(key, int):
        return None

    return array[key] if len(array) > key else None
