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

# edX Pattern Library expects certain packages to be available to it
PATTERN_LIBRARY_SASS_PATH="${BOWER_COMPONENTS_PATH}/edx-pattern-library/pattern-library/sass"
PATTERN_LIBRARY_LIB_PATH="${PATTERN_LIBRARY_SASS_PATH}/global"
PATTERN_LIBRARY_LIBS=('bi-app-sass' 'bourbon' 'breakpoint-sass' 'susy')
for lib in "${PATTERN_LIBRARY_LIBS[@]}"
do
    cp -rf ${BOWER_COMPONENTS_PATH}/$lib $PATTERN_LIBRARY_LIB_PATH/
done

# pre-compile the pattern library to improve sass compilation performance
echo "Pre-compiling edX pattern library..."
sassc ${PATTERN_LIBRARY_SASS_PATH}/edx-pattern-library-ltr.scss ${PATTERN_LIBRARY_SASS_PATH}/edx-pattern-library-ltr-compiled.scss
