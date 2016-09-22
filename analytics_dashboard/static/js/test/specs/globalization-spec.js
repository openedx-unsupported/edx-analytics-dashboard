// eslint-disable-next-line import/no-unresolved
define(['json!cldr-data/availableLocales.json', 'utils/globalization'], function(availableLocales) {
    'use strict';

    var lowerLocalesMapping = {};
    availableLocales.availableLocales.forEach(function(locale) {
        lowerLocalesMapping[locale.toLowerCase()] = locale;
    });

    describe('fixLanguageCode', function() {
        it('should default to English if an invalid argument is provided', function() {
            expect(fixLanguageCode(null, lowerLocalesMapping)).toEqual('en');
            expect(fixLanguageCode('', lowerLocalesMapping)).toEqual('en');
            expect(fixLanguageCode(1, lowerLocalesMapping)).toEqual('en');
            expect(fixLanguageCode(true, lowerLocalesMapping)).toEqual('en');
        });

        it('should return zh if the given language code is either zh-cn, zh-sg and zh-hans(-*) ', function() {
            expect(fixLanguageCode('zh-cn', lowerLocalesMapping)).toEqual('zh');
            expect(fixLanguageCode('zh-sg', lowerLocalesMapping)).toEqual('zh');
            expect(fixLanguageCode('zh-hans', lowerLocalesMapping)).toEqual('zh');
            expect(fixLanguageCode('zh-hans-cn', lowerLocalesMapping)).toEqual('zh');
        });

        it('should return zh-Hant if the given language code is either zh-tw, zh-hk, zh-mo and zh-hant-* ', function() {
            expect(fixLanguageCode('zh-tw', lowerLocalesMapping)).toEqual('zh-Hant');
            expect(fixLanguageCode('zh-hk', lowerLocalesMapping)).toEqual('zh-Hant');
            expect(fixLanguageCode('zh-mo', lowerLocalesMapping)).toEqual('zh-Hant');
            expect(fixLanguageCode('zh-hant-tw', lowerLocalesMapping)).toEqual('zh-Hant');
        });

        it('should return en if the given language code is not known to CLDR', function() {
            expect(fixLanguageCode('not-real', lowerLocalesMapping)).toEqual('en');
        });

        it('should return correct-casing any given cased language code', function() {
            expect(fixLanguageCode('en-gb', lowerLocalesMapping)).toEqual('en-GB');
            expect(fixLanguageCode('en-GB', lowerLocalesMapping)).toEqual('en-GB');
            expect(fixLanguageCode('EN-GB', lowerLocalesMapping)).toEqual('en-GB');
        });
    });
});
