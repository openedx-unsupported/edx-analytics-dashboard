define(function(require) {
    'use strict';

    var $ = require('jquery'),
        _ = require('underscore'),
        axe = require('axe-core'),

        Collection = require('generic-list/common/collections/collection'),
        ListView = require('generic-list/list/views/list'),
        TrackingModel = require('models/tracking-model');

    describe('ListView', function() {
        var fixtureClass = 'list-view-fixture',
            perPage = 25,
            executeSearch,
            getLastRequest,
            getResponseBody,
            getListView,
            server;

        getLastRequest = function() {
            return server.requests[server.requests.length - 1];
        };

        getResponseBody = function(numPages, pageNum) {
            var results,
                page = pageNum || 1;
            if (numPages) {
                results = _.range(perPage * (page - 1), perPage * (page - 1) + perPage).map(function(index) {
                    return {name: 'user ' + index, username: 'user_' + index};
                });
            } else {
                results = [];
            }
            return {
                count: numPages * perPage,
                num_pages: numPages,
                results: results
            };
        };

        getListView = function(options) {
            var collection,
                listView,
                defaultOptions = _.defaults({mode: 'server'}, options);
            collection = defaultOptions.collection || new Collection(
                defaultOptions.collectionResponse,
                _.extend({url: 'test-url'}, defaultOptions.collectionOptions)
            );
            listView = new ListView({
                collection: collection,
                el: '.' + fixtureClass,
                hasData: true,
                trackingModel: new TrackingModel()
            }).render();
            listView.onBeforeShow();
            return listView;
        };

        beforeEach(function() {
            setFixtures('<div class="' + fixtureClass + '"></div>');
            server = sinon.fakeServer.create();
        });

        afterEach(function() {
            server.restore();
        });

        describe('accessibility', function() {
            it('the table has a <caption> element', function() {
                var listView = getListView({
                    collectionResponse: getResponseBody(1, 1),
                    collectionOptions: {parse: true}
                });
                expect(listView.$('table > caption')).toBeInDOM();
            });

            it('all <th> elements have scope attributes', function() {
                var listView = getListView({
                    collectionResponse: getResponseBody(1, 1),
                    collectionOptions: {parse: true}
                });
                listView.$('th').each(function(_index, $th) {
                    expect($th).toHaveAttr('scope', 'col');
                });
            });

            it('all <th> elements have screen reader text', function() {
                var listView = getListView({
                        collectionResponse: getResponseBody(1, 1),
                        collectionOptions: {parse: true}
                    }),
                    screenReaderTextSelector = '.sr-sorting-text',
                    sortColumnSelector = '.username.sortable';
                listView.$('th').each(function(_index, th) {
                    expect($(th).find(screenReaderTextSelector)).toHaveText('click to sort');
                });
                listView.$(sortColumnSelector + ' > a').click();
                expect(listView.$(sortColumnSelector).find(screenReaderTextSelector)).toHaveText('sort ascending');
                listView.$(sortColumnSelector + ' > a').click();
                expect(listView.$(sortColumnSelector).find(screenReaderTextSelector)).toHaveText('sort descending');
            });

            it('all icons should be aria-hidden', function() {
                var listView = getListView({
                    collectionResponse: getResponseBody(1, 1),
                    collectionOptions: {parse: true}
                });
                listView.$('i').each(function(_index, el) {
                    expect($(el)).toHaveAttr('aria-hidden', 'true');
                });
            });

            it('sets focus to the top of the table after taking a paging action', function() {
                var listView = getListView({
                        collectionResponse: getResponseBody(2, 1),
                        collectionOptions: {parse: true}
                    }),
                    firstPageLink = listView.$('.backgrid-paginator li a[title="Page 1"]'),
                    secondPageLink = listView.$('.backgrid-paginator li a[title="Page 2"]');
                // It would be ideal to use jasmine-jquery's
                // expect(...).toBeFocused(), but that doesn't seem to
                // be working with jQuery's focus method.  A spy is
                // the next-best option.
                spyOn($.fn, 'focus');
                firstPageLink.click();
                // The first page link is disabled, and since we
                // haven't changed pages, it should receive focus.
                expect(firstPageLink.focus).toHaveBeenCalled();
                secondPageLink.click();
                // The second page link is not disabled, and after
                // clicking it, we should set focus to the top of the
                // table.
                getLastRequest().respond(200, {}, JSON.stringify(getResponseBody(2, 2)));
                expect($('#app-focusable').focus).toHaveBeenCalled();
            });

            it('sets focus to the top after searching', function() {
                var searchString = 'search string';
                getListView();
                spyOn($.fn, 'focus');
                executeSearch(searchString);
                expect($('#app-focusable').focus).toHaveBeenCalled();
            });

            it('does not violate the axe-core ruleset', function(done) {
                getListView({
                    collectionResponse: getResponseBody(1, 1),
                    collectionOptions: {parse: true}
                });
                axe.a11yCheck($('.list-view-fixture')[0], function(result) {
                    expect(result.violations.length).toBe(0);
                    done();
                });
            });
        });
    });
});
