define(['backbone', 'jquery', 'underscore', 'utils/utils'],
    function(Backbone, $, _, Utils) {
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

            initialize: function(options) {
                var self = this;

                self.options = options;

                // wait until you have a segment application ID before kicking
                // up the script
                self.listenToOnce(self.model, 'change:segmentApplicationId', self.applicationIdSet);
            },

            applicationIdSet: function() {
                var self = this,
                    trackId = self.model.get('segmentApplicationId');

                // if no ID is supplied, then don't track
                if (self.model.isTracking()) {
                    // kick off segment
                    self.initSegment(trackId);
                    self.logUser();

                    // now segment has been loaded, we can track events
                    self.listenTo(self.model, 'segment:track', self.track);
                    self.listenTo(self.model, 'segment:page', self.page);
                }
            },

            /**
             * This emits an event to our external tracking systems when an
             * event bubbles up from a DOM element.
             */
            trackElementEvent: function(ev) {
                var self = this,
                    trackedElement = ev.target,
                    properties = Utils.getNodeProperties(
                        trackedElement.attributes, 'data-track-', ['data-track-event', 'data-track-triggered']),
                    eventType = $(trackedElement).attr('data-track-event'),
                    trackType = $(trackedElement).attr('data-track-type'),
                    triggered = $(trackedElement).attr('data-track-triggered');

                if ((!self.model.isTracking() || _.isEmpty(eventType) || !_.isString(eventType)) ||
                        (trackType === 'tooltip' && triggered)) {
                    return;
                }

                self.track(eventType, properties);
                $(trackedElement).attr('data-track-triggered', 'true');
            },

            /**
             * This sets up segment.io for our application and loads the initial
             * page load.
             *
             * this.segment is set for convenience.
             */
            initSegment: function(applicationKey) {
                var self = this;

                if (_.isUndefined(self.segment)) {
                    // This is taken directly from https://segment.io/docs/tutorials/quickstart-analytics.js/.

                    // eslint-disable-next-line
                    window.analytics = window.analytics || [], window.analytics.methods = ['identify', 'group', 'track', 'page', 'pageview', 'alias', 'ready', 'on', 'once', 'off', 'trackLink', 'trackForm', 'trackClick', 'trackSubmit'], window.analytics.factory = function(t) { return function() { var a = Array.prototype.slice.call(arguments); return a.unshift(t), window.analytics.push(a), window.analytics; }; }; for (var i = 0; i < window.analytics.methods.length; i++) { var key = window.analytics.methods[i]; window.analytics[key] = window.analytics.factory(key); }window.analytics.load = function(t) { if (!document.getElementById('analytics-js')) { var a = document.createElement('script'); a.type = 'text/javascript', a.id = 'analytics-js', a.async = !0, a.src = ('https:' === document.location.protocol ? 'https://' : 'http://') + 'cdn.segment.io/analytics.js/v1/' + t + '/analytics.min.js'; var n = document.getElementsByTagName('script')[0]; n.parentNode.insertBefore(a, n); } }, window.analytics.SNIPPET_VERSION = '2.0.9';


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
            logUser: function() {
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
                    course.org = self.options.courseModel.get('org');
                }

                if (self.model.has('page')) {
                    course.current_page = self.model.get('page');
                    course.label = self.model.get('page').name;
                }

                return course;
            },

            /**
             * Because of limitations on HTML element data attributes, we encode objects flately with hyphen separated
             * keys and need to transform those keys/values back into objects.
             */
            transformPropertiesFromHTMLAttributes: function(props) {
                var properties = props,
                    targetNameParts = [],
                    parts = ['scope', 'lens', 'report', 'depth'],
                    partVal;
                // collapse target scope, lens, report, and depth to a target_page dict
                if ('target-scope' in properties) {
                    properties.target_page = {};
                    parts.forEach(function(part) {
                        partVal = properties['target-' + part] || '';
                        properties.target_page[part] = partVal;
                        if (partVal !== '' && partVal !== undefined) {
                            targetNameParts.push(partVal);
                        }
                        delete properties['target-' + part];
                    });
                    properties.target_page.name = targetNameParts.join('_');
                }

                // convert hyphens to underscores for menu_depth and link_name
                if ('menu-depth' in properties) {
                    properties.menu_depth = properties['menu-depth'] || '';
                    delete properties['menu-depth'];
                }
                if ('link-name' in properties) {
                    properties.link_name = properties['link-name'] || '';
                    delete properties['link-name'];
                }

                // create category from menu_depth and link_name if it is not defined
                if ('menu_depth' in properties && 'link_name' in properties && !('category' in properties)) {
                    properties.category = properties.menu_depth + '+' + properties.link_name;
                }

                return properties;
            },

            /**
             * Catch 'segment:track' events and create events and send
             * to segment.io.
             *
             * @param eventType String event type.
             */
            track: function(eventType, properties) {
                var self = this,
                    course = self.buildCourseProperties(),
                    transformedProps;
                transformedProps = self.transformPropertiesFromHTMLAttributes(properties);
                // send event to segment including the course ID
                self.segment.track(eventType, _.extend(course, transformedProps));
            },

            /**
             * Catch 'segment:page' events in order to send a page view event to
             * segment.io.
             */
            page: function(pageName, metadata) {
                this.segment.page(pageName, _.extend({}, this.buildCourseProperties(), metadata));
            }
        });

        return TrackingView;
    }
);
