/**
 * Displays a table of learners and a pagination control.
 */
define((require) => {
  'use strict';

  const _ = require('underscore');
  const Backgrid = require('backgrid');
  const ListTableView = require('components/generic-list/list/views/table');

  const BaseHeaderCell = require('learners/roster/views/base-header-cell');
  const NameAndUsernameCell = require('learners/roster/views/name-username-cell');
  const Utils = require('utils/utils');
  const learnerTableTemplate = require('learners/roster/templates/table.underscore');

  /**
     * Factory for creating a Backgrid cell class that renders a key
     * from the learner model's engagement attribute.
     */
  const createEngagementCell = (key, options) => Backgrid.Cell.extend({
    className: `learner-engagement-cell ${key}`,

    options,

    formatter: {
      fromRaw(rawData, model) {
        const value = model.get('engagements')[key];
        // Engagement values are always numerical, but we may get
        // "Infinity" for ratio metrics (e.g.
        // problem_attempts_per_completed), which should just be
        // rendered to the user as 'N/A'.
        if (value === Infinity) {
          // Translators: 'N/A' is an abbreviation of "Not Applicable". Please translate accordingly.
          return gettext('N/A');
        }
        return Utils.localizeNumber(value, options.significantDigits);
      },
    },

    enagementCategoryToClass: {
      classRankBottom: 'learner-cell-rank-bottom',
      classRankMiddle: 'learner-cell-rank-middle',
      classRankTop: 'learner-cell-rank-top',
    },

    render() {
      const value = this.model.get('engagements')[key];
      const engagementCategory = this.options.courseMetadata.getEngagementCategory(key, value);
      if (engagementCategory) {
        this.$el.addClass(this.enagementCategoryToClass[engagementCategory]);
        if (engagementCategory === 'classRankTop') {
          this.$el.attr('aria-label', `${value} high`);
        } else if (engagementCategory === 'classRankBottom') {
          this.$el.attr('aria-label', `${value} low`);
        }
      }
      return Backgrid.Cell.prototype.render.apply(this, arguments);
    },
  });

  /**
     * Cell class for engagement headers, which need to be right
     * aligned.
     */
  const EngagementHeaderCell = BaseHeaderCell.extend({
    className: 'learner-engagement-cell',
  });

  const LearnerTableView = ListTableView.extend({
    template: _.template(learnerTableTemplate),
    regions: {
      table: '.learners-table',
      paginator: '.learners-paging-footer',
    },
    buildColumns() {
      let { options } = this;
      return _.map(this.options.collection.sortableFields, (val, key) => {
        const column = this.createDefaultColumn(val.displayName, key);
        if (key === 'username') {
          column.cell = NameAndUsernameCell;
          column.headerCell = BaseHeaderCell;
        } else {
          options = _.defaults({
            significantDigits: key === 'problem_attempts_per_completed' ? 1 : 0,
          }, options);
          column.cell = createEngagementCell(key, options);
          column.headerCell = EngagementHeaderCell;
        }

        return column;
      }, this);
    },
  });

  return LearnerTableView;
});
