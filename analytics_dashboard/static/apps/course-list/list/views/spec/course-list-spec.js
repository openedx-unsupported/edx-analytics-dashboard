define(function(require) {
    'use strict';

    var $ = require('jquery'),
        _ = require('underscore'),
        axe = require('axe-core'),
        moment = require('moment'),
        SpecHelpers = require('uitk/utils/spec-helpers/spec-helpers'),

        Utils = require('utils/utils'),

        CourseList = require('course-list/common/collections/course-list'),
        CourseListView = require('course-list/list/views/course-list'),
        CourseModel = require('course-list/common/models/course'),
        TrackingModel = require('models/tracking-model');


    describe('CourseListView', function() {
        var fixtureClass = 'course-list-view-fixture',
            clickPagingControl,
            getCourseListView;

        getCourseListView = function(options, pageSize) {
            var collection,
                view,
                defaultOptions = _.defaults({}, options);
            collection = defaultOptions.collection || new CourseList([
                // default course data
                new CourseModel({
                    catalog_course_title: 'Alpaca',
                    course_id: 'this/course/id',
                    count: 10,
                    cumulative_count: 20,
                    count_change_7_days: 30,
                    verified_enrollment: 40,
                    start_date: '2015-02-17T050000',
                    end_date: '2015-03-31T000000'
                }),
                new CourseModel({
                    catalog_course_title: 'zebra',
                    course_id: 'another-course-id',
                    count: 0,
                    cumulative_count: 1000,
                    count_change_7_days: -10,
                    verified_enrollment: 1000,
                    start_date: '2016-11-17T050000',
                    end_date: '2016-12-01T000000'
                })],
                _.extend({mode: 'client'}, defaultOptions.collectionOptions)
            );

            if (pageSize) {
                collection.setPageSize(pageSize);
            }
            view = new CourseListView({
                collection: collection,
                el: '.' + fixtureClass,
                trackSubject: 'course_list',
                hasData: true,
                trackingModel: new TrackingModel(),
                tableName: 'Course List',
                appClass: 'course-list'
            }).render();
            view.onBeforeShow();
            return view;
        };

        clickPagingControl = function(titleSelector) {
            $('a[title="' + titleSelector + '"]').click();
        };

        beforeEach(function() {
            setFixtures('<div class="' + fixtureClass + '"></div>');
        });

        it('renders a list of courses with number and date formatted', function() {
            var view = getCourseListView();

            moment.locale(Utils.getMomentLocale());

            _.chain(_.zip(view.collection.models, view.$('tbody tr'))).each(function(courseAndTr) {
                var course = courseAndTr[0],
                    tr = courseAndTr[1];
                expect($(tr).find('td.course-name-cell .course-name')).toContainText(
                    course.get('catalog_course_title'));
                expect($(tr).find('td.course-name-cell .course-id')).toContainText(course.get('course_id'));
                expect($(tr).find('td.start_date')).toContainText(
                    moment.utc(course.get('start_date').split('T')[0]).format('L'));
                expect($(tr).find('td.end_date')).toContainText(
                    moment.utc(course.get('end_date').split('T')[0]).format('L'));
                expect($(tr).find('td.cumulative_count')).toContainText(
                    Utils.localizeNumber(course.get('cumulative_count')));
                expect($(tr).find('td.count')).toContainText(Utils.localizeNumber(course.get('count')));
                expect($(tr).find('td.count_change_7_days')).toContainText(
                    Utils.localizeNumber(course.get('count_change_7_days')));
                expect($(tr).find('td.verified_enrollment')).toContainText(
                    Utils.localizeNumber(course.get('verified_enrollment')));
            });
        });

        describe('sorting', function() {
            var clickSortingHeader,
                executeSortTest,
                expectSortCalled,
                getSortingHeaderLink;

            getSortingHeaderLink = function(headerClass) {
                return $('th.' + headerClass + ' a');
            };

            clickSortingHeader = function(headerClass) {
                getSortingHeaderLink(headerClass).click();
            };

            executeSortTest = function(field, isInitial) {
                expect(getSortingHeaderLink(field).find('span.fa')).toHaveClass(isInitial ? 'fa-sort-asc' : 'fa-sort');
                clickSortingHeader(field);
                expectSortCalled(field, isInitial ? 'desc' : 'asc');
                clickSortingHeader(field);
                expectSortCalled(field, isInitial ? 'asc' : 'desc');
            };

            expectSortCalled = function(sortField, sortValue) {
                expect(getSortingHeaderLink(sortField).find('span')).toHaveClass('fa-sort-' + sortValue);
            };

            beforeEach(function() {
                this.view = getCourseListView();
            });

            SpecHelpers.withConfiguration({
                catalog_course_title: ['catalog_course_title', true],
                start_date: ['start_date'],
                end_date: ['end_date'],
                cumulative_count: ['cumulative_count'],
                count: ['count'],
                count_change_7_days: ['count_change_7_days'],
                verified_enrollment: ['verified_enrollment']
            }, function(sortField, isInitial) {
                this.sortField = sortField;
                this.isInitial = isInitial;
            }, function() {
                it('by headers', function() {
                    executeSortTest(this.sortField, this.isInitial);
                });
            });

            it('goes to the first page after applying a sort', function() {
                this.view = getCourseListView({}, 1);
                clickPagingControl('Page 2');
                expect(this.view.$('a[title="Page 2"]').parent('li')).toHaveClass('active');
                clickSortingHeader('catalog_course_title');
                expect(this.view.$('a[title="Page 1"]').parent('li')).toHaveClass('active');
            });

            SpecHelpers.withConfiguration({
                catalog_course_title: ['catalog_course_title', true],
                start_date: ['start_date'],
                end_date: ['end_date'],
                cumulative_count: ['cumulative_count'],
                count: ['count'],
                count_change_7_days: ['count_change_7_days'],
                verified_enrollment: ['verified_enrollment']
            }, function(column, isInitial) {
                this.column = column;
                this.isInitial = isInitial;
            }, function() {
                it('triggers a tracking event', function() {
                    var directions = ['_asc', '_desc'],
                        triggerSpy = spyOn(this.view.options.trackingModel, 'trigger'),
                        column = this.column;
                    if (this.isInitial) {
                        directions.reverse();
                    }
                    executeSortTest(column, this.isInitial);
                    _.each(directions, function(direction) {
                        expect(triggerSpy).toHaveBeenCalledWith('segment:track', 'edx.bi.course_list.sorted', {
                            category: column + direction
                        });
                    });
                });
            });
        });

        describe('paging', function() {
            var createTwoPageView,
                expectLinkStates;

            createTwoPageView = function() {
                var view = getCourseListView({}, 1);
                return view;
            };

            expectLinkStates = function(view, activeLinkTitle, disabledLinkTitles) {
                view.$('li > a').each(function(_index, link) {
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

            it('triggers a tracking event', function() {
                var view = createTwoPageView(),
                    triggerSpy = spyOn(view.options.trackingModel, 'trigger');
                // navigate to page 2
                clickPagingControl('Next');
                expect(triggerSpy).toHaveBeenCalledWith('segment:track', 'edx.bi.course_list.paged', {
                    category: 2
                });
            });

            it('can jump to a particular page', function() {
                var view = createTwoPageView();
                clickPagingControl('Page 2');
                expectLinkStates(view, 'Page 2', ['Next', 'Last']);
            });

            it('can navigate to the next/previous page', function() {
                var view = createTwoPageView();

                clickPagingControl('Next');
                expectLinkStates(view, 'Page 2', ['Next', 'Last']);

                clickPagingControl('Previous');
                expectLinkStates(view, 'Page 1', ['First', 'Previous']);
            });

            it('does not enable pagination controls for unreachable pages', function() {
                var view = createTwoPageView();
                // Verify no request, no view change
                clickPagingControl('Previous');
                expectLinkStates(view, 'Page 1', ['First', 'Previous']);
            });
        });

        describe('no results', function() {
            it('renders a "no results" view when there is no course data in the initial collection', function() {
                var view = getCourseListView({
                    collection: new CourseList([])
                });
                expect(view.$('.alert-information'))
                    .toContainText('No course data is currently available for your course.');
            });
        });

        describe('accessibility', function() {
            it('the table has a <caption> element', function() {
                var view = getCourseListView();
                expect(view.$('table > caption')).toBeInDOM();
            });

            it('all <th> elements have scope attributes', function() {
                var view = getCourseListView();
                view.$('th').each(function(_index, $th) {
                    expect($th).toHaveAttr('scope', 'col');
                });
            });

            it('all icons should be aria-hidden', function() {
                var view = getCourseListView();
                view.$('i').each(function(_index, el) {
                    expect($(el)).toHaveAttr('aria-hidden', 'true');
                });
            });

            it('sets focus to the top of the table after taking a paging action', function() {
                var view = getCourseListView({}, 1),
                    firstPageLink = view.$('.backgrid-paginator li a[title="Page 1"]'),
                    secondPageLink = view.$('.backgrid-paginator li a[title="Page 2"]');
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
                expect($('#course-list-app-focusable').focus).toHaveBeenCalled();
            });

            it('does not violate the axe-core ruleset', function(done) {
                getCourseListView();
                axe.a11yCheck($('.course-list-view-fixture')[0], function(result) {
                    expect(result.violations.length).toBe(0);
                    done();
                });
            });
        });
    });
});
