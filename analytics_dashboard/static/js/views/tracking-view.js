define(['backbone', 'underscore', 'utils/utils'],
    function (Backbone, _, Utils) {
        'use strict';

        /**
         * This 'view' doesn't display anything, but rather sends tracking
         * information in response to 'segment:track' events triggered by the
         * model.
         *
         * Actions will only be tracked if segmentApplicationId is set in the
         * model.
         */
        var TrackingView = Backbone.View.extend({

            /**
             * Reference to segment.io analytics library.  This is set after
             * loading.
             */
            segment: undefined,

            events: {
                'shown.bs.tooltip': 'trackElementEvent'
            },

            initialize: function (options) {
                var self = this;

                self.options = options;

                // wait until you have a segment application ID before kicking
                // up the script
                if (self.model.isTracking()) {
                    self.applicationIdSet();
                } else {
                    self.listenToOnce(self.model, 'change:segmentApplicationId',
                        self.applicationIdSet);
                }
            },

            applicationIdSet: function () {
                var self = this,
                    trackId = self.model.get('segmentApplicationId');

                // if no ID is supplied, then don't track
                if (self.model.isTracking()) {
                    // kick off segment
                    self.initSegment(trackId);
                    self.logUser();

                    // now segment has been loaded, we can track events
                    self.listenTo(self.model, 'segment:track', self.track);
                }
            },

            /**
             * This emits an event to our external tracking systems when an
             * event bubbles up from a DOM element.
             */
            trackElementEvent: function (ev) {
                var self = this,
                    trackedElement = ev.target,
                    properties = Utils.getNodeProperties(
                        trackedElement.attributes, 'data-track-', ['data-track-event']),
                    eventType = $(trackedElement).attr('data-track-event');

                if (!self.model.isTracking() || _.isEmpty(eventType) || !_.isString(eventType)) {
                    return;
                }

                self.track(eventType, properties);
            },

            /**
             * This sets up segment.io for our application and loads the initial
             * page load.
             *
             * this.segment is set for convenience.
             */
            initSegment: function (applicationKey) {
                var self = this;

                if (_.isUndefined(self.segment)) {
                    // This is taken directly from https://segment.io/docs/tutorials/quickstart-analytics.js/.

                    /* jshint ignore:start */
                    // jscs:disable
                    window.analytics=window.analytics||[],window.analytics.methods=['identify','group','track','page','pageview','alias','ready','on','once','off','trackLink','trackForm','trackClick','trackSubmit'],window.analytics.factory=function(t){return function(){var a=Array.prototype.slice.call(arguments);return a.unshift(t),window.analytics.push(a),window.analytics}};for(var i=0;i<window.analytics.methods.length;i++){var key=window.analytics.methods[i];window.analytics[key]=window.analytics.factory(key)}window.analytics.load=function(t){if(!document.getElementById('analytics-js')){var a=document.createElement('script');a.type='text/javascript',a.id='analytics-js',a.async=!0,a.src=('https:'===document.location.protocol?'https://':'http://')+'cdn.segment.io/analytics.js/v1/'+t+'/analytics.min.js';var n=document.getElementsByTagName('script')[0];n.parentNode.insertBefore(a,n)}},window.analytics.SNIPPET_VERSION='2.0.9';
                    // jscs:enable
                    /* jshint ignore:end */

                    // shortcut to segment.io
                    self.segment = window.analytics;
                }

                // provide our application key for logging
                self.segment.load(applicationKey);

                // this needs to be called once
                self.segment.page(self.buildCourseProperties());
            },

            /**
             * Log the user.
             */
            logUser: function () {
                var self = this,
                    userModel = self.options.userModel;
                self.segment.identify(userModel.get('username'), {
                    name: userModel.get('name'),
                    email: userModel.get('email'),
                    ignoreInReporting: userModel.get('ignoreInReporting')
                });
            },

            buildCourseProperties: function() {
                var self = this,
                    course = {};

                if (self.options.courseModel) {
                    course.courseId = self.options.courseModel.get('courseId');
                }

                if (self.model.has('page')) {
                    course.label = self.model.get('page');
                }

                return course;
            },

            /**
             * Catch 'segment:track' events and create events and send
             * to segment.io.
             *
             * @param eventType String event type.
             */
            track: function (eventType, properties) {
                var self = this,
                    course = self.buildCourseProperties();

                // send event to segment including the course ID
                self.segment.track(eventType, _.extend(course, properties));
            }

        });

        return TrackingView;
    }
);
