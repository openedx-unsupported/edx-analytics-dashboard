import abc


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


class BaseCourseError(Exception):
    __metaclass__ = abc.ABCMeta

    course_id = None

    def __init__(self, *args, **kwargs):
        self.course_id = kwargs.pop('course_id')
        super(BaseCourseError, self).__init__(*args, **kwargs)
        self.message = self.message_template.format(self.course_id)

    @abc.abstractproperty
    def message_template(self):
        pass

    def __str__(self):
        return self.message


class NoAnswerSubmissionsError(BaseCourseError):
    """
    Raise if the course has no answer submissions.
    """
    @property
    def message_template(self):
        return 'No answers have been submitted for course {}.'


class NoVideosError(BaseCourseError):
    """
    Raise if the course has no videos.
    """
    @property
    def message_template(self):
        return 'No videos have been viewed for course {}.'
