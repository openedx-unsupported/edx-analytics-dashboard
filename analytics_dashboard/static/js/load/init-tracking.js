/**
 * Initialize tracking for page load and clicking.
 *
 * Elements with data-track-type="click" will be instrumented.  The event will
 * be defined by the element's data-track-event and all other data-track-*
 * attribute values will be returns as properties to be tracked.
 */
define(['jquery', 'underscore', 'views/clickable-view', 'views/tracking-view', 'utils/utils'],
    function ($, _, ClickableView, TrackingView, Utils) {
        'use strict';
        return function (models) {
            if (models.trackingModel.isTracking()) {
                // this is only activated when tracking ID is set
                new TrackingView({
                    el: document,
                    model: models.trackingModel,
                    userModel: models.userModel,
                    courseModel: models.courseModel
                });

                // instrument the click events
                _($('[data-track-type="click"]')).each(function (track) {
                    // get the properties that we want to send back for with
                    // the tracking events
                    var properties = Utils.getNodeProperties(track.attributes,
                        'data-track-', ['data-track-event']);

                    new ClickableView({
                        model: models.trackingModel,
                        trackEventType: $(track).attr('data-track-event'),
                        trackProperties: properties,
                        el: track
                    });
                });

            }
        };
    });
