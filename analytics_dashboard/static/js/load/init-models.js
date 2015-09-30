/**
 * Initializes standard models with data from the page.
 *
 * Returns the model.
 */
define(['jquery', 'models/course-model', 'models/tracking-model', 'models/user-model'],
    function ($, CourseModel, TrackingModel, UserModel) {
        'use strict';
        var courseModel = new CourseModel(),
            trackingModel = new TrackingModel(),
            userModel = new UserModel(),
            modelData = window.initModelData || {}; // initModelData is set by the Django template at render time.

        courseModel.set(modelData.course);
        trackingModel.set(modelData.tracking);
        userModel.set(modelData.user);

        return {
            courseModel: courseModel,
            trackingModel: trackingModel,
            userModel: userModel
        };
    }
);
