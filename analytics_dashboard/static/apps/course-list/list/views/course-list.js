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
        ActiveFiltersView = require('course-list/list/views/active-filters'),
        CourseListControlsView = require('course-list/list/views/controls'),
        CourseListResultsView = require('course-list/list/views/results'),
        ListView = require('components/generic-list/list/views/list'),

        listTemplate = require('text!course-list/list/templates/list.underscore'),

        CourseListView;

    CourseListView = ListView.extend({
        className: 'course-list',

        template: _.template(listTemplate),

        regions: {
            results: '.course-list-results'
        },

        initialize: function(options) {
            ListView.prototype.initialize.call(this, options);

            this.childViews = [
                {
                    region: 'activeFilters',
                    class: ActiveFiltersView,
                    options: {
                        collection: this.options.collection
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
        }
    });

    return CourseListView;
});
