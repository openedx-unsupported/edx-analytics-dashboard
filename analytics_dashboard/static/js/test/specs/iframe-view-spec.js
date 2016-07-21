define(['jquery', 'views/iframe-view'], function($, IFrameView) {
    'use strict';

    describe('IFrameView', function() {
        it('should set src', function() {
            var el = document.createElement('div'),
                iframe;

            el.dataset.src = 'http://example.com';
            iframe = new IFrameView({
                el: el
            });
            iframe.render();
            expect(el.getAttribute('src')).toEqual('http://example.com');
        });

        it('should hide the loading selector', function() {
            var el = document.createElement('div'),
                iframe;
            iframe = new IFrameView({
                el: el,
                loadingSelector: document.createElement('div').setAttribute('id', 'loading')
            });
            iframe.render();

            expect(document.getElementById('loading')).toBeDefined();

            $(el).trigger('load');
            expect(document.getElementById('loading')).toBeNull();
        });
    });
});
