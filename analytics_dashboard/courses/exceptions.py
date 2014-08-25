class PermissionsError(Exception):
    """
    Base class for permissions errors.
    """
    pass


class UserNotAssociatedWithBackendError(PermissionsError):
    """
    Raise when a user is not associated with a given backend.
    """
    pass


class InvalidAccessTokenError(PermissionsError):
    """
    Raise if user has an empty or otherwise invalid access token.
    """
    pass


class PermissionsRetrievalFailedError(PermissionsError):
    """
    Raise if permissions retrieval fails (e.g. the backend is unreachable).
    """
    pass
