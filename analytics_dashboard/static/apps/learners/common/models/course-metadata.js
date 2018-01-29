define(function(require) {
    'use strict';

    var _ = require('underscore'),
        Backbone = require('backbone'),

        ListUtils = require('components/utils/utils'),

        CourseMetadataModel;

    CourseMetadataModel = Backbone.Model.extend({
        defaults: function() {
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

        /**
         * Returns the filters values and options for the filter UI.
         */
        getFilterOptions: function(filter) {
            if (this.has(filter)) {
                return _(this.get(filter)).map(function(count, key) {
                    return {
                        name: key,
                        displayName: key,
                        count: count
                    };
                });
            } else {
                return undefined;
            }
        },

        renameEngagementRanges: function(engagementRanges) {
            var rankedEngagementRanges = {},
                metrics = ['discussion_contributions', 'problem_attempts_per_completed',
                    'problems_attempted', 'problems_completed', 'videos_viewed'],
                renamedFields = {
                    class_rank_top: 'classRankTop',
                    class_rank_average: 'classRankMiddle',
                    class_rank_bottom: 'classRankBottom'
                };

            _(engagementRanges).each(function(ranges, metric) {
                if (_(metrics).contains(metric)) {
                    rankedEngagementRanges[metric] = {};
                    _(ranges).each(function(range, classRankType) {
                        rankedEngagementRanges[metric][renamedFields[classRankType]] = range;
                    });
                }
            });
            this.set('rankedEngagementRanges', rankedEngagementRanges);
        },

        initialize: function(attributes, options) {
            Backbone.Model.prototype.initialize.call(this, attributes, options);
            this.options = options || {};
            this.renameEngagementRanges(this.get('engagement_ranges'));
        },

        url: function() {
            return this.options.url;
        },

        fetch: function(options) {
            return Backbone.Model.prototype.fetch.call(this, options)
                .fail(ListUtils.handleAjaxFailure.bind(this));
        },

        parse: function(response) {
            var parsedEngagementRanges = _.mapObject(response.engagement_ranges, function(metricRanges, key) {
                // do not parse the date_range field (it's not a metric range)
                if (key === 'date_range') {
                    return metricRanges;
                } else {
                    return _.mapObject(metricRanges, function(range) {
                        // range is either null or a two-element array
                        if (_.isNull(range)) {
                            return null;
                        }
                        return [
                            // A null element is interpreted as infinity
                            // Note: Something like [null, 0] is invalid. The API should not return that.
                            _.isNull(range[0]) ? Infinity : range[0],
                            _.isNull(range[1]) ? Infinity : range[1]
                        ];
                    });
                }
            });

            return _.extend(response, {engagement_ranges: parsedEngagementRanges});
        },

        /**
         * Returns which category ('class_rank_average', 'class_rank_top', 'class_rank_bottom'),
         * the engagement values falls into.  Returns undefined if the range
         * isn't available.
         *
         * @param engagementMetric Key for engagement range. E.g. problems_attempted.
         * @param value Engagement value.
         */
        getEngagementCategory: function(engagementMetric, value) {
            var ranges = this.get('rankedEngagementRanges')[engagementMetric],
                engagementCategory;

            _.each(ranges, function(range, category) {
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
         *   - When the range has the same value on both sides, that value is
         *     considered in-range, but only that value.
         *
         * @param value Value in question.
         * @param range Array of min and max.  May be null.
         */
        inMetricRange: function(value, range) {
            if (_.isNull(range)) {
                return false;
            } else if ((value === Infinity && range[1] === Infinity) ||
                       (value === range[0] && range[0] === range[1])) {
                return true;
            }
            return value >= range[0] && value < range[1];
        }
    });

    return CourseMetadataModel;
});
