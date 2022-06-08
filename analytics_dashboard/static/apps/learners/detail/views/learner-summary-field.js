define((require) => {
  'use strict';

  const _ = require('underscore');
  const Marionette = require('marionette');

  const template = require('learners/detail/templates/learner-summary-field.underscore');

  /**
     * Displays a field name followed by a value upon model update.
     */
  const LearnerSummaryFieldView = Marionette.LayoutView.extend({

    template: _.template(template),

    /**
         * Options:
         *  - modelAttribute: attribute that the view will listen to change events on
         *  - fieldDisplayName: Display name of field.
         *  - valueFormatter (optional): function callback for formatting value.
         */
    initialize(options) {
      Marionette.LayoutView.prototype.initialize.call(this, options);
      this.options = options || {};
      this.model.on(`change:${this.options.modelAttribute}`, this.render);
    },

    /**
         * Formats 'value' according to the valueFormatter callback if provided.
         * Otherwise, returns the value or 'n/a'.
         */
    formatValue(value) {
      if (_(this.options).has('valueFormatter')) {
        return this.options.valueFormatter(value);
      }
      return this.defaultFormatter(value);
    },

    defaultFormatter(value) {
      // Translators: 'n/a' means 'not available'
      return value || gettext('n/a');
    },

    templateHelpers() {
      return {
        field: this.options.fieldDisplayName,
        value: this.formatValue(this.model.get(this.options.modelAttribute)),
      };
    },

  });

  return LearnerSummaryFieldView;
});
