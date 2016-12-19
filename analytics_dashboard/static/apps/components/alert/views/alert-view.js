/**
 * Renders an alert, given an alert type (e.g. error, info).
 */
define(function(require) {
    'use strict';

    var _ = require('underscore'),
        Marionette = require('marionette'),

        alertTemplate = require('text!components/alert/templates/alert.underscore'),

        AlertView;

    AlertView = Marionette.ItemView.extend({

        template: _.template(alertTemplate),

        // add new alert types with template variables
        alertTypes: {
            error: {
                iconClass: 'fa-exclamation-triangle',
                containerClass: 'alert-error'
            },
            info: {
                iconClass: 'fa-bullhorn',
                containerClass: 'alert-information'
            }
        },

        defaults: {
            alertType: 'info',  // default alert type
            title: undefined,   // string title of alert
            body: undefined,    // string body of alert
            suggestions: [],    // list of strings to display after the body
            link: undefined    // string to display and url of link on alert
        },

        /**
         * Throws an error if the alert type isn't valid.
         */
        validateAlertType: function(alertType) {
            var types = _(this.alertTypes).keys();
            if (_(types).contains(alertType)) {
                return this;
            } else {
                throw new Error('AlertView error: "' + alertType + '" is not valid. Valid types are ' +
                    types.join(', ') + '.');
            }
        },

        updateTemplateSetings: function(alertType) {
            // fill in the alert template variables
            this.options = _.extend({}, this.alertTypes[alertType], this.options);
        },

        initialize: function(options) {
            var alertType;

            this.options = _.extend({}, this.defaults, options);

            alertType = this.options.alertType;
            this.validateAlertType(alertType)
                .updateTemplateSetings(alertType);
        },

        templateHelpers: function() {
            return this.options;
        }
    });

    return AlertView;
});
