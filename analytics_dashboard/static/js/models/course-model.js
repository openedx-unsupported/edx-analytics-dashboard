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
        }

    });

    return CourseModel;
});
