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
    'bootstrap',
    'bootstrap_accessibility',  // adds the aria-describedby to tooltips
    'jquery',
    'marionette',
    'text!learners/templates/cohort-filter.underscore',
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
    _Bootstrap,
    _BootstrapAccessibility,
    $,
    Marionette,
    cohortFilterTemplate,
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
        CohortFiliter,
        createEngagementCell,
        createEngagementHeaderCell,
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
        className: function () {
            return [Backgrid.Extension.ServerSideFilter.prototype.className, 'learners-search'].join(' ');
        },
        events: function () {
            return _.extend(Backgrid.Extension.ServerSideFilter.prototype.events, {'click .search': 'search'});
        },
        template: _.template(learnerSearchTemplate, null, {variable: null}),
        render: function () {
            this.$el.empty().append(this.template({
                name: this.name,
                placeholder: this.placeholder,
                value: this.value,
                labelText: gettext('Search learners'),
                executeSearchText: gettext('search'),
                clearSearchText: gettext('clear search')
            }));
            this.showClearButtonMaybe();
            this.delegateEvents();
            return this;
        },
        search: function () {
            Backgrid.Extension.ServerSideFilter.prototype.search.apply(this, arguments);
            this.resetFocus();
        },
        clear: function () {
            Backgrid.Extension.ServerSideFilter.prototype.clear.apply(this, arguments);
            this.resetFocus();
        },
        resetFocus: function () {
            $('#learner-app-focusable').focus();
        }
    });

    /**
     * A component to filter the roster view by cohort.
     */
    CohortFiliter = Marionette.ItemView.extend({
        events: {
            'change #cohort-filter': 'onSelectCohort'
        },
        className: 'learners-cohort-filter',
        template: _.template(cohortFilterTemplate),
        initialize: function (options) {
            this.options = options || {};
            _.bind(this.onSelectCohort, this);
        },
        templateHelpers: function () {
            var cohorts = _.mapObject(this.options.courseMetadata.get('cohorts'), function (numLearners, cohortName) {
                return {
                    displayName: _.template(ngettext(
                        // jshint ignore:start
                        // Translators: 'cohortName' is the name of the cohort and 'numLearners' is the number of learners in that cohort.  The resulting phrase displays a cohort and the number of students belonging to it.
                        '<%- cohortName %> (<%- numLearners %> learner)',
                        // Translators: 'cohortName' is the name of the cohort and 'numLearners' is the number of learners in that cohort.  The resulting phrase displays a cohort and the number of students belonging to it.
                        '<%- cohortName %> (<%- numLearners %> learners)',
                        // jshint ignore:end
                        numLearners
                    ))({
                        cohortName: cohortName,
                        numLearners: Utils.localizeNumber(numLearners, 0)
                    })
                };
            });

            return {
                cohorts: cohorts,
                // Translators: "Cohort Groups" refers to groups of students within a course.
                selectDisplayName: gettext('Cohort Groups'),
                // Translators: "All" refers to viewing all the learners in a course.
                allCohortsSelectedMessage: gettext('All')
            };
        },
        onSelectCohort: function (event) {
            // Sends a request to the server for the learner list filtered by
            // cohort then resets focus.
            event.preventDefault();
            this.collection.setFilterField('cohort', $(event.currentTarget).find('option:selected').val());
            this.collection.refresh();
            $('#learner-app-focusable').focus();
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
            search: '.learners-search-container',
            table: '.learners-table',
            paginator: '.learners-paging-footer',
            cohortFilter: '.learners-cohort-filter-container'
        },

        initialize: function (options) {
            this.options = options || {};
            this.options.collection.on('serverError', this.handleServerError, this);
            this.options.collection.on('networkError', this.handleNetworkError, this);
            this.options.collection.on('sync', this.handleSync, this);
            this.options.courseMetadata.on('serverError', this.handleServerError, this);
            this.options.courseMetadata.on('networkError', this.handleNetworkError, this);
            this.options.courseMetadata.on('sync', this.handleSync, this);
        },

        handleServerError: function (status) {
            if (status === 504) {
                this.triggerMethod('appError', gettext('504: Server error: processing your request took too long to complete. Reload the page to try again.')); // jshint ignore:line
            } else {
                this.triggerMethod(
                    'appError', gettext('Server error: your request could not be processed. Reload the page to try again.') // jshint ignore:line
                );
            }
        },

        handleNetworkError: function () {
            this.triggerMethod(
                'appError', gettext('Network error: your request could not be processed. Reload the page to try again.')
            );
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
                        column.cell = NameAndUsernameCell;
                        column.headerCell = BaseHeaderCell;
                    } else {
                        column.cell = createEngagementCell(key);
                        column.headerCell = createEngagementHeaderCell(key);
                    }

                    return column;
                })
            }));
            // Render the paging footer
            this.showChildView('paginator', new PagingFooter({
                collection: this.options.collection, goBackFirstOnSort: false
            }));
            // Render the cohort filter
            this.showChildView('cohortFilter', new CohortFiliter({
                collection: this.options.collection,
                courseMetadata: this.options.courseMetadata
            }));
            // Accessibility hacks
            this.$('table').prepend('<caption class="sr-only">' + gettext('Learner Roster') + '</caption>');
        }
    });

    return LearnerRosterView;
});
