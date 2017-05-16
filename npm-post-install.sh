#!/usr/bin/env bash

NPM_PATH="node_modules"
NPM_BIN="${NPM_PATH}/.bin"

function CSS2SCSS() {
    filename=$1
    css_filename=${filename}.css

    if [ -f ${css_filename} ]; then
        mv ${css_filename} ${filename}.scss
    fi
}

# "Convert" the CSS to SCSS since SASS can only import .scss files.
CSS2SCSS ${NPM_PATH}/bootstrap-accessibility-plugin/plugins/css/bootstrap-accessibility
CSS2SCSS ${NPM_PATH}/nvd3/build/nv.d3

# Download the CLDR data for all locales
CLDR_DATA_PATH=${NPM_PATH}/cldr-data
node ./node_modules/cldr-data-downloader/bin/download.js -i ${CLDR_DATA_PATH}/urls.json -o ${CLDR_DATA_PATH}

# edX Pattern Library expects certain packages to be available to it
PATTERN_LIBRARY_PATH="${NPM_PATH}/edx-pattern-library"
PATTERN_LIBRARY_SASS_PATH="${PATTERN_LIBRARY_PATH}/pattern-library/sass"
PATTERN_LIBRARY_LIB_PATH="${PATTERN_LIBRARY_SASS_PATH}/global"
PATTERN_LIBRARY_LIBS=('bi-app-sass' 'bourbon' 'breakpoint-sass' 'susy')
for lib in "${PATTERN_LIBRARY_LIBS[@]}"
do
    cp -rf ${NPM_PATH}/$lib $PATTERN_LIBRARY_LIB_PATH/
done

# pre-compile the pattern library to improve sass compilation performance
if [ ! -f ${PATTERN_LIBRARY_SASS_PATH}/edx-pattern-library-ltr-compiled.scss ]; then
  echo "Pre-compiling edX pattern library..."
  ${NPM_BIN}/node-sass ${PATTERN_LIBRARY_SASS_PATH}/edx-pattern-library-ltr.scss ${PATTERN_LIBRARY_SASS_PATH}/edx-pattern-library-ltr-compiled.scss
  echo "Done compiling."
else
  echo "edX pattern library already compiled."
fi

# pre-compile the font-awesome sass because that's the only way I could get fonts working in webpack...
if [ ! -f ${NPM_PATH}/font-awesome/scss/font-awesome-compiled.scss ]; then
  echo "Pre-compiling font-awesome..."
  ${NPM_BIN}/node-sass ${NPM_PATH}/font-awesome/scss/font-awesome.scss ${NPM_PATH}/font-awesome/scss/font-awesome-compiled.scss
  echo "Done compiling."
else
  echo "font-awesome already compiled."
fi
# copy font files to insights static files (they are not included in the compiled sass)
DJANGO_STATIC_PATH=analytics_dashboard/static
STATIC_FONTS_PATH=analytics_dashboard/static/fonts
PATTERN_LIBRARY_FONTS_PATH="${NPM_PATH}/edx-pattern-library/pattern-library/fonts"
FONT_AWESOME_FONTS_PATH="${NPM_PATH}/font-awesome/fonts"
if [ ! -f ${STATIC_FONTS_PATH}/OpenSans ]; then
  echo "Copying font files to Django static fonts directory..."
  mkdir -p ${STATIC_FONTS_PATH}
  mkdir -p ${STATIC_FONTS_PATH}/OpenSans
  cp -rf ${PATTERN_LIBRARY_FONTS_PATH}/OpenSans/* ${STATIC_FONTS_PATH}/OpenSans/
  cp -rf ${FONT_AWESOME_FONTS_PATH}/* ${STATIC_FONTS_PATH}/
  echo "Done copying."
else
  echo "Font files already copied."
fi
