define((require) => {
  'use strict';

  const _ = require('underscore');
  const Marionette = require('marionette');

  return Marionette.ItemView.extend({
    template: _.template(require('learners/detail/templates/return-to-learners.underscore')),

    templateHelpers() {
      return {
        returnText: gettext('Return to Learners'),
        queryString: this.options.queryString,
      };
    },
  });
});
