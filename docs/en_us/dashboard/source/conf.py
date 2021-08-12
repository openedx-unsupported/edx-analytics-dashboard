#

import datetime
import os
import sys

import edx_theme
# on_rtd is whether we are on readthedocs.org, this line of code grabbed from docs.readthedocs.org
html_theme = 'edx_theme'

html_theme_path = [edx_theme.get_html_theme_path()]

sys.path.append(os.path.abspath('../../../'))
sys.path.append(os.path.abspath('../../'))

# from docs.shared.conf import *

sys.path.insert(0, os.path.abspath('.'))

master_doc = 'index'

# Add any paths that contain templates here, relative to this directory.
# templates_path.append('source/_templates')

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
# html_static_path.append('source/_static')

# Add any Sphinx extension module names here, as strings. They can be extensions
# coming with Sphinx (named 'sphinx.ext.*') or your custom ones.
extensions = ['edx_theme']

# General information about the project.
project = 'Using edX Insights'

copyright = '{year}, edX Inc. and licensed under a Creative Commons Attribution-ShareAlike 4.0 International License unless otherwise specified'.format(
    year=datetime.datetime.now().year)

# The short X.Y version.
version = ''
# The full version, including alpha/beta/rc tags.
release = ''
