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
        ActiveFiltersView = require('components/generic-list/list/views/active-filters'),
        CourseListControlsView = require('course-list/list/views/controls'),
        CourseListResultsView = require('course-list/list/views/results'),
        ListView = require('components/generic-list/list/views/list'),

        listTemplate = require('text!course-list/list/templates/list.underscore'),

        CourseListView;

    CourseListView = ListView.extend({
        className: 'course-list',

        template: _.template(listTemplate),

        regions: {
            activeFilters: '.course-list-active-filters',
            controls: '.course-list-table-controls',
            results: '.course-list-results'
        },

        events: {
            clearFilter: 'clearFilter',
            clearAllFilters: 'clearAllFilters'
        },

        initialize: function(options) {
            ListView.prototype.initialize.call(this, options);

            this.childViews = [
                {
                    region: 'activeFilters',
                    class: ActiveFiltersView,
                    options: {
                        collection: this.options.collection,
                        mode: 'client'
                    }
                },
                {
                    region: 'controls',
                    class: CourseListControlsView,
                    options: {
                        collection: this.options.collection,
                        trackingModel: this.options.trackingModel
                    }
                },
                {
                    region: 'results',
                    class: CourseListResultsView,
                    options: {
                        collection: this.options.collection,
                        hasData: this.options.hasData,
                        tableName: this.options.tableName,
                        trackingModel: this.options.trackingModel,
                        trackSubject: this.options.trackSubject,
                        appClass: this.options.appClass
                    }
                }
            ];

            this.controlsLabel = gettext('Course list controls');
        },

        // These two functions glue the search state stored in the search view to the activeFilters view which needs to
        // mutate the search state in order to clear the search. This hack is what is necessary when state is stored way
        // down at the bottom of the view hierarchy.
        clearFilter: function(event, filter) {
            if (filter === 'text_search') {
                this.getRegion('controls').currentView
                        .getRegion('search').currentView
                        .clear(event);
            }
        },

        clearAllFilters: function(event, filters) {
            if ('text_search' in filters) {
                this.getRegion('controls').currentView
                        .getRegion('search').currentView
                        .clear(event);
            }
        }
    });

    return CourseListView;
});
