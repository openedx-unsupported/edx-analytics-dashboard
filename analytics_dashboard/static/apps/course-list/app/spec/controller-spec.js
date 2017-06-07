define(function(require) {
    'use strict';

    var CourseListCollection = require('course-list/common/collections/course-list'),
        CourseListController = require('course-list/app/controller'),
        RootView = require('components/root/views/root'),
        PageModel = require('components/generic-list/common/models/page'),
        TrackingModel = require('models/tracking-model'),

        expectCourseListPage,
        fakeCourse;

    describe('CourseListController', function() {
        // convenience method for asserting that we are on the course list page
        expectCourseListPage = function(controller) {
            expect(controller.options.rootView.$('.course-list')).toBeInDOM();
            expect(controller.options.rootView.$('.course-list-header-region').html()).toContainText('Course List');
        };

        fakeCourse = function(id, name) {
            var count = parseInt(Math.random() * (150) + 50, 10);

            return {
                course_id: id,
                catalog_course_title: name,
                catalog_course: name,
                start_date: '2017-01-01',
                end_date: '2017-04-01',
                pacing_type: Math.random() > 0.5 ? 'instructor_paced' : 'self_paced',
                count: count,
                cumulative_count: parseInt(count + (count / 2), 10),
                passing_users: 0,
                enrollment_modes: {
                    audit: {
                        count: 0,
                        cumulative_count: 0,
                        count_change_7_days: 0
                    },
                    credit: {
                        count: count,
                        cumulative_count: parseInt(count + (count / 2), 10),
                        count_change_7_days: 5
                    },
                    verified: {
                        count: 0,
                        cumulative_count: 0,
                        count_change_7_days: 0
                    },
                    honor: {
                        count: 0,
                        cumulative_count: 0,
                        count_change_7_days: 0
                    },
                    professional: {
                        count: 0,
                        cumulative_count: 0,
                        count_change_7_days: 0
                    }
                },
                created: '',
                availability: 'unknown',
                count_change_7_days: 0,
                verified_enrollment: 0,
                program_ids: []
            };
        };

        beforeEach(function() {
            var pageModel = new PageModel();

            setFixtures('<div class="root-view"><div class="main"></div></div>');
            this.rootView = new RootView({
                el: '.root-view',
                pageModel: pageModel,
                appClass: 'course-list'
            });
            this.rootView.render();
            this.course = fakeCourse('course1', 'Course');
            this.collection = new CourseListCollection([this.course]);
            this.controller = new CourseListController({
                rootView: this.rootView,
                courseListCollection: this.collection,
                hasData: true,
                pageModel: pageModel,
                trackingModel: new TrackingModel()
            });
        });

        it('should show the course list page', function() {
            this.controller.showCourseListPage();
            expectCourseListPage(this.controller);
        });

        it('should show invalid parameters alert with invalid URL parameters', function() {
            this.controller.showCourseListPage('text_search=foo=');
            expect(this.controller.options.rootView.$('.course-list-alert-region').html()).toContainText(
                'Invalid Parameters'
            );
            expect(this.controller.options.rootView.$('.course-list-main-region').html()).toBe('');
        });

        it('should show the not found page', function() {
            this.controller.showNotFoundPage();
            // eslint-disable-next-line max-len
            expect(this.rootView.$el.html()).toContainText("Sorry, we couldn't find the page you're looking for.");
        });

        it('should sort the list with sort parameters', function() {
            var secondCourse = fakeCourse('course2', 'X Course');
            this.collection.add(secondCourse);
            this.controller.showCourseListPage('sortKey=catalog_course_title&order=desc');
            expect(this.collection.at(0).toJSON()).toEqual(secondCourse);
        });
    });
});
