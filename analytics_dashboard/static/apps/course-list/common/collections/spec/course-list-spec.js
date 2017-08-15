define(function(require) {
    'use strict';

    var URI = require('URI'),

        SpecHelpers = require('uitk/utils/spec-helpers/spec-helpers'),

        CourseModel = require('course-list/common/models/course'),
        ProgramModel = require('course-list/common/models/program'),
        CourseList = require('course-list/common/collections/course-list'),
        ProgramsCollection = require('course-list/common/collections/programs');


    describe('CourseList', function() {
        var courseList,
            getUriForLastRequest,
            lastRequest,
            server,
            url;

        lastRequest = function() {
            return server.requests[server.requests.length - 1];
        };

        getUriForLastRequest = function() {
            return new URI(lastRequest().url);
        };

        afterEach(function() {
            server.restore();
        });

        beforeEach(function() {
            var programsCollection = new ProgramsCollection([
                new ProgramModel({
                    program_id: '123',
                    program_title: 'Alpaca Program',
                    program_type: 'Camelid',
                    course_ids: ['Alpaca']
                }),
                new ProgramModel({
                    program_id: '456',
                    program_title: 'Zebra Program',
                    program_type: 'Horse',
                    course_ids: ['zebra']
                }),
                new ProgramModel({
                    program_id: '789',
                    program_title: 'Courseless Program',
                    program_type: 'Courseless',
                    course_ids: []
                })]
            );
            var courses = [
                new CourseModel({
                    catalog_course_title: 'Alpaca',
                    course_id: 'Alpaca',
                    count: 10,
                    cumulative_count: 20,
                    count_change_7_days: 30,
                    verified_enrollment: 40,
                    availability: 'Current',
                    pacing_type: 'self_paced'
                }),
                new CourseModel({
                    catalog_course_title: 'zebra',
                    course_id: 'zebra',
                    count: 0,
                    cumulative_count: 1000,
                    count_change_7_days: -10,
                    verified_enrollment: 1000,
                    availability: 'Upcoming',
                    pacing_tpye: 'instructor_paced'
                })
            ];
            courseList = new CourseList(courses, {
                programsCollection: programsCollection,
                url: 'test-url',
                parse: true
            });
            server = sinon.fakeServer.create();
        });

        describe('filtering updates URI', function() {
            afterEach(function() {
                // unfilter
                courseList.clearAllFilters();
            });

            it('with multiple filters', function() {
                courseList.setFilterField('availability', 'Current');
                courseList.setFilterField('pacing_type', 'self_paced');

                courseList.refresh();
                url = getUriForLastRequest(server);
                expect(url.path()).toEqual('test-url');
                expect(url.query(true)).toEqual({
                    page: '1',
                    page_size: '100',
                    availability: 'Current',
                    pacing_type: 'self_paced',
                    order_by: 'catalog_course_title'  // the default order
                });
            });
        });

        describe('registered sort field', function() {
            SpecHelpers.withConfiguration({
                catalog_course_title: [
                    'catalog_course_title', // field name
                    'Course Name'  // expected display name
                ],
                start_date: [
                    'start_date', // field name
                    'Start Date'  // expected display name
                ],
                end_date: [
                    'end_date', // field name
                    'End Date'  // expected display name
                ],
                cumulative_count: [
                    'cumulative_count', // field name
                    'Total Enrollment'  // expected display name
                ],
                count: [
                    'count', // field name
                    'Current Enrollment'  // expected display name
                ],
                count_change_7_days: [
                    'count_change_7_days', // field name
                    'Change Last Week'  // expected display name
                ],
                verified_enrollment: [
                    'verified_enrollment', // field name
                    'Verified Enrollment'  // expected display name
                ]
            }, function(sortField, expectedResults) {
                this.sortField = sortField;
                this.expectedResults = expectedResults;
            }, function() {
                it('displays name', function() {
                    courseList.setSorting(this.sortField);
                    expect(courseList.sortDisplayName()).toEqual(this.expectedResults);
                });
            });
        });
    });
});
