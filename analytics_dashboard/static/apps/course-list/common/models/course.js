define(function(require) {
    'use strict';

    var _ = require('underscore'),
        Backbone = require('backbone'),

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
                verified_enrollment: 0,
                enrollment_modes: {
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


        /**
         * Backgrid will only work on models that are one level deep, so we must flatten the data structure to access
         * the verified enrollment count from the table.
         */
        initialize: function() {
            this.set({verified_enrollment: this.get('enrollment_modes').verified.count});
        },

        idAttribute: 'course_id',

        /**
         * Returns true if the course_id has been set.  False otherwise.
         */
        hasData: function() {
            return !_(this.get('course_id')).isEmpty();
        }
    });

    return CourseModel;
});
