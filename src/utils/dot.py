def get(item: dict | list, keys: str | list, default=None):
    keys = keys if type(keys) == list else keys.split('.')
    value = item.copy()
    for key in keys:
        value = safe_list_get(value, key) if type(value) == list else value.get(key)
        if value is None:
            return default

    return value if value is not None else default


def safe_list_get(array: list, key: str | int):
    if str(key).isnumeric():
        key = int(key)

    if not isinstance(key, int):
        return None

    return array[key] if len(array) > key else None
