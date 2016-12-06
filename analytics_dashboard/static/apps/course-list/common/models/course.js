define(function(require) {
    'use strict';

    var _ = require('underscore'),
        Backbone = require('backbone'),

        CourseListUtils = require('course-list/common/utils'),

        CourseModel;

    CourseModel = Backbone.Model.extend({
        defaults: function() {
            return {
                created: '',
                course_id: '',
                catalog_course_title: '',
                catalog_course: '',
                start_date: '',
                end_date: '',
                pacing_type: '',
                availability: '',
                count: 0,
                cumulative_count: 0,
                count_change_7_days: 0,
                modes: {
                    audit: {
                        count: 0,
                        cumulative_count: 0,
                        count_change_7_days: 0
                    },
                    credit: {
                        count: 0,
                        cumulative_count: 0,
                        count_change_7_days: 0
                    },
                    verified: {
                        count: 0,
                        cumulative_count: 0,
                        count_change_7_days: 0
                    },
                    honor: {
                        count: 0,
                        cumulative_count: 0,
                        count_change_7_days: 0
                    },
                    professional: {
                        count: 0,
                        cumulative_count: 0,
                        count_change_7_days: 0
                    }
                }
            };
        },

        idAttribute: 'course_id',

        url: function() {
            return Backbone.Model.prototype.url.call(this) + '?course_ids=' + encodeURIComponent(this.get('course_id'));
        },

        fetch: function(options) {
            return Backbone.Model.prototype.fetch.call(this, options)
                .fail(CourseListUtils.handleAjaxFailure.bind(this));
        },

        /**
         * Returns true if the course_id has been set.  False otherwise.
         */
        hasData: function() {
            return !_(this.get('course_id')).isEmpty();
        }
    });

    return CourseModel;
});
