from django.core.serializers.json import DjangoJSONEncoder
from django.utils.encoding import force_text
from django.utils.functional import Promise


class LazyEncoder(DjangoJSONEncoder):
    """
    Force the conversion of lazy translations so that they can be serialized to JSON.
    via https://docs.djangoproject.com/en/dev/topics/serialization/
    """

    # pylint: disable=method-hidden
    def default(self, obj):
        if isinstance(obj, Promise):
            return force_text(obj)
        return super(LazyEncoder, self).default(obj)
