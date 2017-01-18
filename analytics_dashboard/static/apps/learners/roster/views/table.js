/**
 * Displays a table of learners and a pagination control.
 */
define(function(require) {
    'use strict';

    var _ = require('underscore'),
        Backgrid = require('backgrid'),
        ListTableView = require('components/generic-list/list/views/table'),

        BaseHeaderCell = require('learners/roster/views/base-header-cell'),
        NameAndUsernameCell = require('learners/roster/views/name-username-cell'),
        Utils = require('utils/utils'),
        learnerTableTemplate = require('text!learners/roster/templates/table.underscore'),

        createEngagementCell,
        EngagementHeaderCell,
        LearnerTableView;

    /**
     * Factory for creating a Backgrid cell class that renders a key
     * from the learner model's engagement attribute.
     */
    createEngagementCell = function(key, options) {
        return Backgrid.Cell.extend({

            className: 'learner-engagement-cell ' + key,

            options: options,

            formatter: {
                fromRaw: function(rawData, model) {
                    var value = model.get('engagements')[key];
                    // Engagement values are always numerical, but we may get
                    // "Infinity" for ratio metrics (e.g.
                    // problem_attempts_per_completed), which should just be
                    // rendered to the user as 'N/A'.
                    if (value === Infinity) {
                        // Translators: 'N/A' is an abbreviation of "Not Applicable". Please translate accordingly.
                        return gettext('N/A');
                    } else {
                        return Utils.localizeNumber(value, options.significantDigits);
                    }
                }
            },

            enagementCategoryToClass: {
                classRankBottom: 'learner-cell-rank-bottom',
                classRankMiddle: 'learner-cell-rank-middle',
                classRankTop: 'learner-cell-rank-top'
            },

            render: function() {
                var value = this.model.get('engagements')[key],
                    engagementCategory = this.options.courseMetadata.getEngagementCategory(key, value);
                if (engagementCategory) {
                    this.$el.addClass(this.enagementCategoryToClass[engagementCategory]);
                    if (engagementCategory === 'classRankTop') {
                        this.$el.attr('aria-label', value + ' high');
                    } else if (engagementCategory === 'classRankBottom') {
                        this.$el.attr('aria-label', value + ' low');
                    }
                }
                return Backgrid.Cell.prototype.render.apply(this, arguments);
            }
        });
    };

    /**
     * Cell class for engagement headers, which need to be right
     * aligned.
     */
    EngagementHeaderCell = BaseHeaderCell.extend({
        className: 'learner-engagement-cell'
    });

    LearnerTableView = ListTableView.extend({
        template: _.template(learnerTableTemplate),
        regions: {
            table: '.learners-table',
            paginator: '.learners-paging-footer'
        },
        buildColumns: function() {
            var options = this.options;
            return _.map(this.options.collection.sortableFields, function(val, key) {
                var column = this.createDefaultColumn(val.displayName, key);
                if (key === 'username') {
                    column.cell = NameAndUsernameCell;
                    column.headerCell = BaseHeaderCell;
                } else {
                    options = _.defaults({
                        significantDigits: key === 'problem_attempts_per_completed' ? 1 : 0
                    }, options);
                    column.cell = createEngagementCell(key, options);
                    column.headerCell = EngagementHeaderCell;
                }

                return column;
            }, this);
        }
    });

    return LearnerTableView;
});
