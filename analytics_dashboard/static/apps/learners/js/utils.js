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
        }
    };

    return utils;
});
