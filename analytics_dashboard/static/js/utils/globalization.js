if (window.language === undefined) { // should only occur in test environments
    window.language = 'en';
}

function fixLanguageCode(languageCode, lowerLocalesMapping) {
    'use strict';
    var fixedLanguageCode;

    if (!languageCode || typeof languageCode !== 'string') {
        return 'en';
    }

    fixedLanguageCode = languageCode.toLowerCase();

    // CLDR uses zh for Simplified Chinese, while Django may use different strings.
    if (fixedLanguageCode === 'zh-cn' || fixedLanguageCode === 'zh-sg' ||
        fixedLanguageCode.indexOf('zh-hans') === 0) {
        fixedLanguageCode = 'zh';
    }
    // CLDR uses zh-hant for Traditional Chinese, while Django may use different strings.
    if (fixedLanguageCode === 'zh-tw' || fixedLanguageCode === 'zh-hk' ||
        fixedLanguageCode === 'zh-mo' || fixedLanguageCode.indexOf('zh-hant') === 0) {
        fixedLanguageCode = 'zh-hant';
    }

    // There doesn't seem to be an onFailure event for the text! plugin. Make sure we only pass valid language codes
    // so the plugin does not attempt to load non-existent files.
    if (fixedLanguageCode in lowerLocalesMapping) {
        return lowerLocalesMapping[fixedLanguageCode];
    }

    return 'en';
}

define([
    'globalize',
    'json!cldr-data/supplemental/likelySubtags.json',
    'json!cldr-data/supplemental/numberingSystems.json',
    'json!cldr-data/availableLocales.json',  // eslint-disable-line import/no-unresolved
    'json!cldr-data/main/' + window.language + '/numbers.json',
    'globalize/number'
], function(Globalize, likelySubtags, numberingSystems, availableLocales, numbers) {
    'use strict';

    var lowerLocalesMapping = {};
    availableLocales.availableLocales.forEach(function(locale) {
        lowerLocalesMapping[locale.toLowerCase()] = locale;
    });

    window.language = fixLanguageCode(window.language, lowerLocalesMapping);

    Globalize.load(likelySubtags);
    Globalize.load(numberingSystems);
    Globalize.load(numbers);

    return Globalize(window.language);
});
