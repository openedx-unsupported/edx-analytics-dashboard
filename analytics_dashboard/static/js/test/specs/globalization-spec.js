/* jshint ignore:start */
define(['utils/globalization'], function () {
    'use strict';

    describe('fixLanguageCode', function () {
        it('should default to English if an invalid argument is provided', function () {
            expect(fixLanguageCode(null)).toEqual('en');
            expect(fixLanguageCode('')).toEqual('en');
            expect(fixLanguageCode(1)).toEqual('en');
            expect(fixLanguageCode(true)).toEqual('en');
        });

        it('should return zh if the given language code is zh-cn', function () {
            expect(fixLanguageCode('zh-cn')).toEqual('zh');
        });

        it('should return en if the given language code is not known to CLDR', function () {
            expect(fixLanguageCode('not-real')).toEqual('en');
        });
    });
});
/* jshint ignore:end */
