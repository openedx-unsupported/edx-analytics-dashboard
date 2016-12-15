define(function(require) {
    'use strict';

    var ListCollection = require('components/generic-list/common/collections/collection'),
        CourseModel = require('course-list/common/models/course'),

        CourseListCollection;

    CourseListCollection = ListCollection.extend({
        model: CourseModel,

        initialize: function(models, options) {
            ListCollection.prototype.initialize.call(this, models, options);

            this.registerSortableField('catalog_course_title', gettext('Course Name'));
            this.registerSortableField('start_date', gettext('Start Date'));
            this.registerSortableField('end_date', gettext('End Date'));
            this.registerSortableField('pacing_type', gettext('Pacing Type'));
            this.registerSortableField('count', gettext('Enrollment Count'));
            this.registerSortableField('cumulative_count', gettext('Cumulative Enrollment Count'));
            this.registerSortableField('count_change_7_days', gettext('Enrollment Change in Last 7 Days'));
            this.registerSortableField('verified_enrollment', gettext('Verified Enrollment'));

            this.registerFilterableField('availability', gettext('Availability'));
        },

        state: {
            pageSize: 25,
            sortKey: 'count',
            order: 1
        }
    });

    return CourseListCollection;
});
