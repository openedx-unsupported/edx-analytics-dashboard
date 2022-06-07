/**
 * Initializes standard models with data from the page.
 *
 * Returns the model.
 */
define(
  ['jquery', 'models/course-model', 'models/tracking-model', 'models/user-model'],
  ($, CourseModel, TrackingModel, UserModel) => {
    'use strict';

    const courseModel = new CourseModel();
    const trackingModel = new TrackingModel();
    const userModel = new UserModel();

    /* eslint-disable no-undef */
    // initModelData is set by the Django template at render time.
    courseModel.set(initModelData.course);
    trackingModel.set(initModelData.tracking);
    userModel.set(initModelData.user);
    /* eslint-enable no-undef */

    return {
      courseModel,
      trackingModel,
      userModel,
    };
  },
);
