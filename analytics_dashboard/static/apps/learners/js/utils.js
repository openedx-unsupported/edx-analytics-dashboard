define([], function () {
    'use strict';

    var utils = {
        /**
         * Handle an AJAX request which has failed due to either a
         * network error or a server error.  For use within the
         * jqXHR.fail() promise method.
         *
         * When using this function, bind it to an object which
         * extends Backbone.Events.
         *
         * @param jqXHR a jQuery XHR object.
         * @param textStatus
         */
        handleAjaxFailure: function (jqXHR, textStatus) {
            if (jqXHR.readyState === 4) {
                // Request completed; server error
                this.trigger('serverError', jqXHR.status, jqXHR.responseJSON);
            } else {
                // Request incomplete; network error
                this.trigger('networkError', textStatus);
            }
        },

        /**
         * Returns true if the value falls within the range (inclusive of min
         * and exclusive of max).
         *
         * @param value Value in question.
         * @param range Array of min and max.
         */
        inRange: function(value, range) {
            var min = range[0],
                max = range[1],
                minIsUnbounded = _.isNull(min),
                maxIsUnbounded = _.isNull(max);

            if (minIsUnbounded && maxIsUnbounded) {
                throw new Error('min and max range values cannot both be null (unbounded)');
            }

            if (minIsUnbounded) {
                return value < max;
            } else if (maxIsUnbounded) {
                return value >= min;
            }

            return value >= min && value < max;
        },

        /**
         * Transforms events coming from one object to new events on another
         * object.
         *
         * @param originator (object) An object extending Backbone.Events.
         * @param transformFunctions (object) An object hashing event names to
         * event transformation functions.  The event transformation functions
         * take an event name and its arguments and return a new event arguments
         * array.  See 'EventTransformers' for examples.
         * @param forwarder (object) A Marionette object which should trigger
         * the transformed events via 'triggerMethod'.
         */
        mapEvents: function (originator, transformFunctions, forwarder) {
            Object.keys(transformFunctions).map(function (eventName) {
                forwarder.listenTo(originator, eventName, function () {
                    var transformFunc = transformFunctions[eventName],
                        newEventArguments = transformFunc.apply(forwarder, arguments);
                    forwarder.triggerMethod.apply(forwarder, newEventArguments);
                });
            });
        },

        /**
         * Encapsulates a few common event transformer functions for translating
         * model/collection events to view events.
         */
        EventTransformers: {
            /**
             * Transforms an AJAX server error (as defined in handleAjaxFailure)
             * to an application error.
             */
            serverErrorToAppError: function (status) {
                if (status === 504) {
                    return [
                        'appError',
                        // Translators: "504" is a number representing a server error, so please leave it as "504".
                        gettext('504: Server error: processing your request took too long to complete. Reload the page to try again.') // jshint ignore:line
                    ];
                } else {
                    return [
                        'appError',
                        gettext('Server error: your request could not be processed. Reload the page to try again.')
                    ];
                }
            },

            /**
             * Transforms an AJAX network error (as defined in
             * handleAjaxFailure) to an application error.
             */
            networkErrorToAppError: function () {
                return [
                    'appError',
                    gettext('Network error: your request could not be processed. Reload the page to try again.')
                ];
            },

            /**
             * Translates a model/collection 'sync' event to an application
             * 'clearError' event.
             */
            syncToClearError: function () {
                return ['clearError'];
            }
        }
    };

    return utils;
});
