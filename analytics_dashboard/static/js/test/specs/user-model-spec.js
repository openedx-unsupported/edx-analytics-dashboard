define(['models/user-model'], function (UserModel) {
    'use strict';

    describe('user model', function () {
        describe('ignoreInReporting', function () {

            it('should default to false', function () {
                var model = new UserModel();
                expect(model.get('ignoreInReporting')).toBe(false);
            });
        });
    });
});
