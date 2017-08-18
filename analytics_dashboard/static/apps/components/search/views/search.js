/**
 * Subclass of Backgrid.Extension.Filter which allows us to search
 * for the collection. Fixes accessibility issues with the Backgrid
 * filter component.
 *
 * This class is a hack in that it derives from backgrid.filter 0.3.5 and
 * converted to ES2015, making it heavily reliant on that particular implementation.
 */
import $ from 'jquery';
import _ from 'underscore';
import Backgrid from 'backgrid';

import listSearchTemplate from 'components/search/templates/search.underscore';

// this needs to be imported in order for the filter extension to be included
// eslint-disable-next-line no-unused-vars
import backgridFilter from 'backgrid-filter';

export default class Search extends Backgrid.Extension.ServerSideFilter {
// eslint-disable-next-line class-methods-use-this
  className() {
    return [
      Backgrid.Extension.ServerSideFilter.prototype.className,
      'search-form',
    ].join(' ');
  }

// eslint-disable-next-line class-methods-use-this
  events() {
    return _.extend(Backgrid.Extension.ServerSideFilter.prototype.events,
      {
        'click .search': 'search',
        'click .clear.btn': 'clear',
      },
    );
  }

// eslint-disable-next-line class-methods-use-this
  template() {
    return _.template(listSearchTemplate, null, { variable: null });
  }

  constructor(options) {
    super(options);
    this.options = options || {};

    this.options = _.defaults({}, options, {
      searchLabelText: gettext('Search'),
      trackSubject: 'search',
      focusableSelector: '',
      appClass: '',
    });
    this.options = _.defaults(this.options, {
      trackSearchEventName: ['edx', 'bi', this.options.trackSubject, 'searched'].join('.'),
    });
  }

  initialize(options) {
    super.initialize(options);
    this.collection.on('backgrid:sort', this.onSort, this);
    this.listenTo(this.collection, 'sync', this.render);
  }

  clearButton() {
    return this.$el.find('[data-backgrid-action=clear]');
  }

  render() {
    const appClass = this.options.appClass;
    const template = this.template();
    this.value = this.options.collection.getSearchString();
    this.$el.empty().append(template({
      id: `search-${appClass}`,
      name: this.name,
      placeholder: this.placeholder,
      value: this.value,
      labelText: this.options.searchLabelText,
      executeSearchText: gettext('search'),
      clearSearchText: gettext('clear search'),
    }));
    this.showClearButtonMaybe();
    this.delegateEvents();
    return this;
  }

  search(event) {
    const searchString = this.searchBox().val().trim();
    event.preventDefault();
    if (searchString === '') {
      this.collection.unsetSearchString();
    } else {
      this.collection.setSearchString(searchString);
      this.options.trackingModel.trigger('segment:track', this.options.trackSearchEventName, {
        category: 'search',
      });
    }
    this.execute();
  }

  clear(event) {
    event.preventDefault();
    this.collection.unsetSearchString();
    this.searchBox().val('');
    this.execute();
  }

  execute() {
    this.collection.refresh();
    this.resetFocus();
  }

  resetFocus() {
    $(this.options.focusableSelector).focus();
  }
}
