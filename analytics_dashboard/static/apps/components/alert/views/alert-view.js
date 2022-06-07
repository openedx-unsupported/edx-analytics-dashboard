/**
 * Renders an alert, given an alert type (e.g. error, info).
 */
define((require) => {
  'use strict';

  const _ = require('underscore');
  const Marionette = require('marionette');

  const alertTemplate = require('components/alert/templates/alert.underscore');

  const AlertView = Marionette.ItemView.extend({

    template: _.template(alertTemplate),

    // add new alert types with template variables
    alertTypes: {
      error: {
        iconClass: 'fa-exclamation-triangle',
        containerClass: 'alert-error',
      },
      info: {
        iconClass: 'fa-bullhorn',
        containerClass: 'alert-information',
      },
    },

    defaults: {
      alertType: 'info', // default alert type
      title: undefined, // string title of alert
      body: undefined, // string body of alert
      suggestions: [], // list of strings to display after the body
      link: undefined, // string to display and url of link on alert
    },

    /**
         * Throws an error if the alert type isn't valid.
         */
    validateAlertType(alertType) {
      const types = _(this.alertTypes).keys();
      if (_(types).contains(alertType)) {
        return this;
      }
      throw new Error(`AlertView error: "${alertType}" is not valid. Valid types are ${
        types.join(', ')}.`);
    },

    updateTemplateSetings(alertType) {
      // fill in the alert template variables
      this.options = _.extend({}, this.alertTypes[alertType], this.options);
    },

    initialize(options) {
      this.options = _.extend({}, this.defaults, options);

      const { alertType } = this.options;
      this.validateAlertType(alertType)
        .updateTemplateSetings(alertType);
    },

    templateHelpers() {
      return this.options;
    },
  });

  return AlertView;
});
