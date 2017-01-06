define(function(require) {
    'use strict';

    var CourseModel = require('course-list/common/models/course');

    describe('CourseModel', function() {
        it('should have all the expected fields', function() {
            var course = new CourseModel();
            expect(course.attributes).toEqual({
                created: '',
                course_id: '',
                catalog_course_title: '',
                catalog_course: '',
                start_date: '',
                end_date: '',
                pacing_type: '',
                availability: '',
                count: 0,
                cumulative_count: 0,
                count_change_7_days: 0,
                verified_enrollment: 0,
                enrollment_modes: {
                    audit: {
                        count: 0,
                        cumulative_count: 0,
                        count_change_7_days: 0
                    },
                    credit: {
                        count: 0,
                        cumulative_count: 0,
                        count_change_7_days: 0
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
                }
            });
        });

        it('should populate verified_enrollment from the verified count', function() {
            var learner = new CourseModel({
                enrollment_modes: {
                    verified: {
                        count: 90210
                    }
                }
            });
            expect(learner.get('verified_enrollment')).toEqual(90210);
        });

        it('should use course_id to determine if data is available', function() {
            var course = new CourseModel();
            expect(course.hasData()).toBe(false);

            course.set('course_id', 'edx/demo/course');
            expect(course.hasData()).toBe(true);
        });
    });
});
