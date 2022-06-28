define((require) => {
  'use strict';

  const $ = require('jquery');

  const SkipLinkView = require('components/skip-link/views/skip-link-view');

  describe('SkipLinkView', () => {
    it('sets focus when clicked', () => {
      const view = new SkipLinkView({
        el: 'body',
        template: false,
      });
      setFixtures('<a id="skip" href="#content" class="skip-link">Testing</a><div id="content">a div</div>');

      view.render();

      // because it's difficult to test that element has been scrolled to, test check that
      // the method has been called
      spyOn($('#content')[0], 'scrollIntoView').and.callThrough();

      expect($('#content')[0]).not.toBe(document.activeElement);

      $('.skip-link').click();
      expect($('#content')[0]).toBe(document.activeElement);
      expect($('#content')[0].scrollIntoView).toHaveBeenCalled();
    });
  });
});
