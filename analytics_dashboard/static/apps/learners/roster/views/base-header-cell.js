/**
 * Base class for all table header cells.  Adds proper routing and icons.
 */
define(function (require) {
    'use strict';

    var _ = require('underscore'),
        Backgrid = require('backgrid'),

        baseHeaderCellTemplate = require('text!learners/roster/templates/base-header-cell.underscore'),

        BaseHeaderCell;

    BaseHeaderCell = Backgrid.HeaderCell.extend({
        attributes: {
            scope: 'col'
        },
        template: _.template(baseHeaderCellTemplate),
        initialize: function () {
            Backgrid.HeaderCell.prototype.initialize.apply(this, arguments);
            this.collection.on('backgrid:sort', this.onSort, this);
        },
        render: function (column, direction) {
            Backgrid.HeaderCell.prototype.render.apply(this, arguments);
            this.$el.html(this.template({
                label: this.column.get('label')
            }));
            this.renderSortState(column, direction);
            return this;
        },
        onSort: function (column, direction) {
            this.renderSortState(column, direction);
        },
        renderSortState: function (column, direction) {
            var sortIcon = this.$('i'),
                sortDirectionMap;
            if (column && column.cid !== this.column.cid) {
                direction = 'neutral';
            } else {
                direction = direction || 'neutral';
            }
            // Maps a sort direction to its appropriate screen reader
            // text and icon.
            sortDirectionMap = {
                // Translators: "sort ascending" describes the current
                // sort state to the user.
                ascending: {screenReaderText: gettext('sort ascending'), iconClass: 'fa-sort-asc'},
                // Translators: "sort descending" describes the
                // current sort state to the user.
                descending: {screenReaderText: gettext('sort descending'), iconClass: 'fa-sort-desc'},
                // Translators: "click to sort" tells the user that
                // they can click this link to sort by the current
                // field.
                neutral: {screenReaderText: gettext('click to sort'), iconClass: 'fa-sort'}
            };
            sortIcon.removeClass('fa-sort fa-sort-asc fa-sort-desc');
            sortIcon.addClass(sortDirectionMap[direction].iconClass);
            this.$('.sr-sorting-text').text(' ' + sortDirectionMap[direction].screenReaderText);
        }
    });

    return BaseHeaderCell;
});
