define(function(require) {
    'use strict';

    var SpecHelpers = require('uitk/utils/spec-helpers/spec-helpers'),

        CourseModel = require('course-list/common/models/course'),
        CourseList = require('course-list/common/collections/course-list');


    describe('CourseList', function() {
        var courseList;

        beforeEach(function() {
            var courses = [
                new CourseModel({
                    catalog_course_title: 'Alpaca',
                    course_id: 'Alpaca',
                    count: 10,
                    cumulative_count: 20,
                    count_change_7_days: 30,
                    verified_enrollment: 40,
                    availability: 'Current'
                }),
                new CourseModel({
                    catalog_course_title: 'zebra',
                    course_id: 'zebra',
                    count: 0,
                    cumulative_count: 1000,
                    count_change_7_days: -10,
                    verified_enrollment: 1000,
                    availability: 'Upcoming'
                })
            ];
            courseList = new CourseList(courses);
        });

        describe('filtering', function() {
            it('by availability', function() {
                expect(courseList.models.length).toBe(2);

                // filter results
                courseList.setFilterField('availability', 'Current');
                courseList.refresh();
                expect(courseList.models.length).toBe(1);
                expect(courseList.at(0).get('course_id')).toBe('Alpaca');

                // unfiltered
                courseList.clearAllFilters();
                expect(courseList.models.length).toBe(2);
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
