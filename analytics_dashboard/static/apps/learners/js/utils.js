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
        }
    };

    return utils;
});
