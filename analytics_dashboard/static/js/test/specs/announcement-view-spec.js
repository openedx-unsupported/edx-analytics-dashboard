define(['views/announcement-view', 'jquery', 'underscore'], function (AnnouncementView, $, _) {
    'use strict';

    var view, $el,
        csrftoken = '1234',
        url = 'http://example.com',
        template = _.template('<div id="announcement" data-dismiss-url="<%=url%>">' +
            '<input type="hidden" name="csrfmiddlewaretoken" value="<%=csrftoken%>">' +
            '<a class="dismiss">Close</a></div>');

    describe('AnnouncementView', function () {
        beforeEach(function () {
            // Create DOM elements
            $el = $(template({url: url, csrftoken: csrftoken}));
            $(document.body).append($el);

            // Instantiate view
            view = new AnnouncementView({el: $el[0]});
        });

        describe('init', function () {
            it('should retrieve the CSRF token from the hidden input', function () {
                expect(view.csrftoken).toEqual(csrftoken);
            });
        });

        it('should call dismiss when the dismiss element is clicked', function () {
            spyOn(view, 'dismiss');

            view.delegateEvents();
            $('.dismiss', $el).click();

            expect(view.dismiss).toHaveBeenCalled();
        });

        describe('dismiss', function () {
            var server;

            beforeEach(function () {
                server = sinon.fakeServer.create(); // jshint ignore:line
                view.dismiss();
            });

            afterEach(function () {
                server.restore();
            });

            it('should add the CSRF token to the header', function () {
                var request = server.requests[0];
                expect(request.requestHeaders['X-CSRFToken']).toEqual(csrftoken);
            });

            it('should POST to the dismiss URL', function () {
                view.dismiss();

                var request = server.requests[0];
                expect(request.method).toEqual('POST');
                expect(request.url).toEqual(url);
            });
        });
    });
});
