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
    'learners/js/utils',
    'learners/js/views/alert-view',
    'marionette',
    'text!learners/templates/cohort-filter.underscore',
    'text!learners/templates/base-header-cell.underscore',
    'text!learners/templates/name-username-cell.underscore',
    'text!learners/templates/page-handle.underscore',
    'text!learners/templates/roster.underscore',
    'text!learners/templates/roster-controls.underscore',
    'text!learners/templates/search.underscore',
    'text!learners/templates/table.underscore',
    'underscore',
    'utils/utils'
], function (
    Backgrid,
    _backgridFilter,
    _backgridPaginator,
    _Bootstrap,
    _BootstrapAccessibility,
    $,
    LearnerUtils,
    AlertView,
    Marionette,
    cohortFilterTemplate,
    baseHeaderCellTemplate,
    nameUsernameCellTemplate,
    pageHandleTemplate,
    rosterTemplate,
    rosterControlsTemplate,
    learnerSearchTemplate,
    learnerTableTemplate,
    _,
    Utils
) {
    'use strict';

    var BaseHeaderCell,
        CohortFilter,
        createEngagementCell,
        createEngagementHeaderCell,
        RosterControlsView,
        LearnerResultsView,
        LearnerRosterView,
        LearnerSearch,
        LearnerTableView,
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
    createEngagementCell = function (key, options) {
        return Backgrid.Cell.extend({

            className: 'learner-engagement-cell ' + key,

            options: options,

            formatter: {
                fromRaw: function (rawData, model) {
                    var value = model.get('engagements')[key];
                    // Translators: 'N/A' is an abbreviation of "Not Applicable". Please translate accordingly.
                    return value === null ? gettext('N/A') : value;
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
            this.collection.setSearchString(this.searchBox().val().trim());
            this.resetFocus();
        },
        clear: function () {
            Backgrid.Extension.ServerSideFilter.prototype.clear.apply(this, arguments);
            this.collection.unsetSearchString();
            this.resetFocus();
        },
        resetFocus: function () {
            $('#learner-app-focusable').focus();
        }
    });

    /**
     * A component to filter the roster view by cohort.
     */
    CohortFilter = Marionette.ItemView.extend({
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
     * A wrapper view for controls.
     */
    RosterControlsView = Marionette.LayoutView.extend({
        template: _.template(rosterControlsTemplate),
        regions: {
            search: '.learners-search-container',
            cohortFilter: '.learners-cohort-filter-container'
        },
        initialize: function (options) {
            this.options = options || {};
        },
        onBeforeShow: function () {
            this.showChildView('search', new LearnerSearch({
                collection: this.options.collection,
                name: 'text_search',
                placeholder: gettext('Find a learner')
            }));
            this.showChildView('cohortFilter', new CohortFilter({
                collection: this.options.collection,
                courseMetadata: this.options.courseMetadata
            }));
        }
    });

    /**
     * Displays a table of learners and a pagination control.
     */
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

    /**
     * Displays either a paginated table of learners or a message that there are
     * no learners to display.
     */
    LearnerResultsView = Marionette.LayoutView.extend({
        template: _.template('<div class="main"></div>'),
        regions: {
            main: '.main'
        },
        initialize: function (options) {
            this.options = options || {};
            this.listenTo(this.options.collection, 'sync', this.onLearnerCollectionUpdated);
        },
        onBeforeShow: function () {
            this.onLearnerCollectionUpdated(this.options.collection);
        },
        onLearnerCollectionUpdated: function (collection) {
            if (collection.length) {
                // Don't re-render the learner table view if one already exists.
                if (!(this.getRegion('main').currentView instanceof LearnerTableView)) {
                    this.showChildView('main', new LearnerTableView({
                        collection: collection,
                        courseMetadata: this.options.courseMetadata
                    }));
                }
            } else {
                this.showChildView('main', this.createAlertView(collection));
            }
        },
        createAlertView: function(collection) {
            var hasSearch =  !_.isNull(collection.searchString) && collection.searchString !== '',
                hasActiveFilter = collection.getActiveFilterFields().length > 0,
                suggestions = [],
                noLearnersMessage,
                detailedMessage;
            if (hasSearch || hasActiveFilter) {
                noLearnersMessage = gettext('No learners matched your criteria.');
                if (hasSearch) {
                    suggestions.push(gettext('Try a different search.'));
                }
                if (hasActiveFilter) {
                    suggestions.push(gettext('Try clearing the filters.'));
                }
            } else {
                noLearnersMessage = gettext('No learner data is currently available for your course.');
                detailedMessage = gettext('No learners are enrolled, or course activity data has not yet been processed. Data is updated every day, so check back regularly for up-to-date metrics.'); // jshint ignore:line
            }

            return new AlertView({
                alertType: 'info',
                title: noLearnersMessage,
                body: detailedMessage,
                suggestions: suggestions
            });
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
            controls: '.learners-table-controls',
            results: '.learners-results'
        },

        initialize: function (options) {
            var eventTransformers;

            this.options = options || {};

            eventTransformers = {
                serverError: LearnerUtils.EventTransformers.serverErrorToAppError,
                networkError: LearnerUtils.EventTransformers.networkErrorToAppError,
                sync: LearnerUtils.EventTransformers.syncToClearError
            };
            LearnerUtils.mapEvents(this.options.collection, eventTransformers, this);
            LearnerUtils.mapEvents(this.options.courseMetadata, eventTransformers, this);
        },

        onBeforeShow: function () {
            this.showChildView('controls', new RosterControlsView({
                collection: this.options.collection,
                courseMetadata: this.options.courseMetadata
            }));
            this.showChildView('results', new LearnerResultsView({
                collection: this.options.collection,
                courseMetadata: this.options.courseMetadata
            }));
        }
    });

    return LearnerRosterView;
});
