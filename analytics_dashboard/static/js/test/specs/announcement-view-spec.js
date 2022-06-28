define(['views/announcement-view', 'jquery', 'underscore'], (AnnouncementView, $, _) => {
  'use strict';

  let view; let $el;
  const csrftoken = '1234';
  const url = 'http://example.com';
  const template = _.template('<div id="announcement" data-dismiss-url="<%=url%>">'
            + '<input type="hidden" name="csrfmiddlewaretoken" value="<%=csrftoken%>">'
            + '<a class="dismiss">Close</a></div>');

  describe('AnnouncementView', () => {
    beforeEach(() => {
      // Create DOM elements
      $el = $(template({ url, csrftoken }));
      $(document.body).append($el);

      // Instantiate view
      view = new AnnouncementView({ el: $el[0] });
    });

    describe('init', () => {
      it('should retrieve the CSRF token from the hidden input', () => {
        expect(view.csrftoken).toEqual(csrftoken);
      });
    });

    it('should call dismiss when the dismiss element is clicked', () => {
      spyOn(view, 'dismiss');

      view.delegateEvents();
      $('.dismiss', $el).click();

      expect(view.dismiss).toHaveBeenCalled();
    });

    describe('dismiss', () => {
      let server;

      beforeEach(() => {
        server = sinon.fakeServer.create();
        view.dismiss();
      });

      afterEach(() => {
        server.restore();
      });

      it('should add the CSRF token to the header', () => {
        const request = server.requests[0];
        expect(request.requestHeaders['X-CSRFToken']).toEqual(csrftoken);
      });

      it('should POST to the dismiss URL', () => {
        view.dismiss();

        const [request] = server.requests;
        expect(request.method).toEqual('POST');
        expect(request.url).toEqual(url);
      });
    });
  });
});
