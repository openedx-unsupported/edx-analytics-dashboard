function fixLanguageCode(languageCode) {
    'use strict';

    if (!languageCode || typeof languageCode !== 'string') {
        return 'en';
    }

    languageCode = languageCode.toLowerCase();

    // Django uses zh-cn. CLDR uses zh.
    if (languageCode === 'zh-cn') {
        return 'zh';
    }

    // There doesn't seem to be an onFailure event for the text! plugin. Make sure we only pass valid language codes
    // so the plugin does not attempt to load non-existent files.
    if (['ar', 'ca', 'cs', 'da', 'de', 'el', 'en-001', 'en-au', 'en-ca', 'en-gb', 'en-hk', 'en-in', 'en', 'es', 'fi',
        'fr', 'he', 'hi', 'hr', 'hu', 'it', 'ja', 'ko', 'nb', 'nl', 'pl', 'pt-pt', 'pt', 'ro', 'root', 'ru', 'sk', 'sl',
        'sr', 'sv', 'th', 'tr', 'uk', 'vi', 'zh-hant', 'zh'].indexOf(languageCode) > -1) {
        return languageCode;
    }

    return 'en';
}

window.language = fixLanguageCode(window.language);

define([
    'globalize',
    'json!cldr-data/supplemental/likelySubtags.json',
    'json!cldr-data/supplemental/numberingSystems.json',
    'json!cldr-data/main/' + window.language + '/numbers.json',
    'globalize/number'
], function (Globalize, likelySubtags, numberingSystems, numbers) {
    'use strict';

    Globalize.load(likelySubtags);
    Globalize.load(numberingSystems);
    Globalize.load(numbers);

    return Globalize(window.language);  // jshint ignore:line
});
