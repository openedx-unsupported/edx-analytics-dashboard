if (window.language === undefined) { // should only occur in test environments
    window.language = 'en';
}

/**
 * Returns the Globalize object for localizing dates and numbers.  window.language
 * is expected to be standardized to those used in CLDR.  See base_dashboard.html
 * for how window.language is set.
 */
define([
    'globalize',
    '!json-loader!cldr-data/supplemental/likelySubtags.json',
    '!json-loader!cldr-data/supplemental/numberingSystems.json',
    '!json-loader!cldr-data/main/' + window.language + '/numbers.json',  // language fix already applied (e.g. en-gb is en-GB)
    'globalize/dist/globalize-runtime/number'
], function(Globalize, likelySubtags, numberingSystems, numbers) {
    'use strict';

    Globalize.load(numbers);
    Globalize.load(likelySubtags);
    Globalize.load(numberingSystems);

    return Globalize(window.language);
});
