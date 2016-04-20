/**
 * A wrapper view for controls.
 */
define(function (require) {
    'use strict';

    var _ = require('underscore'),
        Marionette = require('marionette'),

        Filter = require('learners/roster/views/filter'),
        LearnerSearch = require('learners/roster/views/search'),
        rosterControlsTemplate = require('text!learners/roster/templates/roster-controls.underscore'),

        RosterControlsView;

    RosterControlsView = Marionette.LayoutView.extend({
        template: _.template(rosterControlsTemplate),

        regions: {
            search: '.learners-search-container',
            cohortFilter: '.learners-cohort-filter-container'
        },

        initialize: function (options) {
            this.options = options || {};
        },

        onBeforeShow: function () {
            this.showChildView('search', new LearnerSearch({
                collection: this.options.collection,
                name: 'text_search',
                placeholder: gettext('Find a learner')
            }));
            this.showChildView('cohortFilter', new Filter({
                collection: this.options.collection,
                filterKey: 'cohort',
                filterValues: this.options.courseMetadata.get('cohorts'),
                selectDisplayName: gettext('Cohort Groups')
            }));
        }
    });

    return RosterControlsView;
});
