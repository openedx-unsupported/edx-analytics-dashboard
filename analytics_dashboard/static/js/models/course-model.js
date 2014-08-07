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
         * Retrieve course enrollment data grouped by country
         */
        fetchEnrollmentByCountry: function() {
            var self = this,
                countryDataUrl = ['/courses', this.get('courseId'), 'json/enrollment_by_country/'].join('/');

            $.getJSON(countryDataUrl, function (data) {
                self.set({
                    enrollmentByCountryUpdateDate: data.date,
                    enrollmentByCountry: data.data
                });
            });
        }
    });

    return CourseModel;
});
