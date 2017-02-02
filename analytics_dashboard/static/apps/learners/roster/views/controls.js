/**
 * A wrapper view for controls.
 */
define(function(require) {
    'use strict';

    var _ = require('underscore'),
        ParentView = require('components/generic-list/common/views/parent-view'),

        CheckboxFilter = require('components/filter/views/checkbox-filter'),
        DropDownFilter = require('components/filter/views/drop-down-filter'),
        LearnerSearch = require('learners/roster/views/search'),
        rosterControlsTemplate = require('text!learners/roster/templates/controls.underscore'),

        RosterControlsView;

    RosterControlsView = ParentView.extend({
        template: _.template(rosterControlsTemplate),

        regions: {
            search: '.learners-search-container',
            cohortFilter: '.learners-cohort-filter-container',
            enrollmentTrackFilter: '.learners-enrollment-track-filter-container',
            activeFilter: '.learners-active-filter-container'
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

            this.childViews = [
                {
                    region: 'search',
                    class: LearnerSearch,
                    options: {
                        collection: this.options.collection,
                        name: 'text_search',
                        placeholder: gettext('Find a learner'),
                        trackingModel: this.options.trackingModel
                    }
                },
                {
                    region: 'cohortFilter',
                    class: DropDownFilter,
                    options: _({
                        filterKey: 'cohort',
                        filterValues: this.options.courseMetadata.get('cohorts'),
                        selectDisplayName: gettext('Cohort Groups'),
                    }).extend(defaultFilterOptions)
                },
                {
                    region: 'enrollmentTrackFilter',
                    class: DropDownFilter,
                    options: _({
                        filterKey: 'enrollment_mode',
                        filterValues: this.options.courseMetadata.get('enrollment_modes'),
                        selectDisplayName: gettext('Enrollment Tracks')
                    }).extend(defaultFilterOptions)
                },
                {
                    region: 'activeFilter',
                    class: CheckboxFilter,
                    options: _({
                        filterKey: 'ignore_segments',
                        filterValues: this.options.courseMetadata.get('segments'),
                        // Translators: inactive meaning that these learners have not interacted with the course
                        // recently.
                        selectDisplayName: gettext('Hide Inactive Learners'),
                    }).extend(defaultFilterOptions)
                }
            ];
        }
    });

    return RosterControlsView;
});
