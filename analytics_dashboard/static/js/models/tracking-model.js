define(['backbone', 'underscore'], function(Backbone, _) {
    'use strict';

    /**
     * Stores our tracking logic and information.
     */
    var TrackingModel = Backbone.Model.extend({

        /**
         * Determine if the application is tracked.
         */
        isTracking: function() {
            var self = this,
                trackId = self.get('segmentApplicationId');
            return !_(trackId).isUndefined() && !_(trackId).isNull();
        }
    });

    return TrackingModel;
});
