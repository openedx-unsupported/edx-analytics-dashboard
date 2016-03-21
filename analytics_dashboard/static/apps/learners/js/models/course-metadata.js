define([
    'backbone',
    'learners/js/utils',
    'underscore'
], function (Backbone, LearnerUtils, _) {
    'use strict';

    var CourseMetadataModel = Backbone.Model.extend({
        defaults:{
            cohorts: {},
            segments: {},
            enrollment_modes: {},
            engagement_ranges: {
                date_range: {},
                problems_attempted: {},
                problems_completed: {},
                problem_attempts_per_completed: {},
                discussion_contributions: {}
            }
        },

        initialize: function (attributes, options) {
            this.options = options || {};
        },

        url: function () {
            return this.options.url;
        },

        fetch: function (options) {
            return Backbone.Model.prototype.fetch.call(this, options)
                .fail(LearnerUtils.handleAjaxFailure.bind(this));
        },

        /**
         * Returns which category ('average', 'above_average', 'below_average'),
         * the engagement values falls into.  Returns undefined the range isn't
         * available.
         *
         * @param engagementKey Key for engagement range. E.g. problems_attempted.
         * @param value Engagement value.
         */
        getEngagementCategory: function(engagementKey, value) {
            var categories = ['average', 'above_average', 'below_average'],
                ranges = this.get('engagement_ranges')[engagementKey],
                engagementCategory;

            if (ranges) {
                _(categories).each(function (category) {
                    if (_(ranges).has(category)) {
                        try {
                            if (LearnerUtils.inRange(value, ranges[category])) {
                                engagementCategory = category;
                            }
                        } catch (Error) {
                            // min and max are null -- do nothing
                        }
                    }
                });
            }

            return engagementCategory;
        }
    });

    return CourseMetadataModel;
});
