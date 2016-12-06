/**
 * A wrapper view for controls.
 */
define(function(require) {
    'use strict';

    var _ = require('underscore'),
        Marionette = require('marionette'),

        Filter = require('course-list/list/views/filter'),
        CourseListSearch = require('course-list/list/views/search'),
        listControlsTemplate = require('text!course-list/list/templates/controls.underscore'),

        ListControlsView;

    ListControlsView = Marionette.LayoutView.extend({
        template: _.template(listControlsTemplate),

        regions: {
            search: '.course-list-search-container',
            availabilityFilter: '.course-list-availability-filter-container'
        },

        initialize: function(options) {
            this.options = options || {};
        },

        onBeforeShow: function() {
            this.showChildView('search', new CourseListSearch({
                collection: this.options.collection,
                name: 'text_search',
                placeholder: gettext('Find a course'),
                trackingModel: this.options.trackingModel
            }));
            // this.showChildView('availabilityFilter', new Filter({
                // collection: this.options.collection,
                // filterKey: 'availability',
                // filterValues: {Current: 0, Archived: 0}, // TODO: actually get this data
                // selectDisplayName: gettext('Current Courses'),
                // trackingModel: this.options.trackingModel
            // }));
        }
    });

    return ListControlsView;
});
