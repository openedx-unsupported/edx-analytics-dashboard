define([
    'backbone',
    'learners/js/utils'
], function (Backbone, LearnerUtils) {
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
                discussions_contributed: {}
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
        }
    });

    return CourseMetadataModel;
});
