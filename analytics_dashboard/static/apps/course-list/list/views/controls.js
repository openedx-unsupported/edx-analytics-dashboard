/**
 * A wrapper view for controls.
 */
define(function(require) {
    'use strict';

    var _ = require('underscore'),
        ParentView = require('components/generic-list/common/views/parent-view'),

        CourseListSearch = require('course-list/list/views/search'),
        courseListControlsTemplate = require('text!course-list/list/templates/controls.underscore'),

        CourseListControlsView;

    CourseListControlsView = ParentView.extend({
        template: _.template(courseListControlsTemplate),

        regions: {
            search: '.course-list-search-container'
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
            ];
        }
    });

    return CourseListControlsView;
});
