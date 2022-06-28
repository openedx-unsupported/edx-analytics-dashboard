define((require) => {
  'use strict';

  const CourseModel = require('course-list/common/models/course');

  describe('CourseModel', () => {
    it('should have all the expected fields', () => {
      const course = new CourseModel();
      expect(course.attributes).toEqual({
        created: '',
        course_id: '',
        catalog_course_title: '',
        catalog_course: '',
        start_date: '',
        end_date: '',
        pacing_type: '',
        availability: 'unknown',
        count: 0,
        cumulative_count: 0,
        count_change_7_days: 0,
        verified_enrollment: 0,
        passing_users: 0,
        enrollment_modes: {
          audit: {
            count: 0,
            cumulative_count: 0,
            count_change_7_days: 0,
          },
          credit: {
            count: 0,
            cumulative_count: 0,
            count_change_7_days: 0,
          },
          verified: {
            count: 0,
            cumulative_count: 0,
            count_change_7_days: 0,
          },
          honor: {
            count: 0,
            cumulative_count: 0,
            count_change_7_days: 0,
          },
          professional: {
            count: 0,
            cumulative_count: 0,
            count_change_7_days: 0,
          },
        },
        program_ids: [],
      });
    });

    it('should populate verified_enrollment from the verified count', () => {
      const learner = new CourseModel({
        enrollment_modes: {
          verified: {
            count: 90210,
          },
        },
      });
      expect(learner.get('verified_enrollment')).toEqual(90210);
    });

    it('should use course_id to determine if data is available', () => {
      const course = new CourseModel();
      expect(course.hasData()).toBe(false);

      course.set('course_id', 'edx/demo/course');
      expect(course.hasData()).toBe(true);
    });
  });
});
