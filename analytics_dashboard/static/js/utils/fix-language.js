/**
 * In order to localize numbers and dates, the language codes must made those in
 * CLDR.  This module standardizes language code argument so that the
 * correct language settings are loaded.
 */
define([
    'json!cldr-data/availableLocales.json'  // eslint-disable-line import/no-unresolved
], function(availableLocales) {
    'use strict';

    var lowerLocalesMapping = {};
    availableLocales.availableLocales.forEach(function(locale) {
        lowerLocalesMapping[locale.toLowerCase()] = locale;
    });

    return function(languageCode) {
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
    };
});
