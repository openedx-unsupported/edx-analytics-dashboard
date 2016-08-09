#!/usr/bin/env bash

BOWER_COMPONENTS_PATH="analytics_dashboard/static/bower_components"

function CSS2SCSS() {
    filename=$1
    css_filename=${filename}.css

    if [ -f ${css_filename} ]; then
        mv ${css_filename} ${filename}.scss
    fi
}

# "Convert" the CSS to SCSS since SASS can only import .scss files.
CSS2SCSS ${BOWER_COMPONENTS_PATH}/bootstrapaccessibilityplugin/plugins/css/bootstrap-accessibility
CSS2SCSS ${BOWER_COMPONENTS_PATH}/nvd3/build/nv.d3

# Download the CLDR data for all locales
CLDR_DATA_PATH=${BOWER_COMPONENTS_PATH}/cldr-data
node ./node_modules/cldr-data-downloader/bin/download.js -i ${CLDR_DATA_PATH}/index.json -o ${CLDR_DATA_PATH}
