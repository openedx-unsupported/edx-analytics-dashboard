define(function (require) {
    'use strict';

    var _ = require('underscore'),
        Backbone = require('backbone'),

        LearnerUtils = require('learners/common/utils'),

        CourseMetadataModel;

    CourseMetadataModel = Backbone.Model.extend({
        defaults: function () {
            return {
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
            };
        },

        initialize: function (attributes, options) {
            Backbone.Model.prototype.initialize.call(this, attributes, options);
            this.options = options || {};
        },

        url: function () {
            return this.options.url;
        },

        fetch: function (options) {
            return Backbone.Model.prototype.fetch.call(this, options)
                .fail(LearnerUtils.handleAjaxFailure.bind(this));
        },

        parse: function (response) {
            var parsedEngagementRanges = _.mapObject(response.engagement_ranges, function (metricRanges) {
                return _.mapObject(metricRanges, function (range) {
                    // range is either null or a two-element array
                    if (_.isNull(range)) {
                        return null;
                    }
                    return [
                        _.isNull(range[0]) ? -Infinity : range[0],
                        _.isNull(range[1]) ? Infinity : range[1]
                    ];
                });
            });
            return _.extend(response, { engagement_ranges: parsedEngagementRanges });
        },

        /**
         * Returns which category ('average', 'above_average', 'below_average'),
         * the engagement values falls into.  Returns undefined if the range
         * isn't available.
         *
         * @param engagementMetric Key for engagement range. E.g. problems_attempted.
         * @param value Engagement value.
         */
        getEngagementCategory: function(engagementMetric, value) {
            var ranges = this.get('engagement_ranges')[engagementMetric],
                engagementCategory;

            _.each(ranges, function (range, category) {
                if (this.inMetricRange(value, range)) {
                    engagementCategory = category;
                }
            }, this);

            return engagementCategory;
        },

        /**
         * Returns true if the value falls within the range (inclusive of min
         * and exclusive of max).
         *
         * There are some edge cases to note:
         *   - `null` ranges are considered unspecified, hence no value will be
         *     in-range.
         *   - When the range is infinite in the positive dimension, infinity is
         *     considered in-range.
         *
         * @param value Value in question.
         * @param range Array of min and max.  May be null.
         */
        inMetricRange: function(value, range) {
            return _.isNull(range) ? false :
                (value === Infinity && range[1] === Infinity) ? true :
                value >= range[0] && value < range[1];
        }
    });

    return CourseMetadataModel;
});
