define(['utils/fix-language'], function(fixLanguages) {
    'use strict';

    function expectLanguages(actualLanguages, expectedLanguageCode) {
        actualLanguages.forEach(function(languageCode) {
            expect(fixLanguages(languageCode), expectedLanguageCode);
        });
    }

    describe('window.language', function() {
        it('should default to English if an invalid argument is provided or not known to CLDR', function() {
            expectLanguages([null, '', 1, false, 'not-real'], 'en');
        });

        it('should return zh if the given language code is either zh-cn, zh-sg and zh-hans(-*) ', function() {
            expectLanguages(['zh-cn', 'zh-sg', 'zh-hans', 'zh-hans-cn'], 'zh');
        });

        it('should return zh-Hant if the given language code is either zh-tw, zh-hk, zh-mo and zh-hant-* ',
            function() {
                expectLanguages(['zh-tw', 'zh-hk', 'zh-mo', 'zh-hant-tw'], 'zh-Hant');
            }
        );

        it('should return correct-casing any given cased language code', function() {
            expectLanguages(['en-gb', 'en-GB', 'EN-GB'], 'en-GB');
        });
    });
});
