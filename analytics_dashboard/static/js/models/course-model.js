define(['underscore', 'backbone'], (_, Backbone) => {
  'use strict';

  const CourseModel = Backbone.Model.extend({

    /**
         * This doesn't do much currently.  I want to test out getting
         * this model working with requireJS, gulp, and jasmine.
         *
         * @returns {*}
         */
    isEmpty() {
      const self = this;
      return !self.has('courseId');
    },

    /**
         * Returns whether the trend data is available with the assumption that
         * data isn't sparse (there are values for fields across all rows).
         *
         * @param attribute Attribute name to reference the trend dataset.
         * @param dataType Field in question.
         */
    hasTrend(attribute, dataType) {
      const self = this;
      const trendData = self.get(attribute);
      let hasTrend = false;

      if (_(trendData).size()) {
        hasTrend = _(trendData[0]).has(dataType);
      }

      return hasTrend;
    },

  });

  return CourseModel;
});
