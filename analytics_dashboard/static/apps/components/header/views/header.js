/**
 * Renders a section title and last updated date for the learner.
 */
define((require) => {
  'use strict';

  const _ = require('underscore');
  const Marionette = require('marionette');

  const headerTemplate = require('components/header/templates/header.underscore');

  const HeaderView = Marionette.ItemView.extend({

    template: _.template(headerTemplate),

    modelEvents: {
      change: 'render',
    },

    templateHelpers() {
      return {
        title: this.model.get('title'),
      };
    },

  });

  return HeaderView;
});
