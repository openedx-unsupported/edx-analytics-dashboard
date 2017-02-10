/**
 * Renders a sortable, filterable, and searchable paginated table of
 * learners for the Learner Analytics app.
 *
 * Requires the following values in the options hash:
 * - options.collection - an instance of LearnerCollection
 */
define(function(require) {
    'use strict';

    var _ = require('underscore'),

        ListView = require('components/generic-list/list/views/list'),
        ActiveDateRangeView = require('learners/roster/views/activity-date-range'),
        ActiveFiltersView = require('learners/roster/views/active-filters'),
        DownloadDataView = require('components/download/views/download-data'),
        LearnerResultsView = require('learners/roster/views/results'),
        RosterControlsView = require('learners/roster/views/controls'),
        NumResultsView = require('components/generic-list/list/views/num-results'),
        rosterTemplate = require('text!learners/roster/templates/roster.underscore'),

        LearnerRosterView;

    LearnerRosterView = ListView.extend({
        className: 'learner-roster',

        template: _.template(rosterTemplate),

        regions: {
            activeFilters: '.learners-active-filters',
            activityDateRange: '.activity-date-range',
            downloadData: '.learners-download-data',
            controls: '.learners-table-controls',
            results: '.learners-results',
            numResults: '.learners-num-results'
        },

        initialize: function(options) {
            ListView.prototype.initialize.call(this, options);

            this.childViews = [
                {
                    region: 'activeFilters',
                    class: ActiveFiltersView,
                    options: {
                        collection: this.options.collection,
                        showChildrenOnRender: true
                    }
                },
                {
                    region: 'activityDateRange',
                    class: ActiveDateRangeView,
                    options: {
                        model: this.options.courseMetadata
                    }
                },
                {
                    region: 'downloadData',
                    class: DownloadDataView,
                    options: {
                        collection: this.options.collection,
                        trackingModel: this.options.trackingModel,
                        trackCategory: 'learner_roster'
                    }
                },
                {
                    region: 'controls',
                    class: RosterControlsView,
                    options: {
                        collection: this.options.collection,
                        courseMetadata: this.options.courseMetadata,
                        trackingModel: this.options.trackingModel,
                        trackSubject: this.options.trackSubject,
                        appClass: this.options.appClass
                    }
                },
                {
                    region: 'results',
                    class: LearnerResultsView,
                    options: {
                        collection: this.options.collection,
                        courseMetadata: this.options.courseMetadata,
                        hasData: this.options.hasData,
                        trackingModel: this.options.trackingModel,
                        tableName: this.options.tableName,
                        trackSubject: this.options.trackSubject,
                        appClass: this.options.appClass
                    }
                },
                {
                    region: 'numResults',
                    class: NumResultsView,
                    options: {
                        collection: this.options.collection,
                        appClass: this.options.appClass
                    }
                }
            ];

            this.controlsLabel = gettext('Learner roster controls');
        }
    });

    return LearnerRosterView;
});
