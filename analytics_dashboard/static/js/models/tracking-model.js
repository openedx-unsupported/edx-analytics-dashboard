define(['backbone', 'underscore'], (Backbone, _) => {
  'use strict';

  /**
     * Stores our tracking logic and information.
     */
  const TrackingModel = Backbone.Model.extend({

    /**
         * Determine if the application is tracked.
         */
    isTracking() {
      const self = this;
      const trackId = self.get('segmentApplicationId');
      return !_(trackId).isUndefined() && !_(trackId).isNull();
    },
  });

  return TrackingModel;
});
