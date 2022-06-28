define((require) => {
  'use strict';

  const Backbone = require('backbone');
  const $ = require('jquery');

  const PageModel = Backbone.Model.extend({
    defaults: {
      title: '', // title displayed in header
      lastUpdated: undefined, // last updated date displayed in header
    },

    initialize() {
      this.bind('change:title', this.updateTitleElement);
    },

    updateTitleElement() {
      const self = this;
      $('title').text(function () {
        return $(this).text().replace(/^.*[-]/, `${self.get('title')} -`);
      });
    },
  });

  return PageModel;
});
