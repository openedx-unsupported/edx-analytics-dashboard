/**
 * Renders a sortable, filterable, and searchable paginated table of
 * learners for the Learner Analytics app.
 *
 * Requires the following values in the options hash:
 * - options.collection - an instance of LearnerCollection
 */
define(function (require) {
    'use strict';

    var _ = require('underscore'),
        Marionette = require('marionette'),

        LearnerResultsView = require('learners/roster/views/results'),
        LearnerUtils = require('learners/common/utils'),
        RosterControlsView = require('learners/roster/views/controls'),
        rosterTemplate = require('text!learners/roster/templates/roster.underscore'),

        LearnerRosterView;

    // Load modules without exports
    require('backgrid-filter');
    require('bootstrap');
    require('bootstrap_accessibility');  // adds the aria-describedby to tooltips

    /**
     * Wraps up the search view, table view, and pagination footer
     * view.
     */
    LearnerRosterView = Marionette.LayoutView.extend({
        className: 'learner-roster',

        template: _.template(rosterTemplate),

        regions: {
            controls: '.learners-table-controls',
            results: '.learners-results'
        },

        initialize: function (options) {
            var eventTransformers;

            this.options = options || {};

            eventTransformers = {
                serverError: LearnerUtils.EventTransformers.serverErrorToAppError,
                networkError: LearnerUtils.EventTransformers.networkErrorToAppError,
                sync: LearnerUtils.EventTransformers.syncToClearError
            };
            LearnerUtils.mapEvents(this.options.collection, eventTransformers, this);
            LearnerUtils.mapEvents(this.options.courseMetadata, eventTransformers, this);
        },

        onBeforeShow: function () {
            this.showChildView('controls', new RosterControlsView({
                collection: this.options.collection,
                courseMetadata: this.options.courseMetadata
            }));
            this.showChildView('results', new LearnerResultsView({
                collection: this.options.collection,
                courseMetadata: this.options.courseMetadata
            }));
        }
    });

    return LearnerRosterView;
});
