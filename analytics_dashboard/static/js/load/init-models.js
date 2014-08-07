/**
 * Initializes standard models with data from the page.
 *
 * Returns the model.
 */
define(['jquery', 'models/course-model', 'models/tracking-model', 'models/user-model'],
        function ($, CourseModel, TrackingModel, UserModel) {
    'use strict';
    var jsonData = JSON.parse($('#content').attr('data-analytics-init')),
        courseModel = new CourseModel(),
        trackingModel = new TrackingModel(),
        userModel = new UserModel();

    courseModel.set(jsonData.course);
    trackingModel.set(jsonData.tracking);
    userModel.set(jsonData.user);

    return {
        courseModel: courseModel,
        trackingModel: trackingModel,
        userModel: userModel
    };
});
