define(['backbone'], function (Backbone) {
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
         * Returns whether the trend data is available with the assumption that
         * data isn't sparse (there are values for fields across all rows).
         *
         * @param attribute Attribute name to reference the trend dataset.
         * @param dataType Field in question.
         */
        hasTrend: function(attribute, dataType) {
            var self = this,
                trendData = self.get(attribute),
                hasTrend = false;

            if (_(trendData).size()) {
                hasTrend = _(trendData[0]).has(dataType);
            }

            return hasTrend;
        }

    });

    return CourseModel;
});
