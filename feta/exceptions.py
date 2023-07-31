class NoAvailableHost(Exception):
    def __init__(self, message="No hosts available at this time"):
        super().__init__(message)


class AuthenticationError(Exception):
    def __init__(self, message="Could not authenticate"):
        super().__init__(message)
