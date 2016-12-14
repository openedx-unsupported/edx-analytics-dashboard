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
        ListView = require('generic-list/list/views/list'),

        // TODO: implement filter and sort controls
        // ActiveFiltersView = require('course-list/list/views/active-filters'),
        DownloadDataView = require('generic-list/common/views/download-data'),
        CourseListResultsView = require('course-list/list/views/results'),
        // ListControlsView = require('course-list/list/views/controls'),
        listTemplate = require('text!course-list/list/templates/list.underscore'),

        CourseListView;

    CourseListView = ListView.extend({
        className: 'course-list',

        template: _.template(listTemplate),

        regions: {
            // activeFilters: '.course-list-active-filters',
            downloadData: '.course-list-download-data',
            // controls: '.course-list-table-controls',
            results: '.course-list-results'
        },

        initialize: function(options) {
            ListView.prototype.initialize.call(this, options);

            this.childViews = [
                {
                    region: 'downloadData',
                    class: DownloadDataView,
                    options: {
                        collection: this.options.collection,
                        trackingModel: this.options.trackingModel,
                        trackCategory: 'course_list'
                    }
                },
                {
                    region: 'results',
                    class: CourseListResultsView,
                    options: {
                        collection: this.options.collection,
                        courseMetadata: this.options.courseMetadata,
                        hasData: this.options.hasData,
                        trackingModel: this.options.trackingModel
                    }
                }
            ];

            this.controlsLabel = gettext('Course list controls');
        }
    });

    return CourseListView;
});
