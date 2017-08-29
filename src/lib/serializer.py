import json

ENCODING = 'utf-8'


def value_serializer(m):
    return json.dumps(m).encode(ENCODING)


def value_deserializer(m):
    return json.loads(m.decode(ENCODING))
