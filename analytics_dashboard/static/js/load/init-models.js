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
            userModel = new UserModel();

        /* jshint ignore:start */
        // initModelData is set by the Django template at render time.
        courseModel.set(initModelData.course);
        trackingModel.set(initModelData.tracking);
        userModel.set(initModelData.user);
        /* jshint ignore:end */

        return {
            courseModel: courseModel,
            trackingModel: trackingModel,
            userModel: userModel
        };
    }
);
