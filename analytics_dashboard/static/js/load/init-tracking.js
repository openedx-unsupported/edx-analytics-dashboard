/**
 * Initialize tracking for page load and clicking.
 *
 * Elements with data-track-type="click" will be instrumented.  The event will
 * be defined by the element's data-track-event and all other data-track-*
 * attribute values will be returns as properties to be tracked.
 */
define(
  ['jquery', 'underscore', 'views/clickable-view', 'views/hoverable-view', 'views/tracking-view', 'utils/utils'],
  ($, _, ClickableView, HoverableView, TrackingView, Utils) => {
    'use strict';

    const instrumentEvents = (eventType, TrackingViewClass, models) => {
      _($(`[data-track-type="${eventType}"]`)).each((track) => {
        // get the properties that we want to send back for with
        // the tracking events
        const properties = Utils.getNodeProperties(
          track.attributes,
          'data-track-',
          ['data-track-event', 'data-track-triggered'],
        );
        const trackingView = new TrackingViewClass({
          model: models.trackingModel,
          trackEventType: $(track).attr('data-track-event'),
          trackProperties: properties,
          el: track,
        });
        trackingView.renderIfHasEventType();
      });
    };

    return models => {
      if (models.trackingModel.isTracking()) {
        // this is only activated when tracking ID is set
        const trackingView = new TrackingView({
          el: document,
          model: models.trackingModel,
          userModel: models.userModel,
          courseModel: models.courseModel,
        });
        trackingView.applicationIdSet();

        // instrument the click events
        instrumentEvents('click', ClickableView, models);

        // instrument the hover events
        instrumentEvents('hover', HoverableView, models);
      }
    };
  },
);
