define(function(require) {
    'use strict';

    var PageModel = require('components/generic-list/common/models/page'),
        $ = require('jquery');

    describe('PageModel', function() {
        var titleConstantPart = 'edx/DemoX/Demo_Course | Open edX Insights';

        beforeEach(function() {
            // Setup default page title
            $('title').text('List - ' + titleConstantPart);
        });

        it('should have all the expected default fields', function() {
            var page = new PageModel();
            expect(page.attributes).toEqual({
                title: '',
                lastUpdated: undefined
            });
        });

        it('should update <title> element on title attribute change', function() {
            var page = new PageModel();
            page.set('title', 'foo');
            expect($('title').text()).toEqual('foo - ' + titleConstantPart);
        });
    });
});
