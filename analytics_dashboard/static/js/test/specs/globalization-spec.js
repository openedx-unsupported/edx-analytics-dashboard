define(['utils/globalization'], function() {
    'use strict';

    describe('fixLanguageCode', function() {
        it('should default to English if an invalid argument is provided', function() {
            expect(fixLanguageCode(null)).toEqual('en');
            expect(fixLanguageCode('')).toEqual('en');
            expect(fixLanguageCode(1)).toEqual('en');
            expect(fixLanguageCode(true)).toEqual('en');
        });

        it('should return zh if the given language code is either zh-cn, zh-sg and zh-hans(-*) ', function() {
            expect(fixLanguageCode('zh-cn')).toEqual('zh');
            expect(fixLanguageCode('zh-sg')).toEqual('zh');
            expect(fixLanguageCode('zh-hans')).toEqual('zh');
            expect(fixLanguageCode('zh-hans-cn')).toEqual('zh');
        });

        it('should return zh-hant if the given language code is either zh-tw, zh-hk, zh-mo and zh-hant-* ', function() {
            expect(fixLanguageCode('zh-tw')).toEqual('zh-hant');
            expect(fixLanguageCode('zh-hk')).toEqual('zh-hant');
            expect(fixLanguageCode('zh-mo')).toEqual('zh-hant');
            expect(fixLanguageCode('zh-hant-tw')).toEqual('zh-hant');
        });

        it('should return en if the given language code is not known to CLDR', function() {
            expect(fixLanguageCode('not-real')).toEqual('en');
        });
    });
});
