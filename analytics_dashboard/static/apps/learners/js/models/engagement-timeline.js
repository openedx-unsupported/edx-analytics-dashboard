define([
    'backbone',
    'learners/js/utils'
], function (
    Backbone,
    LearnerUtils
) {
    'use strict';

    var EngagementTimelineModel = Backbone.Model.extend({
        /* Days is an array of objects, with each object containing the
         * following keys:
         *      - date (string) ISO 8601 date
         *      - discussions_contributed (int) number of discussions
         *        contributed to on the specified date.
         *      - problems_attempted (int) number of problems
         *        attempted on the specified date.
         *      - problems_completed (int) number of problems
         *        completed on the specified date.
         *      - videos_viewed (int) number of videos
         *        viewed on the specified date.
         */
        defaults: {
            days: []
        },

        initialize: function (attributes, options) {
            Backbone.Model.prototype.initialize.call(this, attributes, options);
            this.options = options || {};
        },

        url: function () {
            return this.options.url + '?course_id=' + encodeURIComponent(this.options.courseId);
        },

        fetch: function () {
            return Backbone.Model.prototype.fetch.apply(this, arguments)
                .fail(LearnerUtils.handleAjaxFailure.bind(this));
        }
    });

    return EngagementTimelineModel;
});
