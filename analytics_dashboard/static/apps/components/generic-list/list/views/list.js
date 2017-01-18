/**
 * Renders a sortable, filterable, and searchable paginated table of
 * learners for the Learner Analytics app.
 */
define(function(require) {
    'use strict';

    var ParentView = require('components/generic-list/common/views/parent-view'),
        ListUtils = require('components/utils/utils'),

        ListView;

    // Load modules without exports
    require('backgrid-filter');
    require('bootstrap');
    require('bootstrap_accessibility');  // adds the aria-describedby to tooltips

    /**
     * Wraps up the search view, table view, and pagination footer
     * view.
     */
    ListView = ParentView.extend({
        className: 'generic-list',

        initialize: function(options) {
            var eventTransformers;

            this.options = options || {};

            eventTransformers = {
                serverError: ListUtils.EventTransformers.serverErrorToAppError,
                networkError: ListUtils.EventTransformers.networkErrorToAppError,
                sync: ListUtils.EventTransformers.syncToClearError
            };
            ListUtils.mapEvents(this.options.collection, eventTransformers, this);
            ListUtils.mapEvents(this.options.courseMetadata, eventTransformers, this);
        },

        templateHelpers: function() {
            return {
                controlsLabel: this.controlsLabel
            };
        }
    });

    return ListView;
});
