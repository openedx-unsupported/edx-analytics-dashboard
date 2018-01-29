// eslint-disable-next-line import/no-unresolved
define(['utils/globalization'], function(Globalization) {
    'use strict';

    describe('Globalization', function() {
        // globalization functionality (e.g. number formatting) is tested in utils-spec
        it('should be returned', function() {
            expect(Globalization).toBeDefined();
        });
    });
});
