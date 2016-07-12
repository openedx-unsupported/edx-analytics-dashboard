/**
 * A wrapper view for controls.
 */
define(function(require) {
    'use strict';

    var _ = require('underscore'),
        Marionette = require('marionette'),

        Filter = require('learners/roster/views/filter'),
        LearnerSearch = require('learners/roster/views/search'),
        rosterControlsTemplate = require('text!learners/roster/templates/controls.underscore'),

        RosterControlsView;

    RosterControlsView = Marionette.LayoutView.extend({
        template: _.template(rosterControlsTemplate),

        regions: {
            search: '.learners-search-container',
            cohortFilter: '.learners-cohort-filter-container',
            enrollmentTrackFilter: '.learners-enrollment-track-filter-container'
        },

        initialize: function(options) {
            this.options = options || {};
        },

        onBeforeShow: function() {
            this.showChildView('search', new LearnerSearch({
                collection: this.options.collection,
                name: 'text_search',
                placeholder: gettext('Find a learner'),
                trackingModel: this.options.trackingModel
            }));
            this.showChildView('cohortFilter', new Filter({
                collection: this.options.collection,
                filterKey: 'cohort',
                filterValues: this.options.courseMetadata.get('cohorts'),
                selectDisplayName: gettext('Cohort Groups'),
                trackingModel: this.options.trackingModel
            }));
            this.showChildView('enrollmentTrackFilter', new Filter({
                collection: this.options.collection,
                filterKey: 'enrollment_mode',
                filterValues: this.options.courseMetadata.get('enrollment_modes'),
                selectDisplayName: gettext('Enrollment Tracks'),
                trackingModel: this.options.trackingModel
            }));
        }
    });

    return RosterControlsView;
});
