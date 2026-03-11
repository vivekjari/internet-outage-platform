import datetime


def get_current_timestamp():
    return datetime.datetime.utcnow()


def safe_get(dictionary, key, default=None):
    if dictionary and key in dictionary:
        return dictionary[key]
    return default