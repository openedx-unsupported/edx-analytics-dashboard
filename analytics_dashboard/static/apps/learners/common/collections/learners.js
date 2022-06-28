define((require) => {
  'use strict';

  const ListCollection = require('components/generic-list/common/collections/collection');
  const LearnerModel = require('learners/common/models/learner');

  const LearnerCollection = ListCollection.extend({
    model: LearnerModel,

    initialize(models, options) {
      ListCollection.prototype.initialize.call(this, models, options);

      this.courseId = options.courseId;

      this.registerSortableField('username', gettext('Name (Username)'));
      this.registerSortableField('problems_attempted', gettext('Problems Tried'));
      this.registerSortableField('problems_completed', gettext('Problems Correct'));
      this.registerSortableField('problem_attempts_per_completed', gettext('Attempts per Problem Correct'));
      this.registerSortableField('videos_viewed', gettext('Videos'));
      this.registerSortableField('discussion_contributions', gettext('Discussions'));

      this.registerFilterableField('segments', gettext('Segments'));
      this.registerFilterableField('ignore_segments', gettext('Segments to Ignore'));
      this.registerFilterableField('cohort', gettext('Cohort'));
      this.registerFilterableField('enrollment_mode', gettext('Enrollment Mode'));
    },

    queryParams: {
      course_id() { return this.courseId; },
    },
  });

  return LearnerCollection;
});
