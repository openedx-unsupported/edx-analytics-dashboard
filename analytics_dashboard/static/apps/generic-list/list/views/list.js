/**
 * Renders a sortable, filterable, and searchable paginated table of
 * learners for the Learner Analytics app.
 */
define(function(require) {
    'use strict';

    var _ = require('underscore'),
        Marionette = require('marionette'),

        ListUtils = require('components/utils/utils'),
        listTemplate = require('text!generic-list/list/templates/list.underscore'),

        ListView;

    // Load modules without exports
    require('backgrid-filter');
    require('bootstrap');
    require('bootstrap_accessibility');  // adds the aria-describedby to tooltips

    /**
     * Wraps up the search view, table view, and pagination footer
     * view.
     */
    ListView = Marionette.LayoutView.extend({
        className: 'generic-list',

        template: _.template(listTemplate),

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

        onBeforeShow: function() {
            _.each(this.childViews, _.bind(function(child) {
                this.showChildView(child.region, new child.class(child.options));
            }, this));
        },

        templateHelpers: function() {
            return {
                controlsLabel: this.controlsLabel
            };
        }
    });

    return ListView;
});
