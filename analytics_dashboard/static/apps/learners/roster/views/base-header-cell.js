/**
 * Base class for all table header cells.  Adds proper routing and icons.
 */
define(function(require) {
    'use strict';

    var _ = require('underscore'),
        Backgrid = require('backgrid'),

        baseHeaderCellTemplate = require('text!learners/roster/templates/base-header-cell.underscore'),

        BaseHeaderCell,
        tooltips;

    tooltips = {
        username: gettext('The name and username of this learner. Click to sort by username.'),
        problems_attempted: gettext('Number of unique problems this learner attempted.'),
        problems_completed: gettext('Number of unique problems the learner answered correctly.'),
        videos_viewed: gettext('Number of unique videos this learner played.'),
        // eslint-disable-next-line max-len
        problem_attempts_per_completed: gettext('Average number of attempts per correct problem. Learners with a relatively high value compared to their peers may be struggling.'),
        // eslint-disable-next-line max-len
        discussion_contributions: gettext('Number of contributions by this learner, including posts, responses, and comments.')
    };

    BaseHeaderCell = Backgrid.HeaderCell.extend({
        attributes: {
            scope: 'col'
        },

        template: _.template(baseHeaderCellTemplate),

        initialize: function() {
            Backgrid.HeaderCell.prototype.initialize.apply(this, arguments);
            this.collection.on('backgrid:sort', this.onSort, this);
            // Set up the tooltip
            this.$el.attr('title', tooltips[this.column.get('name')]);
            this.$el.tooltip({container: '.learners-table'});
        },

        render: function(column, direction) {
            if (this.collection.state.sortKey && this.collection.state.sortKey === this.column.attributes.name) {
                direction = this.collection.state.order ? 'ascending' : 'descending';
                this.column.attributes.direction = direction;
                column = this.column;
            }
            Backgrid.HeaderCell.prototype.render.apply(this, arguments);
            this.$el.html(this.template({
                label: this.column.get('label')
            }));
            this.renderSortState(column, direction);
            return this;
        },

        onSort: function(column, direction) {
            this.renderSortState(column, direction);
        },

        renderSortState: function(column, direction) {
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
