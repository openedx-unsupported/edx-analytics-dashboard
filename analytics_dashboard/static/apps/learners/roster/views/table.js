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
        createEngagementHeaderCell,
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
                    if (_(value).isNull() || _(value).isUndefined()) {
                        // Translators: 'N/A' is an abbreviation of "Not Applicable". Please translate accordingly.
                        return gettext('N/A');
                    } else {
                        return Utils.localizeNumber(value, options.significantDigits);
                    }
                }
            },

            enagementCategoryToClass: {
                below_average: 'learner-cell-below-average',
                average: 'learner-cell-average',
                above_average: 'learner-cell-above-average'
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
    createEngagementHeaderCell = function (key) {
        var tooltips = {
            problems_attempted: gettext('Number of unique problems this learner attempted.'),
            problems_completed: gettext('Number of unique problems the learner answered correctly.'),
            videos_viewed: gettext('Number of unique videos this learner played.'),
            problem_attempts_per_completed: gettext('Average number of attempts per correct problem. Learners with a relatively high value compared to their peers may be struggling.'),   // jshint ignore:line
            discussion_contributions: gettext('Number of contributions by this learner, including posts, responses, and comments.')   // jshint ignore:line
        };

        return BaseHeaderCell.extend({
            className: 'learner-engagement-cell',

            attributes: _.extend({}, BaseHeaderCell.prototype.attributes, {
                title: tooltips[key]
            }),

            initialize: function () {
                BaseHeaderCell.prototype.initialize.apply(this, arguments);
                this.$el.tooltip({ container: '.learners-table' });
            }

        });
    };

    LearnerTableView = Marionette.LayoutView.extend({
        template: _.template(learnerTableTemplate),
        regions: {
            table: '.learners-table',
            paginator: '.learners-paging-footer'
        },
        initialize: function (options) {
            this.options = options || {};
        },
        onBeforeShow: function () {
            var options = this.options;
            this.showChildView('table', new Backgrid.Grid({
                className: 'table table-striped',  // Use bootstrap styling
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
                        column.headerCell = createEngagementHeaderCell(key);
                    }

                    return column;
                })
            }));
            this.showChildView('paginator', new PagingFooter({
                collection: this.options.collection, goBackFirstOnSort: false
            }));
            // Accessibility hacks
            this.$('table').prepend('<caption class="sr-only">' + gettext('Learner Roster') + '</caption>');
        }
    });

    return LearnerTableView;
});
