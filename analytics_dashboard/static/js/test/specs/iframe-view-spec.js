define(['jquery', 'views/iframe-view'], ($, IFrameView) => {
  'use strict';

  describe('IFrameView', () => {
    it('should set src', () => {
      const el = document.createElement('div');

      el.dataset.src = 'http://example.com';
      const iframe = new IFrameView({
        el,
      });
      iframe.render();
      expect(el.getAttribute('src')).toEqual('http://example.com');
    });

    it('should hide the loading selector', () => {
      const el = document.createElement('div');
      const iframe = new IFrameView({
        el,
        loadingSelector: document.createElement('div').setAttribute('id', 'loading'),
      });
      iframe.render();

      expect(document.getElementById('loading')).toBeDefined();

      $(el).trigger('load');
      expect(document.getElementById('loading')).toBeNull();
    });
  });
});
