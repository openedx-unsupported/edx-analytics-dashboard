/**
 * A view which renders a select box in order to filter a Learners Collection.
 *
 * It takes a collection, a display name, a filter field, and a set of possible
 * filter values.
 */
define(function (require) {
    'use strict';

    var $ = require('jquery'),
        _ = require('underscore'),
        Marionette = require('marionette'),

        Utils = require('utils/utils'),
        filterTemplate = require('text!learners/roster/templates/filter.underscore'),

        Filter;

    Filter = Marionette.ItemView.extend({
        events: function () {
            var changeFilterEvent = 'change #filter-' + this.options.filterKey,
                eventsHash = {};
            eventsHash[changeFilterEvent] = 'onSelectFilter';
            return eventsHash;
        },

        className: 'learners-filter',

        template: _.template(filterTemplate),

        /**
         * Initialize a filter.
         *
         * @param options an options object which must include the following
         * key/values:
         *      - collection (LearnersCollection): the learners collection to
         *        filter.
         *      - filterKey (string): the field to be filtered by on the learner
         *        collection.
         *      - filterValues (Object): the set of valid values that the
         *        filterKey can take on, represented as a mapping from
         *        filter values to the number of learners matching the applied
         *        filter.
         *      - selectDisplayName (string): a *translated* string that will
         *        appear as the label for this filter.
         */
        initialize: function (options) {
            this.options = options || {};
            _.bind(this.onSelectFilter, this);
        },

        templateHelpers: function () {
            // 'filterValues' is an array of objects, each having a 'name' key
            // and a 'displayName' key.  'name' is the canonical name for the
            // filter, while 'displayName' is the user-facing representation of
            // the filter which combines the filter with the number of users
            // belonging to it.
            var catchAllFilterValue,
                filterValues,
                selectedFilterValue;
            filterValues = _.chain(this.options.filterValues)
                .pairs()
                .map(function (filterPair) {
                    var name = filterPair[0],
                        numLearners = filterPair[1];
                    return {
                        name: name,
                        displayName: _.template(ngettext(
                            // jshint ignore:start
                            // Translators: 'name' is the name of the filter value and 'numLearners' is the number of learners within that specific filter.  The resulting phrase displays a filter and the number of students belonging to it. For example: "Cohort Awesome (1,234 learners)".
                            '<%= name %> (<%= numLearners %> learner)',
                            // Translators: 'name' is the name of the filter value and 'numLearners' is the number of learners within that specific filter.  The resulting phrase displays a filter and the number of students belonging to it. For example: "Cohort Awesome (1,234 learners)".
                            '<%= name %> (<%= numLearners %> learners)',
                            // jshint ignore:end
                            numLearners
                        ))({
                            name: name,
                            numLearners: Utils.localizeNumber(numLearners, 0)
                        })
                    };
                })
                .value();

            if (filterValues.length) {
                // It is assumed that there can never be a filter with an empty
                // name, therefore it's safe to use the empty string as a
                // property in this object.  The API interprets this as "all
                // students, unfiltered".
                catchAllFilterValue = '';
                filterValues.unshift({
                    name: catchAllFilterValue,
                    // Translators: "All" refers to viewing all the learners in a course.
                    displayName: gettext('All')
                });

                // Assumes that you can only filter by one filterKey at a time.
                selectedFilterValue = _.chain(filterValues)
                    .pluck('name')
                    .intersection(this.options.collection.getActiveFilterFields())
                    .first()
                    .value() || catchAllFilterValue;
                _.findWhere(filterValues, {name: selectedFilterValue}).selected = true;
            }

            return {
                filterKey: this.options.filterKey,
                filterValues: filterValues,
                selectDisplayName: this.options.selectDisplayName
            };
        },

        onSelectFilter: function (event) {
            // Sends a request to the server for the filtered learner list.
            event.preventDefault();
            this.collection.setFilterField(
                this.options.filterKey,
                $(event.currentTarget).find('option:selected').val()
            );
            this.collection.refresh();
            $('#learner-app-focusable').focus();
        }
    });

    return Filter;
});
