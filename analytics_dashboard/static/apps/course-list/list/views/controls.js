/**
 * A wrapper view for controls.
 */
define(function(require) {
    'use strict';

    var _ = require('underscore'),
        ParentView = require('components/generic-list/common/views/parent-view'),

        CheckboxFilter = require('components/filter/views/checkbox-filter'),
        CourseListSearch = require('components/search/views/search'),
        courseListControlsTemplate = require('course-list/list/templates/controls.underscore'),

        CourseListControlsView;

    require('components/skip-link/behaviors/skip-link-behavior');

    CourseListControlsView = ParentView.extend({
        template: _.template(courseListControlsTemplate),

        regions: {
            search: '.course-list-search-container',
            skipLink: '.skip-link',
            availabilityFilter: '.course-list-availability-filter-container',
            pacingTypeFilter: '.course-list-pacing-type-filter-container',
            programsFilter: '.course-list-programs-filter-container'
        },

        ui: {
            skipLink: '.skip-link'
        },

        behaviors: {
            SkipLinkBehavior: {}
        },

        templateHelpers: {
            skipToResults: gettext('Skip to results')
        },

        initialize: function(options) {
            var defaultFilterOptions;
            this.options = options || {};

            defaultFilterOptions = {
                collection: this.options.collection,
                trackingModel: this.options.trackingModel,
                trackSubject: this.options.trackSubject,
                appClass: this.options.appClass
            };

            this.childViews = [{
                region: 'search',
                class: CourseListSearch,
                options: _({
                    name: 'text_search',
                    focusableSelector: '#course-list-focusable',
                    searchLabelText: gettext('Search courses'),
                    placeholder: gettext('Find a course')
                }).defaults(defaultFilterOptions)
            }];

            if (this.options.filteringEnabled) {
                this.childViews = this.childViews.concat([{
                    region: 'availabilityFilter',
                    class: CheckboxFilter,
                    options: _({
                        filterKey: 'availability',
                        filterValues: this.options.collection.getFilterValues('availability'),
                        sectionDisplayName: this.options.collection.filterDisplayName('availability')
                    }).defaults(defaultFilterOptions)
                }, {
                    region: 'pacingTypeFilter',
                    class: CheckboxFilter,
                    options: _({
                        filterKey: 'pacing_type',
                        filterValues: this.options.collection.getFilterValues('pacing_type'),
                        sectionDisplayName: this.options.collection.filterDisplayName('pacing_type')
                    }).defaults(defaultFilterOptions)
                }, {
                    region: 'programsFilter',
                    class: CheckboxFilter,
                    options: _({
                        filterKey: 'program_ids',
                        filterValues: this.options.collection.getFilterValues('program_ids'),
                        sectionDisplayName: this.options.collection.filterDisplayName('program_ids')
                    }).defaults(defaultFilterOptions)
                }]);
            }
        }
    });

    return CourseListControlsView;
});
