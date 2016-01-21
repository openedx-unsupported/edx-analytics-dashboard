/**
 * Renders a sortable, filterable, and searchable paginated table of
 * learners for the Learner Analytics app.
 *
 * Requires the following values in the options hash:
 * - options.collection - an instance of LearnerCollection
 */
define([
    'backgrid',
    'backgrid-filter',
    'backgrid-paginator',
    'jquery',
    'marionette',
    'text!learners/templates/base-header-cell.underscore',
    'text!learners/templates/name-username-cell.underscore',
    'text!learners/templates/page-handle.underscore',
    'text!learners/templates/roster.underscore',
    'text!learners/templates/search.underscore',
    'underscore',
    'utils/utils'
], function (
    Backgrid,
    _backgridFilter,
    _backgridPaginator,
    $,
    Marionette,
    baseHeaderCellTemplate,
    nameUsernameCellTemplate,
    pageHandleTemplate,
    rosterTemplate,
    learnerSearchTemplate,
    _,
    Utils
) {
    'use strict';

    var BaseHeaderCell,
        createEngagementCell,
        EngagementHeaderCell,
        LearnerSearch,
        LearnerRosterView,
        NameAndUsernameCell,
        PagingFooter;

    /**
     * Base class for all header cells.  Adds proper routing and icons.
     */
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
            var sortDirectionMap,
                sortIcon = this.$('i');
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

    /**
     * Cell class for engagement headers, which need to be right
     * aligned.
     */
    EngagementHeaderCell = BaseHeaderCell.extend({
        className: 'learner-engagement-cell'
    });

    /**
     * Factory for creating a Backgrid cell class that renders a key
     * from the learner model's engagement attribute.
     */
    createEngagementCell = function (key) {
        return Backgrid.Cell.extend({
            className: 'learner-engagement-cell ' + key,
            formatter: {
                fromRaw: function (rawData, model) {
                    var value = model.get('engagements')[key];
                    // Translators: 'N/A' is an abbreviation of "Not Applicable". Please translate accordingly.
                    return value === null ? gettext('N/A') : value;
                }
            }
        });
    };

    /**
     * Class for the pagination footer, which needs to set focus to
     * the top of the table after being clicked.
     */
    PagingFooter = Backgrid.Extension.Paginator.extend({
        attributes: {
            role: 'navigation'
        },
        controls: {
            rewind: {title: 'First', label: '<i class="fa fa-fast-backward" aria-hidden="true"></i>'},
            back: {title: 'Previous', label: '<i class="fa fa-step-backward" aria-hidden="true"></i>'},
            forward: {title: 'Next', label: '<i class="fa fa-step-forward" aria-hidden="true"></i>'},
            fastForward: {title: 'Last', label: '<i class="fa fa-fast-forward" aria-hidden="true"></i>'}
        },
        pageHandle: Backgrid.Extension.PageHandle.extend({
            template: _.template(pageHandleTemplate),
            render: function () {
                var isHiddenFromSr = true,
                    srText;
                Backgrid.Extension.PageHandle.prototype.render.apply(this, arguments);
                if (this.isRewind) {
                    srText = gettext('first page');
                } else if (this.isBack) {
                    srText = gettext('previous page');
                } else if (this.isForward) {
                    srText = gettext('next page');
                } else if (this.isFastForward) {
                    srText = gettext('last page');
                } else {
                    srText = gettext('page') + ' ';
                    isHiddenFromSr = false;
                }
                this.$el.html(this.template({
                    title: this.title,
                    srText: srText,
                    isHiddenFromSr: isHiddenFromSr,
                    nonSrText: this.label,
                    isDisabled: this.$el.hasClass('disabled')
                }));
                this.delegateEvents();
                return this;
            },
            changePage: function () {
                Backgrid.Extension.PageHandle.prototype.changePage.apply(this, arguments);
                if (!this.$el.hasClass('active') && !this.$el.hasClass('disabled')) {
                    $('#learner-app-focusable').focus();
                } else {
                    this.$('a').focus();
                }
            }
        })
    });

    /**
     * Cell class which combines username and name.  The username links
     * to the user detail page.
     */
    NameAndUsernameCell = Backgrid.Cell.extend({
        className: 'learner-name-username-cell',
        template: _.template(nameUsernameCellTemplate),
        render: function () {
            this.$el.html(this.template(this.model.toJSON()));
            return this;
        }
    });

    /**
     * Subclass of Backgrid.Extension.Filter which allows us to search
     * for learners.  Fixes accessibility issues with the Backgrid
     * filter component.
     *
     * This class is a hack in that it directly copies source code from
     * backgrid.filter 0.3.5, making it heavily reliant on that
     * particular implementation.
     */
    LearnerSearch = Backgrid.Extension.ServerSideFilter.extend({
        template: _.template(learnerSearchTemplate, null, {variable: null}),
        render: function () {
            this.$el.empty().append(this.template({
                name: this.name,
                placeholder: this.placeholder,
                value: this.value,
                labelText: gettext('Search learners'),
                clearSearchText: gettext('clear search')
            }));
            this.showClearButtonMaybe();
            this.delegateEvents();
            return this;
        }
    });

    /**
     * Wraps up the search view, table view, and pagination footer
     * view.
     */
    LearnerRosterView = Marionette.LayoutView.extend({
        className: 'learner-roster',

        template: _.template(rosterTemplate),

        templateHelpers: function () {
            // Note that we currently assume that all the learners in
            // the roster were last updated at the same time.
            var firstLearner = this.options.collection.at(0),
                lastUpdatedMessage = _.template(gettext('Date Last Updated: <%- lastUpdatedDateString %>')),
                lastUpdatedDateString = (firstLearner && firstLearner.get('last_updated')) ?
                    Utils.formatDate(firstLearner.get('last_updated')) :
                    gettext('unknown');
            return {
                lastUpdatedMessage: lastUpdatedMessage({lastUpdatedDateString: lastUpdatedDateString})
            };
        },

        regions: {
            search: '.learners-search',
            table: '.learners-table',
            paginator: '.learners-paging-footer'
        },

        initialize: function (options) {
            this.options = options || {};
            this.options.collection.on('serverError', this.handleServerError, this);
            this.options.collection.on('sync', this.handleSync, this);
        },

        handleServerError: function (status) {
            if (status === 504) {
                // TODO: verify copy with Alison
                this.triggerMethod('appError', gettext('504: Server error: processing your request took too long to complete. Reload the page to try again.')); // jshint ignore:line
            } else {
                // TODO: verify copy with Alison
                this.triggerMethod(
                    'appError', gettext('Server error: your request could not be processed. Reload the page to try again.') // jshint ignore:line
                );
            }
        },

        handleSync: function () {
            this.triggerMethod('clearError');
        },

        onBeforeShow: function () {
            // Render the search bar
            this.showChildView('search', new LearnerSearch({
                collection: this.options.collection,
                name: 'text_search',
                placeholder: gettext('Find a learner')
            }));
            // Render the table
            this.showChildView('table', new Backgrid.Grid({
                className: 'table',  // Use bootstrap styling
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
                        column = _.extend(column, {cell: NameAndUsernameCell, headerCell: BaseHeaderCell});
                    } else {
                        column = _.extend(column, {cell: createEngagementCell(key), headerCell: EngagementHeaderCell});
                    }
                    return column;
                })
            }));
            // Render the paging footer
            this.showChildView('paginator', new PagingFooter({
                collection: this.options.collection, goBackFirstOnSort: false
            }));
            // Accessibility hacks
            this.$('table').prepend('<caption class="sr-only">' + gettext('Learner Roster') + '</caption>');
        }
    });

    return LearnerRosterView;
});
