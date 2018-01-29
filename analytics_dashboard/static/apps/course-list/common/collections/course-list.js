/**
 * Collection of courses stored client-side.
 */
define(function(require) {
    'use strict';

    var $ = require('jquery'),
        _ = require('underscore'),
        Backbone = require('backbone'),
        ListCollection = require('components/generic-list/common/collections/collection'),
        ProgramsCollection = require('course-list/common/collections/programs'),
        CourseModel = require('course-list/common/models/course'),
        FieldFilter = require('course-list/common/filters/field-filter'),
        ArrayFieldFilter = require('course-list/common/filters/array-field-filter'),
        FilterSet = require('course-list/common/filters/filter-set'),
        SearchFilter = require('course-list/common/filters/search-filter'),

        // this is a lightweight collection that will store the original models
        // in order to restore to the full/original state after filtering is cleared
        ShadowCourseListCollection = Backbone.Collection.extend({
            model: CourseModel
        }),
        CourseListCollection;

    CourseListCollection = ListCollection.extend({

        mode: 'client',

        model: CourseModel,

        /**
         * The collection in its entirety.  Used to restore the collection clear
         * clearing filters.
         */
        shadowCollection: undefined,

        /**
         * Matcher used when searching and created by the paginator's ClientSideFilter.
         */
        searchMatcher: undefined,

        initialize: function(models, options) {
            ListCollection.prototype.initialize.call(this, models, options);

            // original collection are saved for filtering and restoring when filters are unset
            this.shadowCollection = new ShadowCourseListCollection(models);
            this.shadowCollection.listenTo(this, 'add', function(model, collection, ops) {
                this.add(model, ops);
            });
            this.shadowCollection.listenTo(this, 'remove', function(model, collection, ops) {
                this.remove(model, ops);
            });

            this.programsCollection = options.programsCollection || new ProgramsCollection([]);
            // add program_ids to programs array on every course
            this.programsCollection.each(_.bind(function(program) {
                var courseIds = program.get('course_ids');
                _.each(courseIds, function(courseId) {
                    var course = this.shadowCollection.get(courseId);
                    if (course !== undefined) {
                        course.set({
                            program_ids: course.get('program_ids').concat(program.get('program_id'))
                        });
                    }
                }, this);

                // Also append this program's ID and display name to filterNameToDisplay
                // (so that the active filters will display the program title, not the ID)
                if (this.filterNameToDisplay === undefined) {
                    this.filterNameToDisplay = {program_ids: {}};
                } else if (this.filterNameToDisplay.program_ids === undefined) {
                    this.filterNameToDisplay.program_ids = {};
                }
                this.filterNameToDisplay.program_ids[program.get('program_id')] = program.get('program_title');
            }, this));

            this.registerSortableField('catalog_course_title', gettext('Course Name'));
            this.registerSortableField('start_date', gettext('Start Date'));
            this.registerSortableField('end_date', gettext('End Date'));
            this.registerSortableField('cumulative_count', gettext('Total Enrollment'));
            this.registerSortableField('count', gettext('Current Enrollment'));
            this.registerSortableField('count_change_7_days', gettext('Change Last Week'));
            this.registerSortableField('verified_enrollment', gettext('Verified Enrollment'));

            if (options.passingUsersEnabled) {
                this.registerSortableField('passing_users', gettext('Passing Learners'));
            }

            this.registerFilterableField('availability', gettext('Availability'));
            this.registerFilterableField('pacing_type', gettext('Pacing Type'));
            this.registerFilterableArrayField('program_ids', gettext('Programs'));
        },

        state: {
            pageSize: 100,
            sortKey: 'catalog_course_title',
            order: 0
        },

        /**
         * Constructors a filter ANDed between search and filterable fields.
         * The results are ORed Within the filterable fields,
         */
        constructFilter: function() {
            var activeFilterFields = this.getActiveFilterFields(),
                filters = [];
            if (this.searchMatcher) {
                filters.push(new SearchFilter(this.searchMatcher));
            }

            _(activeFilterFields).each(function(value, key) {
                var activeFilters;
                activeFilters = _(value.split(',')).map(function(field) {
                    if ('fieldType' in this.filterableFields[key] &&
                            this.filterableFields[key].fieldType === 'array') {
                        return new ArrayFieldFilter(key, field);
                    } else {
                        return new FieldFilter(key, field);
                    }
                }, this);
                filters.push(new FilterSet('OR', activeFilters));
            }, this);

            return new FilterSet('AND', filters);
        },

        updateSearch: function() {
            if (this.pageableCollection) {
                this.pageableCollection.getFirstPage({silent: true});
            }
            this.refresh();
            this.trigger('backgrid:searchChanged', {
                searchTerm: this.getSearchString(),
                collection: this
            });
        },

        unsetSearchString: function() {
            ListCollection.prototype.unsetSearchString.call(this);
            this.searchMatcher = undefined;
            this.updateSearch(undefined);
        },

        setSearchString: function(searchString, matcher) {
            ListCollection.prototype.setSearchString.call(this, searchString);
            this.searchMatcher = matcher;
            this.updateSearch();
        },

        /**
         * Given a filter type, returns the filters that can be applied and
         * display name.
         */
        getFilterValues: function(filterType) {
            var filters = {
                pacing_type: [{
                    name: 'instructor_paced',
                    displayName: this.getFilterValueDisplayName('pacing_type', 'instructor_paced')
                }, {
                    name: 'self_paced',
                    displayName: this.getFilterValueDisplayName('pacing_type', 'self_paced')
                }],
                availability: [{
                    name: 'Upcoming',
                    displayName: this.getFilterValueDisplayName('availability', 'Upcoming')
                }, {
                    name: 'Current',
                    displayName: this.getFilterValueDisplayName('availability', 'Current')
                }, {
                    name: 'Archived',
                    displayName: this.getFilterValueDisplayName('availability', 'Archived')
                }, {
                    name: 'unknown',
                    displayName: this.getFilterValueDisplayName('availability', 'unknown')
                }],
                program_ids: []
            };

            // Dynamically create list of program filters from programsCollection models
            this.programsCollection.each(function(program) {
                filters.program_ids.push({
                    name: program.get('program_id'),
                    displayName: program.get('program_title')
                });
            }, this);

            return filters[filterType];
        },

        refresh: function() {
            var filter = this.constructFilter();
            ListCollection.prototype.refresh.call(this);
            this.fullCollection.reset(filter.filter(this.shadowCollection), {reindex: false});
            this.trigger('backgrid:refresh', {collection: this});
        },

        // Override PageableCollection's setPage() method because it has a bug where it assumes that backgrid getPage()
        // will always return a promise. It does not in client mode.
        // Note: this function will only work in client mode. It should be removed if this collection is used
        // in server mode.
        setPage: function(page) {
            var deferred = $.Deferred();

            this.getPage(page - (1 - this.state.firstPage), {reset: true});
            // getPage() will probably throw an exception if it fails in client mode, so assume succeeded
            this.isStale = false;
            this.trigger('page_changed');
            deferred.resolve();
            return deferred.promise();
        }
    });

    return CourseListCollection;
});
