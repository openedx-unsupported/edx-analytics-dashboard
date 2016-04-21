define(function (require) {
    'use strict';

    var PagingCollection = require('uitk/pagination/paging-collection'),

        LearnerModel = require('learners/common/models/learner'),
        LearnerUtils = require('learners/common/utils'),

        LearnerCollection;

    LearnerCollection = PagingCollection.extend({
        model: LearnerModel,

        initialize: function (models, options) {
            PagingCollection.prototype.initialize.call(this, options);

            this.url = options.url;
            this.courseId = options.courseId;

            this.registerSortableField('username', gettext('Name'));
            this.registerSortableField('problems_attempted', gettext('Problems Tried'));
            this.registerSortableField('problems_completed', gettext('Problems Correct'));
            this.registerSortableField('videos_viewed', gettext('Videos'));
            this.registerSortableField('problem_attempts_per_completed', gettext('Attempts per Problem Correct'));
            this.registerSortableField('discussion_contributions', gettext('Discussions'));

            this.registerFilterableField('segments', gettext('Segments'));
            this.registerFilterableField('ignore_segments', gettext('Segments to Ignore'));
            this.registerFilterableField('cohort', gettext('Cohort'));
            this.registerFilterableField('enrollment_mode', gettext('Enrollment Mode'));
        },

        fetch: function (options) {
            return PagingCollection.prototype.fetch.call(this, options)
                .fail(LearnerUtils.handleAjaxFailure.bind(this));
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
