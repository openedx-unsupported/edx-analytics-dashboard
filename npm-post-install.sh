#!/usr/bin/env bash

NPM_PATH="node_modules"
NPM_BIN="${NPM_PATH}/.bin"

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
