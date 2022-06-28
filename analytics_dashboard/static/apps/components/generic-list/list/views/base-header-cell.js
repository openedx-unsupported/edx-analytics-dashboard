/**
 * Base class for all table header cells.  Adds proper routing and icons.
 */
define((require) => {
  'use strict';

  const _ = require('underscore');
  const Backgrid = require('backgrid');

  const baseHeaderCellTemplate = require('components/generic-list/list/templates/base-header-cell.underscore');

  const BaseHeaderCell = Backgrid.HeaderCell.extend({
    attributes: {
      scope: 'col',
    },

    template: _.template(baseHeaderCellTemplate),

    tooltips: {
      // Inherit and fill out.
    },
    container: '.list-table',

    initialize() {
      Backgrid.HeaderCell.prototype.initialize.apply(this, arguments);
      this.collection.on('backgrid:sort', this.onSort, this);
      // Set up the tooltip
      this.$el.attr('title', this.tooltips[this.column.get('name')]);
      this.$el.tooltip({ container: this.container });
    },

    render() {
      let directionWord;
      if (this.collection.state.sortKey && this.collection.state.sortKey === this.column.attributes.name) {
        directionWord = this.collection.state.order === 1 ? 'descending' : 'ascending';
        this.column.attributes.direction = directionWord;
      }

      Backgrid.HeaderCell.prototype.render.apply(this, arguments);
      this.$el.html(this.template({
        label: this.column.get('label'),
      }));

      if (directionWord) { // this column is sorted
        this.renderSortState(this.column, directionWord);
      } else {
        this.renderSortState();
      }
      return this;
    },

    onSort(column, direction) {
      this.renderSortState(column, direction);
    },

    renderSortState(column, direction) {
      const sortIcon = this.$('span.fa');
      let directionOrNeutral;
      if (column && column.cid !== this.column.cid) {
        directionOrNeutral = 'neutral';
      } else {
        directionOrNeutral = direction || 'neutral';
      }
      // Maps a sort direction to its appropriate screen reader
      // text and icon.
      const sortDirectionMap = {
        // Translators: "sort ascending" describes the current sort state to the user.
        ascending: { screenReaderText: gettext('sort ascending'), iconClass: 'fa fa-sort-asc' },
        // Translators: "sort descending" describes the current sort state to the user.
        descending: { screenReaderText: gettext('sort descending'), iconClass: 'fa fa-sort-desc' },
        // eslint-disable-next-line max-len
        // Translators: "click to sort" tells the user that they can click this link to sort by the current field.
        neutral: { screenReaderText: gettext('click to sort'), iconClass: 'fa fa-sort' },
      };
      sortIcon.removeClass('fa-sort fa-sort-asc fa-sort-desc');
      sortIcon.addClass(sortDirectionMap[directionOrNeutral].iconClass);
      this.$('.sr-sorting-text').text(` ${sortDirectionMap[directionOrNeutral].screenReaderText}`);
    },
  });

  return BaseHeaderCell;
});
