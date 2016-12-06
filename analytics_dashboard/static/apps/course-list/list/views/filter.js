/**
 * A view which renders a select box in order to filter a Course List Collection.
 *
 * It takes a collection, a display name, a filter field, and a set of possible
 * filter values.
 */
define(function(require) {
    'use strict';

    var $ = require('jquery'),
        _ = require('underscore'),
        Marionette = require('marionette'),

        Utils = require('utils/utils'),
        filterTemplate = require('text!course-list/list/templates/filter.underscore'),

        Filter;

    Filter = Marionette.ItemView.extend({
        events: function() {
            var changeFilterEvent = 'change #filter-' + this.options.filterKey,
                eventsHash = {};
            eventsHash[changeFilterEvent] = 'onFilter';
            return eventsHash;
        },

        // It is assumed that there can never be a filter with an empty
        // name, therefore it's safe to use the empty string as a
        // property in this object.  The API interprets this as "all
        // courses, unfiltered".
        catchAllFilterValue: '',

        className: 'course-list-filter',

        template: _.template(filterTemplate),

        /**
         * Initialize a filter.
         *
         * @param options an options object which must include the following
         * key/values:
         *      - collection (CourseListCollection): the course lsit collection to
         *        filter.
         *      - filterKey (string): the field to be filtered by on the course list
         *        collection.
         *      - filterValues (Object): the set of valid values that the
         *        filterKey can take on, represented as a mapping from
         *        filter values to the number of courses matching the applied
         *        filter.
         *      - selectDisplayName (string): a *translated* string that will
         *        appear as the label for this filter.
         *      - trackingModel (Object): tracking model for broadcasting filter
         *        events.
         */
        initialize: function(options) {
            this.options = options || {};
            _.bind(this.onSelectFilter, this);
            this.listenTo(this.options.collection, 'sync', this.render);
        },

        templateHelpers: function() {
            // 'filterValues' is an array of objects, each having a 'name' key
            // and a 'displayName' key.  'name' is the name of the filter value
            // (e.g. the cohort name when filtering by cohort), while
            // 'displayName' is the user-facing representation of the filter
            // which combines the filter with the number of users belonging to
            // it.
            var hideArchived = false,
                filterValues,
                selectedFilterValue;
            filterValues = _.chain(this.options.filterValues)
                .pairs()
                .map(function(filterPair) {
                    var name = filterPair[0],
                        numCourses = filterPair[1];
                    return {
                        name: name,
                        displayName: _.template(
                            // eslint-disable-next-line max-len
                            // Translators: 'name' here refers to the name of the filter, while 'numCourses' refers to the number of courses belonging to that filter.
                            gettext('<%= name %> (<%= numCourses %>)')
                        )({
                            name: name,
                            numCourses: Utils.localizeNumber(numCourses, 0)
                        })
                    };
                })
                .sortBy('name')
                .value();

            if (filterValues.length) {
                filterValues.unshift({
                    name: this.catchAllFilterValue,
                    // Translators: "All" refers to viewing all the courses in a course.
                    displayName: gettext('All')
                });

                // Assumes that you can only filter by one filterKey at a time.
                selectedFilterValue = _.chain(filterValues)
                    .pluck('name')
                    .intersection(this.options.collection.getActiveFilterFields())
                    .first()
                    .value() || this.catchAllFilterValue;
                _.findWhere(filterValues, {name: selectedFilterValue}).selected = true;
            }
            if (this.options.filterKey === 'availability') {
                // Translators: inactive meaning that these courses have not interacted with the course recently.
                this.options.selectDisplayName = gettext('Current Courses');
            }
            if ('availability' in this.options.collection.getActiveFilterFields()) {
                hideArchived = true;
            }
            return {
                filterKey: this.options.filterKey,
                filterValues: filterValues,
                hideArchived: hideArchived,
                selectDisplayName: this.options.selectDisplayName
            };
        },

        onCheckboxFilter: function(event) {
            if ($(event.currentTarget).find('input:checkbox:checked').length) {
                this.collection.setFilterField('availability', 'archived');
            } else {
                this.collection.unsetFilterField('availability');
            }
            this.collection.refresh();
            $('#course-list-app-focusable').focus();
            this.options.trackingModel.trigger('segment:track', 'edx.bi.course_list.filtered', {
                category: 'archived'
            });
        },

        onSelectFilter: function(event) {
            // Sends a request to the server for the filtered course list.
            var selectedOption = $(event.currentTarget).find('option:selected'),
                selectedFilterValue = selectedOption.val(),
                filterWasUnset = selectedFilterValue === this.catchAllFilterValue;
            event.preventDefault();
            if (this.options.filterKey === 'availability') {
                selectedFilterValue = 'archived';
            }
            if (filterWasUnset) {
                this.collection.unsetFilterField(this.options.filterKey);
            } else {
                this.collection.setFilterField(this.options.filterKey, selectedFilterValue);
            }
            this.collection.refresh();
            $('#course-list-app-focusable').focus();
            this.options.trackingModel.trigger('segment:track', 'edx.bi.course_list.filtered', {
                category: this.options.filterKey
            });
        },

        onFilter: function(event) {
            if ($(event.currentTarget).find('option').length) {
                this.onSelectFilter(event);
            } else if ($(event.currentTarget).find('input:checkbox').length) {
                this.onCheckboxFilter(event);
            }
        }
    });

    return Filter;
});
