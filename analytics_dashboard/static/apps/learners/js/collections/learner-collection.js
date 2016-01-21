define([
    'components/pagination/collections/paging_collection',
    'learners/js/models/learner-model'
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
            this.registerSortableField('problem_attempts_per_completed', gettext('Problem Attempts per Completed'));
            this.registerSortableField('discussion_contributions', gettext('Discussion Contributions'));

            this.registerFilterableField('segments', gettext('Segments'));
            this.registerFilterableField('ignore_segments', gettext('Segments to Ignore'));
            this.registerFilterableField('cohort', gettext('Cohort'));
            this.registerFilterableField('enrollment_mode', gettext('Enrollment Mode'));
        },

        fetch: function (options) {
            // Handle gateway timeouts
            return PagingCollection.prototype.fetch.call(this, options).fail(function (jqXHR) {
                this.trigger('serverError', jqXHR.status, jqXHR.responseJson);
            }.bind(this));
        },

        state: {
            pageSize: 25
        },

        queryParams: {
            course_id: function () { return this.courseId; }
        },

        // Shim code follows for backgrid.paginator 0.3.5
        // compatibility, which expects the backbone.pageable
        // (pre-backbone.paginator) API.
        hasPrevious: function () {
            return this.hasPreviousPage();
        },

        hasNext: function () {
            return this.hasNextPage();
        }
    });

    return LearnerCollection;
});
