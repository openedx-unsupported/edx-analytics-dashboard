/**
 * Collection of courses stored client-side.
 */
define(function(require) {
    'use strict';

    var _ = require('underscore'),
        ListCollection = require('components/generic-list/common/collections/collection'),
        ProgramsCollection = require('course-list/common/collections/programs'),
        CourseModel = require('course-list/common/models/course'),

        CourseListCollection;

    CourseListCollection = ListCollection.extend({

        model: CourseModel,

        initialize: function(models, options) {
            ListCollection.prototype.initialize.call(this, models, options);

            this.programsCollection = options.programsCollection || new ProgramsCollection([]);
            // add program_ids to programs array on every course
            this.programsCollection.each(_.bind(function(program) {
                // append this program's ID and display name to filterNameToDisplay
                // (so that the active filters will display the program title, not the ID)
                if (this.filterNameToDisplay === undefined) {
                    this.filterNameToDisplay = {program_ids: {}};
                } else if (this.filterNameToDisplay.program_ids === undefined) {
                    this.filterNameToDisplay.program_ids = {};
                }
                this.filterNameToDisplay.program_ids[program.get('program_id')] = program.get('program_title');
            }, this));

            this.registerSortableField('catalog_course_title', gettext('Course Name'));
            this.registerSortableField('start_date', gettext('Start Date'));
            this.registerSortableField('end_date', gettext('End Date'));
            this.registerSortableField('cumulative_count', gettext('Total Enrollment'));
            this.registerSortableField('count', gettext('Current Enrollment'));
            this.registerSortableField('count_change_7_days', gettext('Change Last Week'));
            this.registerSortableField('verified_enrollment', gettext('Verified Enrollment'));

            if (options.passingUsersEnabled) {
                this.registerSortableField('passing_users', gettext('Passing Learners'));
            }

            this.registerFilterableField('availability', gettext('Availability'));
            this.registerFilterableField('pacing_type', gettext('Pacing Type'));
            this.registerFilterableArrayField('program_ids', gettext('Programs'));
        },

        state: {
            pageSize: 100,
            sortKey: 'catalog_course_title',
            order: 0
        },

        /**
         * Given a filter type, returns the filters that can be applied and
         * display name.
         */
        getFilterValues: function(filterType) {
            var filters = {
                pacing_type: [{
                    name: 'instructor_paced',
                    displayName: this.getFilterValueDisplayName('pacing_type', 'instructor_paced')
                }, {
                    name: 'self_paced',
                    displayName: this.getFilterValueDisplayName('pacing_type', 'self_paced')
                }],
                availability: [{
                    name: 'Upcoming',
                    displayName: this.getFilterValueDisplayName('availability', 'Upcoming')
                }, {
                    name: 'Current',
                    displayName: this.getFilterValueDisplayName('availability', 'Current')
                }, {
                    name: 'Archived',
                    displayName: this.getFilterValueDisplayName('availability', 'Archived')
                }, {
                    name: 'unknown',
                    displayName: this.getFilterValueDisplayName('availability', 'unknown')
                }],
                program_ids: []
            };

            // Dynamically create list of program filters from programsCollection models
            this.programsCollection.each(function(program) {
                filters.program_ids.push({
                    name: program.get('program_id'),
                    displayName: program.get('program_title')
                });
            }, this);

            return filters[filterType];
        }
    });

    return CourseListCollection;
});
