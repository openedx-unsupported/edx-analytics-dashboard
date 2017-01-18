define(function(require) {
    'use strict';

    var _ = require('underscore'),
        Backbone = require('backbone'),

        ListUtils = require('components/utils/utils'),

        LearnerModel;

    LearnerModel = Backbone.Model.extend({
        defaults: function() {
            return {
                name: '',
                username: '',
                email: '',
                account_url: '',
                enrollment_mode: '',
                enrollment_date: null,
                cohort: null,
                segments: [],
                /*
                 * The set of engagement metrics and their default values for all
                 * learners.  When metric keys map to `null` in the API response it
                 * means that the learner has an Infinite value for that metric.
                 * Infinite values are returned for ratio metrics (e.g.
                 * problem_attempts_per_completed) when the ratio is some positive
                 * number over zero.
                 */
                engagements: {
                    discussion_contributions: 0,
                    problems_attempted: 0,
                    problems_completed: 0,
                    videos_viewed: 0,
                    problem_attempts_per_completed: Infinity
                },
                last_updated: null,
                course_id: ''
            };
        },

        idAttribute: 'username',

        url: function() {
            return Backbone.Model.prototype.url.call(this) + '?course_id=' + encodeURIComponent(this.get('course_id'));
        },

        fetch: function(options) {
            return Backbone.Model.prototype.fetch.call(this, options)
                .fail(ListUtils.handleAjaxFailure.bind(this));
        },

        parse: function(response) {
            return _.extend({}, response, {
                enrollment_date: response.enrollment_date ? new Date(response.enrollment_date) : null,
                last_updated: response.last_updated ? new Date(response.last_updated) : null,
                engagements: _.extend(
                    {}, this.defaults().engagements, _.pick(response.engagements, function(metricValue) {
                        // metrics with null values should defer to defaults
                        return !_.isNull(metricValue) && !_.isUndefined(metricValue);
                    })
                )
            });
        },

        /**
         * Returns true if the username has been set.  False otherwise.
         */
        hasData: function() {
            return !_(this.get('username')).isEmpty();
        }
    });

    return LearnerModel;
});
