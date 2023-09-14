import json

from django import template
from django.conf import settings
from django.template.defaultfilters import stringfilter
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from opaque_keys.edx.keys import CourseKey
from slugify import slugify

register = template.Library()


@register.simple_tag
def settings_value(name):
    """
    Retrieve a value from settings.

    If setting is not found, None is returned.
    """
    return getattr(settings, name)


@register.filter
def metric_percentage(value):
    # Translators: Simply move the percent symbol (%) to the correct location. Do NOT translate the word statistic.
    percent_stat = _('{statistic}%')
    percent = '0'

    if value:
        if value < 0.01:
            percent = '< 1'
        else:
            percent = '{:.1f}'.format(round(value, 3) * 100)

    return percent_stat.format(statistic=percent)


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
    except ValueError as e:
        raise template.TemplateSyntaxError("'captureas' node requires a variable name.") from e
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
def summary_point(value, label, subheading=None, tooltip=None, additional_value=None):
    return {
        'value': value,
        'label': label,
        'subheading': subheading,
        'additional_value': additional_value,
        'tooltip': tooltip
    }


@register.inclusion_tag('section_error.html')
def show_chart_error():
    """
    Returns the error section with default context.
    """
    return _get_base_error_context('chart')


@register.inclusion_tag('section_error.html')
def show_table_error():
    return _get_base_error_context('table')


@register.inclusion_tag('section_error.html')
def show_metrics_error():
    return _get_base_error_context('metrics')


def _get_base_error_context(content_type):
    return {
        'content_type': content_type,
        'load_error_message': settings.DOCUMENTATION_LOAD_ERROR_MESSAGE,
    }


@register.filter
def format_course_key(course_key, separator='/'):
    if isinstance(course_key, str):
        course_key = CourseKey.from_string(course_key)

    return separator.join([course_key.org, course_key.course, course_key.run])


@register.filter(is_safe=True)
@stringfilter
def unicode_slugify(value):
    return slugify(value)


@register.filter
def escape_json(data):
    """
    Escape a JSON string (or convert a dict to a JSON string, and then
    escape it) for being embedded within an HTML template.
    """
    json_string = json.dumps(data) if isinstance(data, dict) else data
    json_string = json_string.replace("&", "\\u0026")
    json_string = json_string.replace(">", "\\u003e")
    json_string = json_string.replace("<", "\\u003c")
    return mark_safe(json_string)


@register.filter
def languade_code_to_cldr(language_code):
    """
    Returns language codes in the CLDR expected naming convention.  The CLDR
    language codes in javascript are expected to have uppercase countries.
    """
    separator = '-'
    tokens = language_code.split(separator)

    if len(tokens) == 1:
        return language_code

    formatted_tokens = [tokens[0].lower()]
    for token in tokens[1:]:
        if len(token) == 2 or token in ['valencia', 'posix']:
            formatted_tokens.append(token.upper())
        else:
            formatted_tokens.append(token.capitalize())

    formatted_language_code = separator.join(formatted_tokens)

    # special cases
    if formatted_language_code.lower() in ['zh-tw', 'zh-hk', 'zh-mo', 'zh-hant']:
        formatted_language_code = 'zh-Hant'
    elif formatted_language_code.lower() in ['zh-cn', 'zh-sg', 'zh-hans']:
        formatted_language_code = 'zh'

    return formatted_language_code
