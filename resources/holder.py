
import datetime


class HolderSingleton(type):
    """ Metaclass - define an instance operation that lets client access it's unique instance """

    def __init__(cls, name, bases, attrs, **kwargs):
        super().__init__(name, bases, attrs)
        cls._instance = None

    def __call__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__call__(*args, **kwargs)
        return cls._instance


class RecoveryHolder(metaclass=HolderSingleton):
    """ Temporary data """
    expires = datetime.timedelta(hours=24)
    reset_token = ''
    password = ''
    pass
