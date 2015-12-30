define([
    'components/pagination/collections/paging_collection',
    'models/learner-model'
], function (PagingCollection, LearnerModel) {
    'use strict';

    var LearnerCollection = PagingCollection.extend({
        model: LearnerModel,

        initialize: function (models, options) {
            PagingCollection.prototype.initialize.call(this, options);

            this.url = options.url;
            this.courseId = options.courseId;

            this.registerSortableField('username', gettext('Username'));
            this.registerSortableField('problems_attempted', gettext('Problems Attempted'));
            this.registerSortableField('problems_completed', gettext('Problems Completed'));
            this.registerSortableField('videos_viewed', gettext('Videos Viewed'));
            this.registerSortableField('problems_attempted_per_completed', gettext('Problems Attempted per Completed'));
            this.registerSortableField('discussion_contributions', gettext('Discussion Contributions'));

            this.registerFilterableField('segments', gettext('Segments'));
            this.registerFilterableField('ignore_segments', gettext('Segments to Ignore'));
            this.registerFilterableField('cohort', gettext('Cohort'));
            this.registerFilterableField('enrollment_mode', gettext('Enrollment Mode'));
        },

        fetch: function (options) {
            // Handle gateway timeouts
            return PagingCollection.prototype.fetch.call(this, options).fail(function (jqXHR) {
                // Note that we're currently only handling gateway
                // timeouts here, but we can eventually check against
                // other expected errors and trigger events
                // accordingly.
                if (jqXHR.status === 504) {
                    this.trigger('gatewayTimeout');
                }
            }.bind(this));
        },

        state: {
            pageSize: 25
        },

        queryParams: {
            course_id: function () { return this.courseId; }
        }
    });

    return LearnerCollection;
});
