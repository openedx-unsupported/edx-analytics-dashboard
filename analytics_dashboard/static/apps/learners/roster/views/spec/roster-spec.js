define(function(require) {
    'use strict';

    var $ = require('jquery'),
        _ = require('underscore'),
        axe = require('axe-core'),
        SpecHelpers = require('uitk/utils/spec-helpers/spec-helpers'),
        URI = require('URI'),

        CourseMetadataModel = require('learners/common/models/course-metadata'),
        LearnerCollection = require('learners/common/collections/learners'),
        LearnerRosterView = require('learners/roster/views/roster'),
        TrackingModel = require('models/tracking-model');

    describe('LearnerRosterView', function() {
        var fixtureClass = 'roster-view-fixture',
            perPage = 25,
            clickPagingControl,
            executeSearch,
            getLastRequest,
            getLastRequestParams,
            getResponseBody,
            getRosterView,
            server,
            testTimeout,
            verifyErrorHandling;

        getLastRequest = function() {
            return server.requests[server.requests.length - 1];
        };

        getLastRequestParams = function() {
            return (new URI(getLastRequest().url)).query(true);
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

        getRosterView = function(options) {
            var collection,
                rosterView,
                defaultOptions = _.defaults({}, options);
            collection = defaultOptions.collection || new LearnerCollection(
                defaultOptions.collectionResponse,
                _.extend({url: 'test-url'}, defaultOptions.collectionOptions)
            );
            rosterView = new LearnerRosterView({
                collection: collection,
                courseMetadata: defaultOptions.courseMetadataModel ||
                    new CourseMetadataModel(defaultOptions.courseMetadata, {parse: true}),
                el: '.' + fixtureClass,
                trackSubject: 'roster',
                hasData: true,
                trackingModel: new TrackingModel()
            }).render();
            rosterView.onBeforeShow();
            return rosterView;
        };

        testTimeout = function(rosterView, actionFunction) {
            var ajaxSetup;
            jasmine.clock().install();
            ajaxSetup = $.ajaxSetup();
            $.ajaxSetup({timeout: 1});
            spyOn(rosterView, 'trigger');
            actionFunction();
            jasmine.clock().tick(2);
            expect(rosterView.trigger).toHaveBeenCalledWith(
                'appError',
                {
                    title: 'Network error',
                    description: 'Your request could not be processed. Reload the page to try again.'
                }
            );
            jasmine.clock().uninstall();
            $.ajaxSetup(ajaxSetup);
        };

        verifyErrorHandling = function(rosterView, status) {
            getLastRequest().respond(status, {}, '');
            expect(rosterView.trigger).toHaveBeenCalledWith('appError', jasmine.any(Object));
        };

        executeSearch = function(searchString) {
            $('#search-learners').val(searchString);
            $('#search-learners').keyup();  // Triggers rendering of the clear search control
            $('#search-learners').submit();
        };

        clickPagingControl = function(titleSelector) {
            $('a[title="' + titleSelector + '"]').click();
        };

        beforeEach(function() {
            setFixtures('<div class="' + fixtureClass + '"></div>');
            server = sinon.fakeServer.create();
        });

        afterEach(function() {
            server.restore();
        });

        it('renders a list of learners', function() {
            var generateEngagements = function() {
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
                rosterView = getRosterView({
                    collectionResponse: {results: learners},
                    collectionOptions: {parse: true}
                });
            _.chain(_.zip(learners, rosterView.$('tbody tr'))).each(function(learnerAndTr) {
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

        it('categorizes engagement values', function() {
            var learners = [{
                    name: 'agnes',
                    username: 'agnes',
                    engagements: {
                        discussion_contributions: 10,
                        problems_attempted: 100,
                        problems_completed: 32,
                        videos_viewed: 1,
                        problem_attempts_per_completed: 1.56
                    }
                }],
                engagementRanges = {
                    problems_attempted: {
                        class_rank_bottom: [0, 10],
                        class_rank_average: [11, 25],
                        class_rank_top: [26, null]
                    },
                    videos_viewed: {
                        class_rank_bottom: [0, 1],
                        class_rank_average: [1, 10],
                        class_rank_top: [10, null]
                    },
                    problems_completed: {
                        class_rank_bottom: [0, 10],
                        class_rank_average: [11, 50],
                        class_rank_top: [50, null]
                    },
                    problem_attempts_per_completed: {
                        class_rank_top: [1, 1.6],
                        class_rank_average: [1.6, 25],
                        class_rank_bottom: [26, 60]
                    },
                    discussion_contributions: {
                        class_rank_bottom: [0, 100],
                        class_rank_average: [100, 125],
                        class_rank_top: [125, null]
                    }
                },
                rosterView = getRosterView({
                    collectionResponse: {results: learners},
                    collectionOptions: {parse: true},
                    courseMetadata: {
                        engagement_ranges: engagementRanges
                    }
                }),
                $tr = $(rosterView.$('tbody tr'));

            expect($tr.children('td.discussion_contributions'))
                .toHaveClass('learner-cell-rank-bottom');
            expect($tr.children('td.discussion_contributions ')).toHaveAttr('aria-label', '10 low');
            expect($tr.find('td.problems_completed'))
                .toHaveClass('learner-cell-rank-middle');
            expect($tr.find('td.problems_attempted'))
                .toHaveClass('learner-cell-rank-top');
            expect($tr.find('td.problems_attempted')).toHaveAttr('aria-label', '100 high');
            expect($tr.find('td.problem_attempts_per_completed'))
                .toHaveClass('learner-cell-rank-top');
            expect($tr.find('td.problem_attempts_per_completed')).toHaveAttr('aria-label', '1.56 high');
            expect($tr.find('td.videos_viewed'))
                .toHaveClass('learner-cell-rank-middle');
        });

        it('formats numbers', function() {
            var learners = [{
                    name: 'agnes',
                    username: 'agnes',
                    engagements: {
                        discussion_contributions: 0,
                        problems_attempted: 0,
                        problems_completed: 32,
                        videos_viewed: 0,
                        problem_attempts_per_completed: 0.566
                    }
                }],
                rosterView = getRosterView({
                    collectionResponse: {results: learners},
                    collectionOptions: {parse: true}
                }),
                $tr = $(rosterView.$('tbody tr'));

            expect($tr.children('td.discussion_contributions'))
                .toContainText('0');
            expect($tr.find('td.problems_completed'))
                .toContainText('32');
            expect($tr.find('td.problems_attempted'))
                .toContainText('0');
            expect($tr.find('td.problem_attempts_per_completed'))
                .toContainText('0.6');
            expect($tr.find('td.videos_viewed'))
                .toContainText('0');
        });

        it('displays "infinite" metrics as N/A', function() {
            var learners = [{
                    name: 'agnes',
                    username: 'agnes',
                    engagements: {
                        discussion_contributions: 0,
                        problems_attempted: 0,
                        problems_completed: 0,
                        videos_viewed: 0,
                        problem_attempts_per_completed: null
                    }
                }],
                rosterView = getRosterView({
                    collectionResponse: {results: learners},
                    collectionOptions: {parse: true}
                }),
                $tr = $(rosterView.$('tbody tr'));

            expect($tr.children('td.discussion_contributions'))
                .toContainText('0');
            expect($tr.find('td.problems_completed'))
                .toContainText('0');
            expect($tr.find('td.problems_attempted'))
                .toContainText('0');
            expect($tr.find('td.problem_attempts_per_completed'))
                .toContainText('N/A');
            expect($tr.find('td.videos_viewed'))
                .toContainText('0');
        });

        describe('table headers', function() {
            it('has tooltips', function() {
                var headerClasses = [
                    'username',
                    'videos_viewed',
                    'problems_completed',
                    'problems_attempted',
                    'discussion_contributions',
                    'problem_attempts_per_completed'
                ];

                getRosterView({
                    collectionResponse: getResponseBody(1, 1),
                    collectionOptions: {parse: true}
                });

                _(headerClasses).each(function(headerClass) {
                    var $heading = $('th.' + headerClass).focusin(),
                        $tooltip;

                    // aria tag is added when tooltip is displayed (e.g. on focus)
                    expect($heading).toHaveAttr('aria-describedby');
                    $tooltip = $('#' + $heading.attr('aria-describedby'));
                    expect($tooltip.text().length).toBeGreaterThan(0);
                });
            });
        });

        describe('sorting', function() {
            var clickSortingHeader, executeSortTest, expectSortCalled, getSortingHeaderLink;

            getSortingHeaderLink = function(headerClass) {
                return $('th.' + headerClass + ' a');
            };

            clickSortingHeader = function(headerClass) {
                getSortingHeaderLink(headerClass).click();
            };

            executeSortTest = function(field) {
                expect(getSortingHeaderLink(field).find('span.fa')).toHaveClass('fa-sort');
                clickSortingHeader(field);
                expectSortCalled(field, 'asc');
                clickSortingHeader(field);
                expectSortCalled(field, 'desc');
            };

            expectSortCalled = function(sortField, sortValue) {
                expect(getLastRequestParams()).toEqual(jasmine.objectContaining({
                    order_by: sortField,
                    sort_order: sortValue
                }));
                getLastRequest().respond(200, {}, JSON.stringify(getResponseBody(1, 1)));
                expect(getSortingHeaderLink(sortField).find('span')).toHaveClass('fa-sort-' + sortValue);
            };

            beforeEach(function() {
                this.rosterView = getRosterView({
                    collectionResponse: getResponseBody(1, 1),
                    collectionOptions: {parse: true}
                });
            });

            it('can sort by username', function() {
                executeSortTest('username');
            });

            it('can sort by discussion contributions', function() {
                executeSortTest('discussion_contributions');
            });

            it('can sort by problems attempted', function() {
                executeSortTest('problems_attempted');
            });

            it('can sort by attempts per problem completed', function() {
                executeSortTest('problem_attempts_per_completed');
            });

            it('can sort by videos watched', function() {
                executeSortTest('videos_viewed');
            });

            it('handles server errors', function() {
                spyOn(this.rosterView, 'trigger');
                clickSortingHeader('username');
                verifyErrorHandling(this.rosterView, 500);
                clickSortingHeader('username');
                verifyErrorHandling(this.rosterView, 504);
            });

            it('handles network errors', function() {
                testTimeout(this.rosterView, function() {
                    clickSortingHeader('username');
                });
            });

            it('goes to the first page after applying a sort', function() {
                this.rosterView = getRosterView({
                    collectionResponse: getResponseBody(2, 1),
                    collectionOptions: {parse: true}
                });
                clickPagingControl('Page 2');
                getLastRequest().respond(200, {}, JSON.stringify(getResponseBody(2, 2)));
                expect(this.rosterView.$('a[title="Page 2"]').parent('li')).toHaveClass('active');
                clickSortingHeader('username');
                getLastRequest().respond(200, {}, JSON.stringify(getResponseBody(2, 2)));
                expect(getLastRequestParams()).toEqual(jasmine.objectContaining({
                    page: '1',
                    order_by: 'username'
                }));
                getLastRequest().respond(200, {}, JSON.stringify(getResponseBody(2, 1)));
                expect(this.rosterView.$('a[title="Page 1"]').parent('li')).toHaveClass('active');
            });

            it('triggers a tracking event', function() {
                var triggerSpy = spyOn(this.rosterView.options.trackingModel, 'trigger'),
                    headerClasses = [
                        'username',
                        'videos_viewed',
                        'problems_attempted',
                        'problems_completed',
                        'discussion_contributions',
                        'problem_attempts_per_completed'
                    ];
                _.each(headerClasses, function(column) {
                    executeSortTest(column);
                    expect(triggerSpy).toHaveBeenCalledWith('segment:track', 'edx.bi.roster.sorted', {
                        category: column + '_asc'
                    });
                    expect(triggerSpy).toHaveBeenCalledWith('segment:track', 'edx.bi.roster.sorted', {
                        category: column + '_desc'
                    });
                });
            });
        });

        describe('paging', function() {
            var createTwoPageRoster,
                expectLinkStates,
                expectRequestedPage;

            createTwoPageRoster = function() {
                return getRosterView({
                    collectionResponse: getResponseBody(2, 1),
                    collectionOptions: {parse: true}
                });
            };

            expectLinkStates = function(rosterView, activeLinkTitle, disabledLinkTitles) {
                rosterView.$('li > a').each(function(_index, link) {
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

            expectRequestedPage = function(pageNum) {
                expect(getLastRequestParams()).toEqual(jasmine.objectContaining({
                    page: pageNum.toString()
                }));
            };

            it('triggers a tracking event', function() {
                var rosterView = createTwoPageRoster(),
                    triggerSpy = spyOn(rosterView.options.trackingModel, 'trigger');

                // verifies the initial state
                expectLinkStates(rosterView, 'Page 1', ['First', 'Previous']);

                // navigate to page 2
                clickPagingControl('Next');
                expectRequestedPage(2);
                getLastRequest().respond(200, {}, JSON.stringify(getResponseBody(2, 2)));
                expectLinkStates(rosterView, 'Page 2', ['Next', 'Last']);
                expect(triggerSpy).toHaveBeenCalledWith('segment:track', 'edx.bi.roster.paged', {
                    category: 2
                });
            });

            it('can jump to a particular page', function() {
                var rosterView = createTwoPageRoster();
                clickPagingControl('Page 2');
                expectRequestedPage(2);
                getLastRequest().respond(200, {}, JSON.stringify(getResponseBody(2, 2)));
                expectLinkStates(rosterView, 'Page 2', ['Next', 'Last']);
            });

            it('can navigate to the next/previous page', function() {
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

            it('does not enable pagination controls for unreachable pages', function() {
                var rosterView = createTwoPageRoster();
                // Verify no request, no view change
                clickPagingControl('Previous');
                expect(server.requests.length).toBe(0);
                expectLinkStates(rosterView, 'Page 1', ['First', 'Previous']);
            });

            it('handles gateway timeouts', function() {
                var rosterView = createTwoPageRoster();
                spyOn(rosterView, 'trigger');
                clickPagingControl('Next');
                verifyErrorHandling(rosterView, 504);
            });

            it('handles server errors', function() {
                var rosterView = createTwoPageRoster();
                spyOn(rosterView, 'trigger');
                clickPagingControl('Next');
                verifyErrorHandling(rosterView, 500);
            });

            it('handles network errors', function() {
                var rosterView = createTwoPageRoster();
                testTimeout(rosterView, function() {
                    clickPagingControl('Next');
                });
            });
        });

        describe('search', function() {
            var expectSearchedFor;

            expectSearchedFor = function(searchString) {
                expect(getLastRequestParams()).toEqual(jasmine.objectContaining({
                    text_search: searchString
                }));
            };

            it('renders the current search string', function() {
                var collection,
                    rosterView,
                    searchString;
                searchString = 'search string';
                collection = new LearnerCollection();
                collection.setSearchString(searchString);
                rosterView = getRosterView({collection: collection});
                expect(rosterView.$('#search-learners')).toHaveValue(searchString);
            });

            it('can search for arbitrary strings', function() {
                var searchString = 'search string';
                getRosterView();
                executeSearch(searchString);
                expect(getLastRequestParams()).toEqual(jasmine.objectContaining({
                    text_search: searchString
                }));
            });

            it('renders itself whenever the collection changes', function() {
                var rosterView = getRosterView({courseMetadataModel: this.courseMetadata}),
                    searchString = 'search string';
                executeSearch(searchString);
                expect(getLastRequestParams()).toEqual(jasmine.objectContaining({
                    text_search: searchString
                }));
                expect(rosterView.$('#search-learners')).toHaveValue(searchString);
                rosterView.options.collection.unsetSearchString();
                rosterView.options.collection.refresh();
                getLastRequest().respond(200, {}, JSON.stringify(getResponseBody(0)));
                expect(rosterView.$('#search-learners')).toHaveValue('');
            });

            it('can clear the search with the clear link', function() {
                var searchString = 'search string';
                getRosterView();
                executeSearch(searchString);
                expectSearchedFor(searchString);
                getLastRequest().respond(200, {}, JSON.stringify(getResponseBody(1, 1)));
                $('.clear.btn').click();
                expect(getLastRequestParams().text_search).toBeUndefined();
            });

            it('can clear the search by searching the empty string', function() {
                var rosterView,
                    searchString;
                searchString = 'search string';
                rosterView = getRosterView();
                executeSearch(searchString);
                expectSearchedFor(searchString);
                getLastRequest().respond(200, {}, JSON.stringify(getResponseBody(1, 1)));
                executeSearch('');
                expect(rosterView.options.collection.getSearchString()).toBeNull();
                expect(getLastRequestParams().text_search).toBeUndefined();
                getLastRequest().respond(200, {}, JSON.stringify(getResponseBody(1, 1)));
            });

            it('triggers a tracking event', function() {
                var rosterView = getRosterView(),
                    searchString = 'search string',
                    triggerSpy = spyOn(rosterView.options.trackingModel, 'trigger');

                executeSearch(searchString);
                expectSearchedFor(searchString);
                expect(triggerSpy).toHaveBeenCalledWith('segment:track', 'edx.bi.roster.searched', {
                    category: 'search'
                });
            });

            it('handles server errors', function() {
                var rosterView = getRosterView();
                spyOn(rosterView, 'trigger');
                executeSearch('test search');
                verifyErrorHandling(rosterView, 504);
                executeSearch('test search');
                verifyErrorHandling(rosterView, 500);
            });

            it('handles network errors', function() {
                var rosterView = getRosterView();
                testTimeout(rosterView, function() {
                    executeSearch('test search');
                });
            });
        });

        describe('filtering', function() {
            var expectCanFilterBy = function(filterKey, filterValue) {
                var expectedRequestSubset;
                $('select').val(filterValue);
                $('select').change();
                if (filterValue) {
                    expectedRequestSubset = {};
                    expectedRequestSubset[filterKey] = filterValue;
                    expect(getLastRequestParams()).toEqual(jasmine.objectContaining(expectedRequestSubset));
                } else {
                    expect(getLastRequestParams().hasOwnProperty(filterKey)).toBe(false);
                }
                getLastRequest().respond(200, {}, JSON.stringify(getResponseBody(1, 1)));
                expect($('option[value="' + filterValue + '"]')).toBeSelected();
            };

            it('renders filters in alphabetical order', function() {
                var options,
                    rosterView;
                rosterView = getRosterView({courseMetadata: {
                    cohorts: {
                        zebra: 1,
                        antelope: 2
                    }
                }});
                options = rosterView.$('.learners-filter option');
                expect(options[1]).toHaveText('antelope (2)');
                expect(options[2]).toHaveText('zebra (1)');
            });

            SpecHelpers.withConfiguration({
                'by cohort': [
                    'cohort', // filter field name
                    'cohorts', // course metadata field name
                    {'Cohort A': 1, 'Cohort B': 2} // default cohort metadata
                ],
                'by enrollment track': [
                    'enrollment_mode', // filter field name
                    'enrollment_modes', // course metadata field name
                    {verified: 1, audit: 2} // default enrollment modes
                ]
            }, function(filterFieldName, courseMetadataFieldName, filterOptions) {
                var courseMetadataAttributes = {};
                courseMetadataAttributes[courseMetadataFieldName] = filterOptions;
                this.courseMetadata = new CourseMetadataModel(courseMetadataAttributes);
                this.filterFieldName = filterFieldName;
                this.filterOptions = filterOptions;
                this.firstFilterOption = _.keys(this.filterOptions)[0];
            }, function() {
                it('renders the filter which is currently applied', function() {
                    var collection,
                        firstFilterOption,
                        rosterView;
                    firstFilterOption = this.firstFilterOption;
                    collection = new LearnerCollection();
                    collection.setFilterField(this.filterFieldName, firstFilterOption);
                    rosterView = getRosterView({
                        courseMetadataModel: this.courseMetadata,
                        collection: collection
                    });
                    expect(rosterView.$('.learners-filter option[value="' + firstFilterOption + '"]')).toBeSelected();
                });

                it('only renders when filter options are provided', function() {
                    var rosterView,
                        selectOptions,
                        defaultSelectOption;

                    // Doesn't render when no filter options are provided.
                    rosterView = getRosterView({courseMetadata: {}});
                    expect(rosterView.$('.learners-filter').children()).not.toExist();

                    // Does render when filter options are provided.
                    rosterView = getRosterView({courseMetadataModel: this.courseMetadata});
                    selectOptions = rosterView.$('.learners-filter option').get();
                    defaultSelectOption = selectOptions[0];

                    expect(defaultSelectOption).toBeSelected();
                    expect(defaultSelectOption).toHaveValue('');
                    expect(defaultSelectOption).toHaveText('All');

                    _.chain(this.filterOptions)
                        .pairs()
                        .sortBy(0) // we expect the filter options to appear in alphabetical order
                        .zip(_.rest(selectOptions))
                        .each(function(filterAndSelectOption) {
                            var filterOption = filterAndSelectOption[0],
                                filterOptionKey = filterOption[0],
                                learnerCount = filterOption[1],
                                selectOption = filterAndSelectOption[1];
                            expect(selectOption).not.toBeSelected();
                            expect(selectOption).toHaveValue(filterOptionKey);
                            expect(selectOption).toHaveText(filterOptionKey + ' (' + learnerCount + ')');
                        });
                });

                it('can execute a filter', function() {
                    getRosterView({courseMetadataModel: this.courseMetadata});
                    expectCanFilterBy(this.filterFieldName, this.firstFilterOption);
                    expectCanFilterBy(this.filterFieldName, '');
                });

                it('renders itself whenever the collection changes', function() {
                    var rosterView = getRosterView({courseMetadataModel: this.courseMetadata});
                    expectCanFilterBy(this.filterFieldName, this.firstFilterOption);
                    rosterView.collection.unsetAllFilterFields();
                    rosterView.collection.refresh();
                    getLastRequest().respond(200, {}, JSON.stringify(getResponseBody(0)));
                    expect(rosterView.$('select option:selected')).toHaveValue('');
                });

                it('triggers a tracking event', function() {
                    var rosterView = getRosterView({courseMetadataModel: this.courseMetadata}),
                        filterFieldName = this.filterFieldName,
                        triggerSpy = spyOn(rosterView.options.trackingModel, 'trigger');

                    expectCanFilterBy(filterFieldName, this.firstFilterOption);
                    expect(triggerSpy).toHaveBeenCalledWith('segment:track', 'edx.bi.roster.filtered', {
                        category: filterFieldName
                    });
                });

                it('sets focus to the top after filtering', function() {
                    var filterFieldName = this.filterFieldName;
                    getRosterView({courseMetadataModel: this.courseMetadata});
                    spyOn($.fn, 'focus');
                    expectCanFilterBy(filterFieldName, this.firstFilterOption);
                    expect($('#learner-app-focusable').focus).toHaveBeenCalled();
                });

                it('handles server errors', function() {
                    var rosterView = getRosterView({courseMetadataModel: this.courseMetadata});
                    spyOn(rosterView, 'trigger');
                    rosterView.$('select').val(this.firstFilterOption);
                    rosterView.$('select').change();
                    verifyErrorHandling(rosterView, 500);
                });

                it('handles network errors', function() {
                    var rosterView = getRosterView({courseMetadataModel: this.courseMetadata});
                    testTimeout(rosterView, function() {
                        rosterView.$('select').val(this.firstFilterOption);
                        rosterView.$('select').change();
                    }.bind(this));
                });
            });
        });

        describe('activity date range', function() {
            it('renders dates', function() {
                var rosterView = getRosterView({
                    courseMetadata: {
                        engagement_ranges: {
                            date_range: {
                                start: '2016-01-12',
                                end: '2016-03-30'
                            }
                        }
                    }
                });
                expect(rosterView.$('.activity-date-range'))
                    .toContainText('Activity between January 12, 2016 - March 30, 2016');
            });

            it('renders n/a when no date range available', function() {
                var rosterView = getRosterView();
                expect(rosterView.$('.activity-date-range'))
                    .toContainText('Activity between n/a - n/a');
            });
        });

        describe('active filters', function() {
            var expectActiveFilters,
                expectNoActiveFilters;

            expectNoActiveFilters = function(rosterView) {
                expect(rosterView.$('#active-filters-title')).not.toExist();
                expect(rosterView.$('.action-clear-all-filters')).not.toExist();
            };

            expectActiveFilters = function(rosterView, options) {
                var activeFiltersTitle = rosterView.$('#active-filters-title'),
                    clearAllButton = rosterView.$('.action-clear-all-filters'),
                    activeFilters = rosterView.$('.active-filters'),
                    activeSearch = activeFilters.find('.filter-text_search'),
                    activeCohort = activeFilters.find('.filter-cohort'),
                    activeEngagement = activeFilters.find('.filter-ignore_segments'),
                    activeEnrollmentTrack = activeFilters.find('.filter-enrollment_mode'),
                    removeFilterText = 'Click to remove this filter';

                expect(activeFiltersTitle).toExist();
                expect(activeFilters.find('.filter').length).toEqual(_.keys(options).length);
                expect(clearAllButton).toExist();

                if (options.search) {
                    expect(activeSearch).toContainText('"' + options.search + '"');
                    expect(activeSearch.find('.sr-only')).toContainText(removeFilterText);
                } else {
                    expect(activeSearch).not.toExist();
                }

                if (options.cohort) {
                    expect(activeCohort).toContainText('Cohort: ' + options.cohort);
                    expect(activeCohort.find('.sr-only')).toContainText(removeFilterText);
                } else {
                    expect(activeCohort).not.toExist();
                }

                if (options.enrollmentTrack) {
                    expect(activeEnrollmentTrack).toContainText('Enrollment Track: ' + options.enrollmentTrack);
                    expect(activeEnrollmentTrack.find('.sr-only')).toContainText(removeFilterText);
                } else {
                    expect(activeEnrollmentTrack).not.toExist();
                }

                if (options.engagement) {
                    expect(activeEngagement).toContainText('Active Learners');
                    expect(activeEngagement.find('.sr-only')).toContainText(removeFilterText);
                } else {
                    expect(activeEngagement).not.toExist();
                }
            };

            it('does not render when there are no active filters', function() {
                expectNoActiveFilters(getRosterView());
            });

            it('renders a search filter', function() {
                var rosterView = getRosterView();
                rosterView.options.collection.setSearchString('hello, world');
                rosterView.options.collection.refresh();
                getLastRequest().respond(200, {}, JSON.stringify(getResponseBody(0)));
                expectActiveFilters(rosterView, {search: 'hello, world'});
            });

            it('renders a cohort filter', function() {
                var rosterView = getRosterView();
                rosterView.options.collection.setFilterField('cohort', 'labrador');
                rosterView.options.collection.refresh();
                getLastRequest().respond(200, {}, JSON.stringify(getResponseBody(0)));
                expectActiveFilters(rosterView, {cohort: 'Labrador'});
            });

            it('renders an enrollment track filter', function() {
                var rosterView = getRosterView();
                rosterView.options.collection.setFilterField('enrollment_mode', 'honor');
                rosterView.options.collection.refresh();
                getLastRequest().respond(200, {}, JSON.stringify(getResponseBody(0)));
                expectActiveFilters(rosterView, {enrollmentTrack: 'Honor'});
            });

            it('renders an engagement filter', function() {
                var rosterView = getRosterView();
                rosterView.options.collection.setFilterField('ignore_segments', 'inactive');
                rosterView.options.collection.refresh();
                getLastRequest().respond(200, {}, JSON.stringify(getResponseBody(0)));
                expectActiveFilters(rosterView, {engagement: 'inactive'});
            });

            it('renders multiple filters', function() {
                var rosterView = getRosterView();
                rosterView.options.collection.setSearchString('foo');
                rosterView.options.collection.setFilterField('cohort', 'labrador');
                rosterView.options.collection.setFilterField('enrollment_mode', 'honor');
                rosterView.options.collection.refresh();
                getLastRequest().respond(200, {}, JSON.stringify(getResponseBody(0)));
                expectActiveFilters(rosterView, {
                    search: 'foo',
                    cohort: 'Labrador',
                    enrollmentTrack: 'Honor'
                });
            });

            it('can clear a search', function() {
                var rosterView = getRosterView();
                rosterView.options.collection.setFilterField('cohort', 'labrador');
                rosterView.options.collection.setSearchString('foo');
                rosterView.options.collection.refresh();
                getLastRequest().respond(200, {}, JSON.stringify(getResponseBody(0)));
                expectActiveFilters(rosterView, {
                    search: 'foo',
                    cohort: 'Labrador'
                });
                rosterView.$('.active-filters .filter-text_search .action-clear-filter').click();
                getLastRequest().respond(200, {}, JSON.stringify(getResponseBody(0)));
                expect(rosterView.options.collection.hasActiveSearch()).toBe(false);
                expectActiveFilters(rosterView, {cohort: 'Labrador'});
            });

            it('can clear a filter', function() {
                var rosterView = getRosterView();
                rosterView.options.collection.setFilterField('cohort', 'labrador');
                rosterView.options.collection.setSearchString('foo');
                rosterView.options.collection.refresh();
                getLastRequest().respond(200, {}, JSON.stringify(getResponseBody(0)));
                expectActiveFilters(rosterView, {
                    search: 'foo',
                    cohort: 'Labrador'
                });
                rosterView.$('.active-filters .filter-cohort .action-clear-filter').click();
                getLastRequest().respond(200, {}, JSON.stringify(getResponseBody(0)));
                expectActiveFilters(rosterView, {search: 'foo'});
                expect(rosterView.collection.getFilterFieldValue('cohort')).not.toBe('labrador');
            });

            it('can clear all the filters', function() {
                var rosterView = getRosterView();
                rosterView.options.collection.setSearchString('foo');
                rosterView.options.collection.setFilterField('cohort', 'labrador');
                rosterView.options.collection.setFilterField('enrollment_mode', 'honor');
                rosterView.options.collection.refresh();
                getLastRequest().respond(200, {}, JSON.stringify(getResponseBody(0)));
                expectActiveFilters(rosterView, {
                    search: 'foo',
                    cohort: 'Labrador',
                    enrollmentTrack: 'Honor'
                });
                rosterView.$('.action-clear-all-filters').click();
                getLastRequest().respond(200, {}, JSON.stringify(getResponseBody(0)));
                expectNoActiveFilters(rosterView);
            });

            it('handles server errors', function() {
                var rosterView = getRosterView({courseMetadataModel: this.courseMetadata});
                spyOn(rosterView, 'trigger');
                rosterView.options.collection.setFilterField('cohort', 'labrador');
                rosterView.options.collection.refresh();
                getLastRequest().respond(200, {}, JSON.stringify(getResponseBody(0)));
                rosterView.$('.active-filters .filter-cohort .action-clear-filter').click();
                verifyErrorHandling(rosterView, 500);
            });

            it('handles network errors', function() {
                var rosterView = getRosterView({courseMetadataModel: this.courseMetadata});
                rosterView.options.collection.setFilterField('cohort', 'labrador');
                rosterView.options.collection.refresh();
                getLastRequest().respond(200, {}, JSON.stringify(getResponseBody(0)));
                testTimeout(rosterView, function() {
                    rosterView.$('.active-filters .filter-cohort .action-clear-filter').click();
                });
            });
        });

        describe('no results', function() {
            it('renders a "no results" view when there is no learner data in the initial collection', function() {
                var rosterView = getRosterView();
                expect(rosterView.$('.alert-information'))
                    .toContainText('No learner data is currently available for your course.');
            });

            it('renders a "no results" view when there are no learners for the current search', function() {
                var rosterView = getRosterView({
                    collectionResponse: getResponseBody(1, 1),
                    collectionOptions: {parse: true}
                });
                executeSearch('Dan');
                getLastRequest().respond(200, {}, JSON.stringify(getResponseBody(0)));
                expect(rosterView.$('.alert-information')).toContainText('No learners matched your criteria.');
                expect(rosterView.$('.alert-information')).toContainText('Try a different search.');
                expect(rosterView.$('.alert-information')).not.toContainText('Try clearing the filters.');
            });

            it('renders a "no results" view when there are no learners for the current filter', function() {
                var rosterView = getRosterView({
                    collectionResponse: getResponseBody(1, 1),
                    collectionOptions: {parse: true},
                    courseMetadata: {cohorts: {'Cohort A': 10}}
                });
                $('select').val('Cohort A');
                $('select').change();
                getLastRequest().respond(200, {}, JSON.stringify(getResponseBody(0)));
                expect(rosterView.$('.alert-information')).toContainText('No learners matched your criteria.');
                expect(rosterView.$('.alert-information')).toContainText('Try clearing the filters.');
                expect(rosterView.$('.alert-information')).not.toContainText('Try a different search.');
            });

            it('renders a "no results" view when there are no learners for the current search and filter', function() {
                var rosterView = getRosterView({
                    collectionResponse: getResponseBody(1, 1),
                    collectionOptions: {parse: true},
                    courseMetadata: {cohorts: {'Cohort A': 10}}
                });
                executeSearch('Dan');
                getLastRequest().respond(200, {}, JSON.stringify(getResponseBody(1, 1)));
                $('select').val('Cohort A');
                $('select').change();
                getLastRequest().respond(200, {}, JSON.stringify(getResponseBody(0)));
                expect(rosterView.$('.alert-information')).toContainText('No learners matched your criteria.');
                expect(rosterView.$('.alert-information')).toContainText('Try clearing the filters.');
                expect(rosterView.$('.alert-information')).toContainText('Try a different search.');
            });
        });

        describe('accessibility', function() {
            it('the table has a <caption> element', function() {
                var rosterView = getRosterView({
                    collectionResponse: getResponseBody(1, 1),
                    collectionOptions: {parse: true}
                });
                expect(rosterView.$('table > caption')).toBeInDOM();
            });

            it('all <th> elements have scope attributes', function() {
                var rosterView = getRosterView({
                    collectionResponse: getResponseBody(1, 1),
                    collectionOptions: {parse: true}
                });
                rosterView.$('th').each(function(_index, $th) {
                    expect($th).toHaveAttr('scope', 'col');
                });
            });

            it('all <th> elements have screen reader text', function() {
                var rosterView = getRosterView({
                        collectionResponse: getResponseBody(1, 1),
                        collectionOptions: {parse: true}
                    }),
                    screenReaderTextSelector = '.sr-sorting-text',
                    sortColumnSelector = '.username.sortable';
                rosterView.$('th').each(function(_index, th) {
                    expect($(th).find(screenReaderTextSelector)).toHaveText('click to sort');
                });
                rosterView.$(sortColumnSelector + ' > a').click();
                expect(rosterView.$(sortColumnSelector).find(screenReaderTextSelector)).toHaveText('sort ascending');
                rosterView.$(sortColumnSelector + ' > a').click();
                expect(rosterView.$(sortColumnSelector).find(screenReaderTextSelector)).toHaveText('sort descending');
            });

            it('the search input has a label', function() {
                var rosterView = getRosterView(),
                    searchContainer = rosterView.$('.learners-search-container'),
                    inputId = searchContainer.find('input').attr('id'),
                    $label = searchContainer.find('label');
                expect($label).toHaveAttr('for', inputId);
                expect($label).toHaveText('Search learners');
            });

            it('all icons should be aria-hidden', function() {
                var rosterView = getRosterView({
                    collectionResponse: getResponseBody(1, 1),
                    collectionOptions: {parse: true}
                });
                rosterView.$('i').each(function(_index, el) {
                    expect($(el)).toHaveAttr('aria-hidden', 'true');
                });
            });

            it('sets focus to the top of the table after taking a paging action', function() {
                var rosterView = getRosterView({
                        collectionResponse: getResponseBody(2, 1),
                        collectionOptions: {parse: true}
                    }),
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

            it('sets focus to the top after searching', function() {
                var searchString = 'search string';
                getRosterView();
                spyOn($.fn, 'focus');
                executeSearch(searchString);
                expect($('#learner-app-focusable').focus).toHaveBeenCalled();
            });

            it('does not violate the axe-core ruleset', function(done) {
                getRosterView({
                    collectionResponse: getResponseBody(1, 1),
                    collectionOptions: {parse: true}
                });
                axe.a11yCheck($('.roster-view-fixture')[0], function(result) {
                    expect(result.violations.length).toBe(0);
                    done();
                });
            });
        });
    });
});
