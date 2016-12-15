/**
 * A wrapper view for controls.
 */
define(function(require) {
    'use strict';

    var _ = require('underscore'),
        ListControlsView = require('generic-list/list/views/controls'),

        LearnerFilter = require('learners/roster/views/filter'),
        LearnerSearch = require('learners/roster/views/search'),
        rosterControlsTemplate = require('text!learners/roster/templates/controls.underscore'),

        RosterControlsView;

    RosterControlsView = ListControlsView.extend({
        template: _.template(rosterControlsTemplate),

        regions: {
            search: '.learners-search-container',
            cohortFilter: '.learners-cohort-filter-container',
            enrollmentTrackFilter: '.learners-enrollment-track-filter-container',
            activeFilter: '.learners-active-filter-container'
        },

        initialize: function(options) {
            this.options = options || {};

            this.childViews = [
                {
                    region: 'search',
                    class: LearnerSearch,
                    options: {
                        collection: this.options.collection,
                        name: 'text_search',
                        placeholder: gettext('Find a learner'),
                        trackingModel: this.options.trackingModel
                    }
                },
                {
                    region: 'cohortFilter',
                    class: LearnerFilter,
                    options: {
                        collection: this.options.collection,
                        filterKey: 'cohort',
                        filterValues: this.options.courseMetadata.get('cohorts'),
                        selectDisplayName: gettext('Cohort Groups'),
                        trackingModel: this.options.trackingModel
                    }
                },
                {
                    region: 'enrollmentTrackFilter',
                    class: LearnerFilter,
                    options: {
                        collection: this.options.collection,
                        filterKey: 'enrollment_mode',
                        filterValues: this.options.courseMetadata.get('enrollment_modes'),
                        selectDisplayName: gettext('Enrollment Tracks'),
                        trackingModel: this.options.trackingModel
                    }
                },
                {
                    region: 'activeFilter',
                    class: LearnerFilter,
                    options: {
                        collection: this.options.collection,
                        filterKey: 'ignore_segments',
                        filterValues: this.options.courseMetadata.get('segments'),
                        selectDisplayName: gettext('Inactive Learners'),
                        trackingModel: this.options.trackingModel
                    }
                }
            ];
        }
    });

    return RosterControlsView;
});
