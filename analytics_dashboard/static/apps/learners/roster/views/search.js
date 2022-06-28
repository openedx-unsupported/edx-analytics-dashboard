/**
 * Subclass of Backgrid.Extension.Filter which allows us to search
 * for learners.  Fixes accessibility issues with the Backgrid
 * filter component.
 *
 * This class is a hack in that it directly copies source code from
 * backgrid.filter 0.3.5, making it heavily reliant on that
 * particular implementation.
 */
define((require) => {
  'use strict';

  const $ = require('jquery');
  const _ = require('underscore');
  const Backgrid = require('backgrid');

  const listSearchTemplate = require('components/generic-list/list/templates/search.underscore');

  require('backgrid-filter');

  const LearnerSearch = Backgrid.Extension.ServerSideFilter.extend({
    className() {
      return [Backgrid.Extension.ServerSideFilter.prototype.className, 'learners-search'].join(' ');
    },

    events() {
      return _.extend(
        Backgrid.Extension.ServerSideFilter.prototype.events,
        {
          'click .search': 'search',
          'click .clear.btn': 'clear',
        },
      );
    },

    template: _.template(listSearchTemplate, null, { variable: null }),

    initialize(options) {
      this.options = options || {};
      this.listenTo(options.collection, 'sync', this.render);
      Backgrid.Extension.ServerSideFilter.prototype.initialize.call(this, options);
    },

    clearButton() {
      return this.$el.find('[data-backgrid-action=clear]');
    },

    render() {
      this.value = this.options.collection.getSearchString();
      this.$el.empty().append(this.template({
        id: 'search-learners',
        name: this.name,
        placeholder: this.placeholder,
        value: this.value,
        labelText: gettext('Search learners'),
        executeSearchText: gettext('search'),
        clearSearchText: gettext('clear search'),
      }));
      this.showClearButtonMaybe();
      this.delegateEvents();
      return this;
    },

    search(event) {
      const searchString = this.searchBox().val().trim();
      event.preventDefault();
      if (searchString === '') {
        this.collection.unsetSearchString();
      } else {
        this.collection.setSearchString(searchString);
        this.options.trackingModel.trigger('segment:track', 'edx.bi.roster.searched', {
          category: 'search',
        });
      }
      this.execute();
    },

    clear(event) {
      event.preventDefault();
      this.collection.unsetSearchString();
      this.searchBox().val('');
      this.execute();
    },

    execute() {
      this.collection.refresh();
      this.resetFocus();
    },

    resetFocus() {
      $('#learner-app-focusable').focus();
    },
  });

  return LearnerSearch;
});
