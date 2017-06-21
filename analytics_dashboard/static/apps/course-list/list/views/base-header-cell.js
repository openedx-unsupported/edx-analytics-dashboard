define(function(require) {
    'use strict';

    var BaseHeaderCell = require('components/generic-list/list/views/base-header-cell'),

        CourseListBaseHeaderCell;

    CourseListBaseHeaderCell = BaseHeaderCell.extend({
        container: '.course-list-table',
        tooltips: {
            catalog_course_title: gettext('Course name advertised on edX site.'),
            start_date: gettext('Start date advertised on edX site.'),
            end_date: gettext('End date set in edX Studio.'),
            cumulative_count: gettext('Learners who ever enrolled in the course.'),
            count: gettext('Learners currently enrolled in the course.'),
            count_change_7_days: gettext('Net difference in current enrollment in the last week.'),
            // eslint-disable-next-line max-len
            verified_enrollment: gettext('Number of currently enrolled learners pursuing a verified certificate of achievement.'),
            passing_users: gettext('Learners who have earned a passing grade.')
        }
    });

    return CourseListBaseHeaderCell;
});
