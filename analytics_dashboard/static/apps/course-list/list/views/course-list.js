/**
 * Renders a sortable, filterable, and searchable paginated table of
 * courses for the Course List app.
 *
 * Requires the following values in the options hash:
 * - options.collection - an instance of CourseListCollection
 */
define(function(require) {
    'use strict';

    var _ = require('underscore'),
        Marionette = require('marionette'),

        // ActiveFiltersView = require('course-list/list/views/active-filters'),
        DownloadDataView = require('generic-list/common/views/download-data'),
        CourseListResultsView = require('course-list/list/views/results'),
        ListUtils = require('course-list/common/utils'),
        // ListControlsView = require('course-list/list/views/controls'),
        listTemplate = require('text!course-list/list/templates/list.underscore'),

        CourseListView;

    // Load modules without exports
    require('backgrid-filter');
    require('bootstrap');
    require('bootstrap_accessibility');  // adds the aria-describedby to tooltips

    /**
     * Wraps up the search view, table view, and pagination footer
     * view.
     */
    CourseListView = Marionette.LayoutView.extend({
        className: 'course-list',

        template: _.template(listTemplate),

        regions: {
            // activeFilters: '.course-list-active-filters',
            activityDateRange: '.activity-date-range',
            downloadData: '.course-list-download-data',
            // controls: '.course-list-table-controls',
            results: '.course-list-results'
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
        },

        onBeforeShow: function() {
            // this.showChildView('activeFilters', new ActiveFiltersView({
                // collection: this.options.collection
            // }));
            this.showChildView('downloadData', new DownloadDataView({
                collection: this.options.collection,
                trackingModel: this.options.trackingModel,
                trackCategory: 'course_list'
            }));
            // this.showChildView('controls', new ListControlsView({
                // collection: this.options.collection,
                // courseMetadata: this.options.courseMetadata,
                // trackingModel: this.options.trackingModel
            // }));
            this.showChildView('results', new CourseListResultsView({
                collection: this.options.collection,
                courseMetadata: this.options.courseMetadata,
                hasData: this.options.hasData,
                trackingModel: this.options.trackingModel
            }));
        },

        templateHelpers: function() {
            return {
                controlsLabel: gettext('Course list controls')
            };
        }
    });

    return CourseListView;
});
