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
        Marionette = require('marionette'),

        ActiveFiltersView = require('learners/roster/views/active-filters'),
        DownloadDataView = require('generic-list/common/views/download-data'),
        LearnerResultsView = require('learners/roster/views/results'),
        ListUtils = require('generic-list/common/utils'),
        RosterControlsView = require('learners/roster/views/controls'),
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

        regions: {
            activeFilters: '.active-filters',
            downloadData: '.download-data',
            controls: '.table-controls',
            results: '.results'
        },

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

            this.childViews = [
                {
                    region: 'activeFilters',
                    class: ActiveFiltersView,
                    options: {
                        collection: this.options.collection
                    }
                },
                {
                    region: 'downloadData',
                    class: DownloadDataView,
                    options: {
                        collection: this.options.collection,
                        trackingModel: this.options.trackingModel,
                        trackCategory: 'generic_list'
                    }
                },
                {
                    region: 'controls',
                    class: RosterControlsView,
                    options: {
                        collection: this.options.collection,
                        courseMetadata: this.options.courseMetadata,
                        trackingModel: this.options.trackingModel
                    }
                },
                {
                    region: 'results',
                    class: LearnerResultsView,
                    options: {
                        collection: this.options.collection,
                        courseMetadata: this.options.courseMetadata,
                        hasData: this.options.hasData,
                        trackingModel: this.options.trackingModel
                    }
                }
            ];

            this.controlsLabel = gettext('Learner roster controls');
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
