if (window.language === undefined) { // should only occur in test environments
    window.language = 'en';
}

/**
 * Returns the Globalize object for localizing dates and numbers.  window.language
 * is expected to be standardized to those used in CLDR.  See js/load/init-page.js
 * for setting window.language.
 */
define([
    'globalize',
    'json!cldr-data/supplemental/likelySubtags.json',
    'json!cldr-data/supplemental/numberingSystems.json',
    'json!cldr-data/main/' + window.language + '/numbers.json',  // language fix already applied (e.g. en-gb is en-GB)
    'globalize/number'
], function(Globalize, likelySubtags, numberingSystems, numbers) {
    'use strict';

    Globalize.load(numbers);
    Globalize.load(likelySubtags);
    Globalize.load(numberingSystems);

    return Globalize(window.language);
});
