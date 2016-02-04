from django import template
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.templatetags.static import StaticNode
from django.contrib.staticfiles.storage import staticfiles_storage


register = template.Library()


def get_rjs_path(path):
    if getattr(settings, 'RJS_OPTIMIZATION_ENABLED', False):
        rjs_output_dir = getattr(settings, 'RJS_OUTPUT_DIR')

        if rjs_output_dir:
            return '{0}/{1}'.format(rjs_output_dir, path)

        raise ImproperlyConfigured('RJS_OPTIMIZATION_ENABLED is set to True, but RJS_OUTPUT_DIR has not been set.')

    return path


class RjsStaticFilesNode(StaticNode):
    def url(self, context):
        path = self.path.resolve(context)
        path = get_rjs_path(path)
        return staticfiles_storage.url(path)


@register.tag('static_rjs')
def do_static(parser, token):
    """
    A template tag that returns the URL to a file (that has been optimized by r.js)
    using staticfiles' storage backend

    Usage::

        {% static_rjs path [as varname] %}

    Examples::

        {% static_rjs "myapp/js/main.js" %}

    """
    return RjsStaticFilesNode.handle_token(parser, token)
