from os import environ

import yaml

# Normally you should not import ANYTHING from Django directly
# into your settings, but ImproperlyConfigured is an exception.
from django.core.exceptions import ImproperlyConfigured


def get_env_setting(setting):
    """ Get the environment setting or return exception """
    try:
        return environ[setting]
    except KeyError:
        error_msg = "Set the %s env variable" % setting
        raise ImproperlyConfigured(error_msg)


CONFIG_FILE = get_env_setting('ANALYTICS_DASHBOARD_CFG')

with open(CONFIG_FILE) as f:
    config_from_yaml = yaml.load(f)

vars().update(config_from_yaml)
