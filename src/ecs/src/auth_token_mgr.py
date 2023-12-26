import secrets


class SingletonParentClass(type):
    _instances = {}

    # standard singleton pattern
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


class AuthTokenMgr(metaclass=SingletonParentClass):
    def __init__(self):
        self.auth_tokens = {}

    def is_token_valid(self, user_id, token):
        return token == self.auth_tokens.get(user_id, None)

    def create_token(self, user_id):
        self.auth_tokens[user_id] = secrets.randbits(128)
        return self.auth_tokens[user_id]

    def remove_token(self, user_id):
        if user_id in self.auth_tokens:
            del self.auth_tokens[user_id]
            return True
        return False
