/**
 * Displays a table of learners and a pagination control.
 */
define(function (require) {
    'use strict';

    var _ = require('underscore'),
        Backgrid = require('backgrid'),
        Marionette = require('marionette'),

        BaseHeaderCell = require('learners/roster/views/base-header-cell'),
        NameAndUsernameCell = require('learners/roster/views/name-username-cell'),
        PagingFooter = require('learners/roster/views/paging-footer'),
        Utils = require('utils/utils'),
        learnerTableTemplate = require('text!learners/roster/templates/table.underscore'),

        createEngagementCell,
        EngagementHeaderCell,
        LearnerTableView;

    /**
     * Factory for creating a Backgrid cell class that renders a key
     * from the learner model's engagement attribute.
     */
    createEngagementCell = function (key, options) {
        return Backgrid.Cell.extend({

            className: 'learner-engagement-cell ' + key,

            options: options,

            formatter: {
                fromRaw: function (rawData, model) {
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
        className: 'learner-engagement-cell',
    });

    LearnerTableView = Marionette.LayoutView.extend({
        template: _.template(learnerTableTemplate),
        regions: {
            table: '.learners-table',
            paginator: '.learners-paging-footer'
        },
        initialize: function (options) {
            this.options = options || {};
            this.collection.on('backgrid:sort', this.onSort, this);
        },
        onSort: function(column, direction) {
            this.options.trackingModel.trigger('segment:track', 'edx.bi.roster.sorted', {
                category: column.get('name') + '_' + direction.slice(0,-6)
            });
        },
        onBeforeShow: function () {
            var options = this.options;
            this.showChildView('table', new Backgrid.Grid({
                className: 'table table-striped dataTable',  // Combine bootstrap and datatables styling
                collection: this.options.collection,
                columns: _.map(this.options.collection.sortableFields, function (val, key) {
                    var column = {
                        label: val.displayName,
                        name: key,
                        editable: false,
                        sortable: true,
                        sortType: 'toggle'
                    };

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
                })
            }));
            this.showChildView('paginator', new PagingFooter({
                collection: this.options.collection,
                trackingModel: this.options.trackingModel
            }));
            // Accessibility hacks
            this.$('table').prepend('<caption class="sr-only">' + gettext('Learner Roster') + '</caption>');
        }
    });

    return LearnerTableView;
});
