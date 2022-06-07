define(['models/user-model'], (UserModel) => {
  'use strict';

  describe('user model', () => {
    describe('ignoreInReporting', () => {
      it('should default to false', () => {
        const model = new UserModel();
        expect(model.get('ignoreInReporting')).toBe(false);
      });
    });
  });
});
