define(['backbone', 'jquery'], function(Backbone, $) {
    'use strict';

    var CourseModel = Backbone.Model.extend({

        /**
         * This doesn't do much currently.  I want to test out getting
         * this model working with requireJS, gulp, and jasmine.
         *
         * @returns {*}
         */
        isEmpty: function() {
            var self = this;
            return !self.has('courseId');
        },

        /**
         * Get the enrollment trends with dates as UTC as an array of
         * arrays.
         *
         * @returns {*}
         */
        getEnrollmentSeries: function() {
            var self = this,
                enrollmentData = self.get('enrollmentTrends'),
                series;

            series = _.map(enrollmentData, function(enrollment){
                return [self.convertDate(enrollment.date), enrollment.count];
            });

            return series;
        },

        /**
         * Convert the yyyy-mm-dd date to UTC.
         *
         * @param dates
         * @returns {Array}
         */
        convertDate: function(date) {
            var self = this,
                tokens;

            tokens = date.split('-');
            // JS months start at 0
            return Date.UTC(tokens[0], tokens[1]-1, tokens[2]);
        }
    });

    return CourseModel;
});
