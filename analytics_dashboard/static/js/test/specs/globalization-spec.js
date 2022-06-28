// eslint-disable-next-line import/no-unresolved
define(['utils/globalization'], (Globalization) => {
  'use strict';

  describe('Globalization', () => {
    // globalization functionality (e.g. number formatting) is tested in utils-spec
    it('should be returned', () => {
      expect(Globalization).toBeDefined();
    });
  });
});
