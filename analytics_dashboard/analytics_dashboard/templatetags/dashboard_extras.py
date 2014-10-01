from django import template
from django.conf import settings
from django.utils.safestring import mark_safe

register = template.Library()


@register.simple_tag
def settings_value(name):
    """
    Retrieve a value from settings.

    If setting is not found, None is returned.
    """
    return getattr(settings, name)


@register.tag(name='captureas')
def do_captureas(parser, token):
    """
    Capture contents of block into context.

    Source:
        https://djangosnippets.org/snippets/545/

    Example:
        {% captureas foo %}{{ foo.value }}-suffix{% endcaptureas %}
        {% if foo in bar %}{% endif %}
    """

    try:
        __, args = token.contents.split(None, 1)
    except ValueError:
        raise template.TemplateSyntaxError("'captureas' node requires a variable name.")
    nodelist = parser.parse(('endcaptureas',))
    parser.delete_first_token()
    return CaptureasNode(nodelist, args)


class CaptureasNode(template.Node):
    def __init__(self, nodelist, varname):
        self.nodelist = nodelist
        self.varname = varname

    def render(self, context):
        output = mark_safe(self.nodelist.render(context).strip())
        context[self.varname] = output
        return ''


@register.inclusion_tag('summary_point.html')
def summary_point(value, label, subheading=None, tooltip=None):
    return {
        'value': value,
        'label': label,
        'subheading': subheading,
        'tooltip': tooltip
    }


@register.inclusion_tag('section_error.html')
def show_chart_error():
    return {'content_type': 'chart', 'documentation_url': settings.DOCUMENTATION_LOAD_ERROR_URL}


@register.inclusion_tag('section_error.html')
def show_table_error():
    return {'content_type': 'table', 'documentation_url': settings.DOCUMENTATION_LOAD_ERROR_URL}


@register.inclusion_tag('section_error.html')
def show_metrics_error():
    return {'content_type': 'metrics', 'documentation_url': settings.DOCUMENTATION_LOAD_ERROR_URL}
