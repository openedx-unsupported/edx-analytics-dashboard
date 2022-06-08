/**
 * Displays a table of items and a pagination control.
 */
define((require) => {
  'use strict';

  const _ = require('underscore');
  const Backgrid = require('backgrid');
  const Marionette = require('marionette');

  const BaseHeaderCell = require('./base-header-cell');
  const PagingFooter = require('./paging-footer');
  const listTableTemplate = require('components/generic-list/list/templates/table.underscore');

  const ListTableView = Marionette.LayoutView.extend({
    template: _.template(listTableTemplate),

    regions: {
      table: '.list-table',
      paginator: '.list-paging-footer',
    },

    initialize(options) {
      this.options = _.defaults({}, options, {
        tableName: gettext('Generic List'),
        trackSubject: 'list',
        appClass: '',
      });

      this.options = _.defaults(this.options, {
        trackSortEventName: ['edx', 'bi', this.options.trackSubject, 'sorted'].join('.'),
        trackPageEventName: ['edx', 'bi', this.options.trackSubject, 'paged'].join('.'),
      });

      this.collection.on('backgrid:sort', this.onSort, this);
    },

    onSort(column, direction) {
      this.options.trackingModel.trigger('segment:track', this.options.trackSortEventName, {
        category: `${column.get('name')}_${direction.slice(0, -6)}`,
      });
    },

    onBeforeShow() {
      this.showChildView('table', new Backgrid.Grid({
        className: 'table table-striped dataTable', // Combine bootstrap and datatables styling
        collection: this.options.collection,
        columns: this.buildColumns(),
      }));
      this.showChildView('paginator', new PagingFooter({
        collection: this.options.collection,
        trackingModel: this.options.trackingModel,
        appClass: this.options.appClass,
        trackPageEventName: this.options.trackPageEventName,
      }));
      // Accessibility hacks
      this.$('table').prepend(`<caption class="sr-only">${this.options.tableName}</caption>`);
    },

    /**
         * Returns default column settings.
         */
    createDefaultColumn(label, name) {
      return {
        label,
        name,
        editable: false,
        sortable: true,
        sortType: 'toggle',
        sortValue(model, colName) {
          const sortVal = model.get(colName);
          if (sortVal === null || sortVal === undefined || sortVal === '') {
            // Force null values to the end of the ascending sorted list
            // NOTE: only works for sorting string value columns
            return 'z';
          }
          return `a ${sortVal}`;
        },
        headerCell: BaseHeaderCell,
        cell: 'string',
      };
    },

    /**
         * Returns column formats for backgrid.  See course-list and roster tables
         * for examples of usage.
         *
         * Use createDefaultColumn for standard column settings.
         */
    buildColumns() {
      throw 'Not implemented'; // eslint-disable-line no-throw-literal
    },

  });

  return ListTableView;
});
