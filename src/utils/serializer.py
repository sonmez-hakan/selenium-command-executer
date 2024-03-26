import json


class Serializer(json.JSONEncoder):
    def default(self, o):
        return o.__dict__


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
