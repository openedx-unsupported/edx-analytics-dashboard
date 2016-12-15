/**
 * A wrapper view for controls.
 */
define(function(require) {
    'use strict';

    var _ = require('underscore'),
        ListControlsView = require('generic-list/list/views/controls'),

        // CourseListFilter = require('course-list/list/views/filter'),
        CourseListSearch = require('course-list/list/views/search'),
        listControlsTemplate = require('text!course-list/list/templates/controls.underscore'),

        CourseListControlsView;

    CourseListControlsView = ListControlsView.extend({
        template: _.template(listControlsTemplate),

        regions: {
            search: '.course-list-search-container',
            availabilityFilter: '.course-list-availability-filter-container'
        },

        initialize: function(options) {
            this.options = options || {};

            this.childViews = [
                {
                    region: 'search',
                    class: CourseListSearch,
                    options: {
                        collection: this.options.collection,
                        name: 'text_search',
                        placeholder: gettext('Find a course'),
                        trackingModel: this.options.trackingModel
                    }
                }
                // TODO: add availability filter once we have real filter values
                // {
                    // region: 'availibilityFilter',
                    // class: CourseListFilter,
                    // options: {
                        // collection: this.options.collection,
                        // filterKey: 'availability',
                        // filterValues: {Current: 0, Archived: 0},
                        // selectDisplayName: gettext('Current Courses'),
                        // trackingModel: this.options.trackingModel
                    // }
                // }
            ];
        }
    });

    return CourseListControlsView;
});
