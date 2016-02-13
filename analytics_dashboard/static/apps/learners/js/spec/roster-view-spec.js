define([
    'axe-core',
    'jquery',
    'learners/js/collections/learner-collection',
    'learners/js/models/learner-model',
    'learners/js/views/roster-view',
    'underscore',
    'URI'
], function (axe, $, LearnerCollection, LearnerModel, LearnerRosterView, _, URI) {
    'use strict';

    describe('LearnerRosterView', function () {
        var fixtureClass,
            getLastRequest,
            getLastRequestParams,
            getResponseBody,
            getRosterView,
            perPage,
            server,
            verifyErrorHandling;

        perPage = 25;

        fixtureClass  = 'roster-view-fixture';

        getLastRequest = function () {
            return server.requests[server.requests.length - 1];
        };

        getLastRequestParams = function () {
            return (new URI(getLastRequest().url)).query(true);
        };

        getResponseBody = function (numPages, pageNum) {
            return {
                count: numPages * perPage,
                num_pages: numPages,
                results: _.range(perPage * (pageNum - 1), perPage * (pageNum - 1) + perPage).map(function (index) {
                    return {name: 'user ' + index, username: 'user_' + index};
                })
            };
        };

        getRosterView  = function (collectionResponse, collectionOptions) {
            var rosterView = new LearnerRosterView({
                collection: new LearnerCollection(
                    collectionResponse,
                    _.extend({url: 'test-url'}, collectionOptions)
                ),
                el: '.' + fixtureClass
            }).render();
            rosterView.onBeforeShow();
            return rosterView;
        };

        verifyErrorHandling = function (rosterView, status, expectedMessage) {
            getLastRequest().respond(status, {}, '');
            expect(rosterView.trigger).toHaveBeenCalledWith('appError', expectedMessage);
        };

        beforeEach(function () {
            setFixtures('<div class="' + fixtureClass + '"></div>');
            server = sinon.fakeServer.create();  // jshint ignore:line
        });

        afterEach(function () {
            server.restore();
        });

        it('displays the last updated date', function () {
            var roster = getRosterView({results: [{last_updated: new Date('1/1/2016')}]}, {parse: true});
            expect(roster.$('.last-updated-message')).toContainText('Date Last Updated: January 1, 2016');
        });

        it('renders a list of learners', function () {
            var generateEngagements = function () {
                    return {
                        discussion_contributions: Math.floor(Math.random() * 10),
                        problems_attempted: Math.floor(Math.random() * 10),
                        problems_completed: Math.floor(Math.random() * 10),
                        videos_viewed: Math.floor(Math.random() * 10),
                        problem_attempts_per_completed: Math.floor(Math.random() * 10)
                    };
                },
                learners = [
                    {name: 'agnes', username: 'agnes', engagements: generateEngagements()},
                    {name: 'lily', username: 'lily', engagements: generateEngagements()},
                    {name: 'zita', username: 'zita', engagements: generateEngagements()}
                ],
                rosterView = getRosterView({results: learners}, {parse: true});
            _.chain(_.zip(learners, rosterView.$('tbody tr'))).each(function (learnerAndTr) {
                var learner = learnerAndTr[0],
                    tr = learnerAndTr[1];
                expect($(tr).find('td.learner-name-username-cell .name')).toContainText(learner.name);
                expect($(tr).find('td.learner-name-username-cell .username')).toContainText(learner.username);
                expect($(tr).find('td.discussion_contributions'))
                    .toContainText(learner.engagements.discussion_contributions);
                expect($(tr).find('td.problems_attempted'))
                    .toContainText(learner.engagements.problems_attempted);
                expect($(tr).find('td.problem_attempts_per_completed'))
                    .toContainText(learner.engagements.problem_attempts_per_completed);
                expect($(tr).find('td.videos_viewed'))
                    .toContainText(learner.engagements.videos_viewed);
            });
        });

        describe('sorting', function () {
            var clickSortingHeader, executeSortTest, expectSortCalled, getSortingHeaderLink;

            getSortingHeaderLink = function (headerClass) {
                return $('th.' + headerClass + ' a');
            };

            clickSortingHeader = function (headerClass) {
                getSortingHeaderLink(headerClass).click();
            };

            executeSortTest = function (field) {
                expect(getSortingHeaderLink(field).find('i')).toHaveClass('fa-sort');
                clickSortingHeader(field);
                expectSortCalled(field, 'asc');
                clickSortingHeader(field);
                expectSortCalled(field, 'desc');
            };

            expectSortCalled = function (sortField, sortValue) {
                expect(getLastRequestParams()).toEqual(jasmine.objectContaining({
                    order_by: sortField,
                    sort_order: sortValue
                }));
                getLastRequest().respond(200, {}, JSON.stringify(getResponseBody(1, 1)));
                expect(getSortingHeaderLink(sortField).find('i')).toHaveClass('fa-sort-' + sortValue);
            };

            beforeEach(function () {
                this.rosterView = getRosterView();
            });

            it('can sort by username', function () {
                executeSortTest('username');
            });

            it('can sort by discussion contributions', function () {
                executeSortTest('discussion_contributions');
            });

            it('can sort by problems attempted', function () {
                executeSortTest('problems_attempted');
            });

            it('can sort by attempts per problem completed', function () {
                executeSortTest('problem_attempts_per_completed');
            });

            it('can sort by videos watched', function () {
                executeSortTest('videos_viewed');
            });

            it('handles server errors', function () {
                spyOn(this.rosterView, 'trigger');
                clickSortingHeader('username');
                verifyErrorHandling(
                    this.rosterView, 500, 'Server error: your request could not be processed. Reload the page to try again.' // jshint ignore:line
                );
                clickSortingHeader('username');
                verifyErrorHandling(this.rosterView, 504, '504: Server error: processing your request took too long to complete. Reload the page to try again.'); // jshint ignore:line
            });
        });

        describe('paging', function () {
            var clickPagingControl,
                createTwoPageRoster,
                expectLinkStates,
                expectRequestedPage;

            clickPagingControl = function (titleSelector) {
                $('a[title="' + titleSelector + '"]').click();
            };

            createTwoPageRoster = function () {
                return getRosterView(getResponseBody(2, 1), {parse: true});
            };

            expectLinkStates = function (rosterView, activeLinkTitle, disabledLinkTitles) {
                rosterView.$('li > a').each(function (_index, link) {
                    var $link = $(link),
                        $parentLi = $link.parent('li');
                    if ($link.attr('title') === activeLinkTitle) {
                        expect($parentLi).toHaveClass('active');
                        expect($parentLi).not.toHaveClass('disabled');
                    } else if (_.contains(disabledLinkTitles, $link.attr('title'))) {
                        expect($parentLi).not.toHaveClass('active');
                        expect($parentLi).toHaveClass('disabled');
                    } else {
                        expect($parentLi).not.toHaveClass('active');
                        expect($parentLi).not.toHaveClass('disabled');
                    }
                });
            };

            expectRequestedPage = function (pageNum) {
                expect(getLastRequestParams()).toEqual(jasmine.objectContaining({
                    page: pageNum.toString()
                }));
            };

            it('can jump to a particular page', function () {
                var rosterView = createTwoPageRoster();
                clickPagingControl('Page 2');
                expectRequestedPage(2);
                getLastRequest().respond(200, {}, JSON.stringify(getResponseBody(2, 2)));
                expectLinkStates(rosterView, 'Page 2', ['Next', 'Last']);
            });

            it('can navigate to the next/previous page', function () {
                var rosterView = createTwoPageRoster();

                clickPagingControl('Next');
                expectRequestedPage(2);
                getLastRequest().respond(200, {}, JSON.stringify(getResponseBody(2, 2)));
                expectLinkStates(rosterView, 'Page 2', ['Next', 'Last']);

                clickPagingControl('Previous');
                expectRequestedPage(1);
                getLastRequest().respond(200, {}, JSON.stringify(getResponseBody(2, 1)));
                expectLinkStates(rosterView, 'Page 1', ['First', 'Previous']);
            });

            it('does not enable pagination controls for unreachable pages', function () {
                var rosterView = createTwoPageRoster();
                // Verify no request, no view change
                clickPagingControl('Previous');
                expect(server.requests.length).toBe(0);
                expectLinkStates(rosterView, 'Page 1', ['First', 'Previous']);
            });

            it('handles gateway timeouts', function () {
                var rosterView = createTwoPageRoster();
                spyOn(rosterView, 'trigger');
                clickPagingControl('Next');
                verifyErrorHandling(rosterView, 504, '504: Server error: processing your request took too long to complete. Reload the page to try again.'); // jshint ignore:line
            });

            it('handles server errors', function () {
                var rosterView = createTwoPageRoster();
                spyOn(rosterView, 'trigger');
                clickPagingControl('Next');
                verifyErrorHandling(
                    rosterView, 500, 'Server error: your request could not be processed. Reload the page to try again.' // jshint ignore:line
                );
            });
        });

        describe('search', function () {
            var executeSearch, expectSearchedFor;

            executeSearch = function (searchString) {
                $('#search-learners').val(searchString);
                $('#search-learners').keyup();  // Triggers rendering of the clear search control
                $('#search-learners').submit();
            };

            expectSearchedFor = function (searchString) {
                expect(getLastRequestParams()).toEqual(jasmine.objectContaining({
                    text_search: searchString
                }));
            };

            it('can search for arbitrary strings', function () {
                var searchString = 'search string';
                getRosterView();
                executeSearch(searchString);
                expect(getLastRequestParams()).toEqual(jasmine.objectContaining({
                    text_search: searchString
                }));
            });

            it('can clear the search with the clear link', function () {
                var searchString = 'search string';
                getRosterView();
                executeSearch(searchString);
                expectSearchedFor(searchString);
                getLastRequest().respond(200, {}, JSON.stringify(getResponseBody(1, 1)));
                $('a.clear').click();
                expect(getLastRequestParams().text_search).toBeUndefined();
            });

            it('can clear the search by searching the empty string', function () {
                var searchString = 'search string';
                getRosterView();
                executeSearch(searchString);
                expectSearchedFor(searchString);
                getLastRequest().respond(200, {}, JSON.stringify(getResponseBody(1, 1)));
                executeSearch('');
                expect(getLastRequestParams().text_search).toBeUndefined();
            });

            it('handles server errors', function () {
                var rosterView = getRosterView();
                spyOn(rosterView, 'trigger');
                executeSearch('test search');
                verifyErrorHandling(rosterView, 504, '504: Server error: processing your request took too long to complete. Reload the page to try again.'); // jshint ignore:line
                executeSearch('test search');
                verifyErrorHandling(
                    rosterView, 500, 'Server error: your request could not be processed. Reload the page to try again.' // jshint ignore:line
                );
            });
        });

        describe('accessibility', function () {
            it('the table has a <caption> element', function () {
                var rosterView = getRosterView();
                expect(rosterView.$('table > caption')).toBeInDOM();
            });

            it('all <th> elements have scope attributes', function () {
                var rosterView = getRosterView();
                rosterView.$('th').each(function (_index, $th) {
                    expect($th).toHaveAttr('scope', 'col');
                });
            });

            it('all <th> elements have screen reader text', function () {
                var rosterView = getRosterView(),
                    screenReaderTextSelector = '.sr-sorting-text',
                    sortColumnSelector = '.username.sortable';
                rosterView.$('th').each(function (_index, th) {
                    expect($(th).find(screenReaderTextSelector)).toHaveText('click to sort');
                });
                rosterView.$(sortColumnSelector + ' > a').click();
                expect(rosterView.$(sortColumnSelector).find(screenReaderTextSelector)).toHaveText('sort ascending');
                rosterView.$(sortColumnSelector + ' > a').click();
                expect(rosterView.$(sortColumnSelector).find(screenReaderTextSelector)).toHaveText('sort descending');
            });

            it('the search input has a label', function () {
                var rosterView = getRosterView(),
                    inputId = rosterView.$('input').attr('id'),
                    $label = rosterView.$('label');
                expect($label).toHaveAttr('for', inputId);
                expect($label).toHaveText('Search learners');
            });

            it('all icons should be aria-hidden', function () {
                var rosterView = getRosterView();
                rosterView.$('i').each(function (_index, el) {
                    expect($(el)).toHaveAttr('aria-hidden', 'true');
                });
            });

            it('sets focus to the top of the table after taking a paging action', function () {
                var rosterView = getRosterView(getResponseBody(2, 1), {parse: true}),
                    firstPageLink = rosterView.$('.backgrid-paginator li a[title="Page 1"]'),
                    secondPageLink = rosterView.$('.backgrid-paginator li a[title="Page 2"]');
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
                expect($('#learner-app-focusable').focus).toHaveBeenCalled();
            });

            it('does not violate the axe-core ruleset', function (done) {
                getRosterView(getResponseBody(1, 1), {parse: true});
                axe.a11yCheck($('.roster-view-fixture')[0], function (result) {
                    expect(result.violations.length).toBe(0);
                    done();
                });
            });
        });
    });
});
