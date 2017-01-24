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
            this.registerSortableField('cumulative_count', gettext('Total Enrollment'));
            this.registerSortableField('count', gettext('Current Enrollment'));
            this.registerSortableField('count_change_7_days', gettext('Change Last Week'));
            this.registerSortableField('verified_enrollment', gettext('Verified Enrollment'));

            this.registerFilterableField('availability', gettext('Availability'));
            this.registerFilterableField('pacing_type', gettext('Pacing Type'));
        },

        state: {
            pageSize: 100,
            sortKey: 'catalog_course_title',
            order: 0
        }
    });

    return CourseListCollection;
});
