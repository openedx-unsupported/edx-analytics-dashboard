define(function (require) {
    'use strict';

    var _ = require('underscore'),
        Backbone = require('backbone'),

        LearnerUtils = require('learners/common/utils'),

        LearnerModel;

    LearnerModel = Backbone.Model.extend({
        defaults: {
            name: '',
            username: '',
            email: '',
            account_url: '',
            enrollment_mode: '',
            enrollment_date: null,
            cohort: null,
            segments: [],
            engagements: {},
            last_updated: null,
            course_id: ''
        },

        idAttribute: 'username',

        url: function () {
            return Backbone.Model.prototype.url.call(this) + '?course_id=' + encodeURIComponent(this.get('course_id'));
        },

        fetch: function (options) {
            return Backbone.Model.prototype.fetch.call(this, options)
                .fail(LearnerUtils.handleAjaxFailure.bind(this));
        },

        /**
         * Converts the ISO 8601 date strings to JavaScript Date
         * objects.
         */
        parse: function (response) {
            var parsedResponse = response;
            parsedResponse.enrollment_date = response.enrollment_date ? new Date(response.enrollment_date) : null;
            parsedResponse.last_updated = response.last_updated ? new Date(response.last_updated) : null;
            return parsedResponse;
        },

        /**
         * Returns true if the username has been set.  False otherwise.
         */
        hasData: function () {
            return !_(this.get('username')).isEmpty();
        }
    });

    return LearnerModel;
});
