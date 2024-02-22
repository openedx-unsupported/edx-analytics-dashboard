#

import datetime
import os
import sys

# on_rtd is whether we are on readthedocs.org, this line of code grabbed from docs.readthedocs.org
html_theme = 'sphinx_book_theme'

# html_theme_path = []

html_logo = "https://logos.openedx.org/open-edx-logo-color.png"

html_favicon = "https://logos.openedx.org/open-edx-favicon.ico"

html_theme_options = {
 "repository_url": "https://github.com/openedx/edx-analytics-dashboard",
 "repository_branch": "master",
 "path_to_docs": "docs/en_us/dashboard/source",
 "home_page_in_toc": True,
 "use_repository_button": True,
 "use_issues_button": True,
 "use_edit_page_button": True,
 # False was the default value for navigation_with_keys. However, in version 0.14.2 of pydata-sphinx-theme, this default
 # was removed and a warning was added that would be emitted whenever navigation_with_keys was not set. Because of the
 # "SPHINXOPTS = -W" configuration in tox.ini, all warnings are promoted to an error. Therefore, it's necesary to set
 # this value. I have set it to the default value explicitly. Please see the following GitHub comments for context.
 # https://github.com/pydata/pydata-sphinx-theme/issues/1539
 # https://github.com/pydata/pydata-sphinx-theme/issues/987#issuecomment-1277214209
 "navigation_with_keys": False,
 # Please don't change unless you know what you're doing.
 "extra_footer": """
        <a rel="license" href="https://creativecommons.org/licenses/by-sa/4.0/">
            <img
                alt="Creative Commons License"
                style="border-width:0"
                src="https://i.creativecommons.org/l/by-sa/4.0/80x15.png"/>
        </a>
        <br>
        These works by
            <a
                xmlns:cc="https://creativecommons.org/ns#"
                href="https://openedx.org"
                property="cc:attributionName"
                rel="cc:attributionURL"
            >Axim Collaborative, Inc</a>
        are licensed under a
            <a
                rel="license"
                href="https://creativecommons.org/licenses/by-sa/4.0/"
            >Creative Commons Attribution-ShareAlike 4.0 International License</a>.
    """
}

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
extensions = []

# General information about the project.
project = 'Using edX Insights'

author = 'Axim Collaborative, Inc'

copyright = '{year}, Axim Collaborative, Inc and licensed under a Creative Commons Attribution-ShareAlike 4.0 International License unless otherwise specified'.format(
    year=datetime.datetime.now().year)

# The short X.Y version.
version = ''
# The full version, including alpha/beta/rc tags.
release = ''
