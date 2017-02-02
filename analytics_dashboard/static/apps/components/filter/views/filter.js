/**
 * A view which renders a select box in order to filter a ListCollection.
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
        // items, unfiltered".
        catchAllFilterValue: '',

        className: function() {
            return this.appClass + '-filter';
        },

        /**
         * Updates the filter set on the collection and calls filterUpdated().
         */
        onFilter: function() {
            throw 'onFilter must be implemented'
        },

        /**
         * Initialize a filter.
         *
         * @param options an options object which must include the following
         * key/values:
         *      - collection (ListCollection): the collection to
         *        filter.
         *      - filterKey (string): the field to be filtered by on the collection.
         *      - filterValues (Object): the set of valid values that the
         *        filterKey can take on, represented as a mapping from
         *        filter values to the number of items matching the applied filter.
         *      - selectDisplayName (string): a *translated* string that will
         *        appear as the label for this filter.
         *      - trackingModel (Object): tracking model for broadcasting filter
         *        events.
         */
        initialize: function(options) {
            this.options = _.defaults({}, options, {
                trackSubject: 'list',
                appClass: ''
            });
            this.options = _.defaults(this.options, {
                trackFilterEventName: ['edx', 'bi', this.options.trackSubject, 'filtered'].join('.')
            });
            this.listenTo(this.options.collection, 'sync', this.render);
        },

        templateHelpers: function() {
            // 'filterValues' is an array of objects, each having a 'name' key
            // and a 'displayName' key.  'name' is the name of the filter value
            // (e.g. the cohort name when filtering by cohort), while
            // 'displayName' is the user-facing representation of the filter
            // which combines the filter with the number of users belonging to
            // it.
            var filterValues;

            filterValues = _.chain(this.options.filterValues)
                .pairs()
                .map(function(filterPair) {
                    var name = filterPair[0],
                        count = filterPair[1];
                    return {
                        name: name,
                        displayName: _.template(
                            // eslint-disable-next-line max-len
                            // Translators: 'name' here refers to the name of the filter, while 'count' refers to the number of items belonging to that filter.
                            gettext('<%= name %> (<%= count %>)')
                        )({
                            name: name,
                            count: Utils.localizeNumber(count, 0)
                        })
                    };
                })
                .sortBy('name')
                .value();

            return {
                filterKey: this.options.filterKey,
                filterValues: filterValues,
                selectDisplayName: this.options.selectDisplayName
            };
        },

        /**
         * Refreshes collection, sets focus, and triggers tracking event.
         */
        filterUpdated: function(filterValue) {
            this.collection.refresh();
            $('#' + this.appClass + '-focusable').focus();
            this.options.trackingModel.trigger('segment:track', this.options.trackFilterEventName, {
                category: filterValue
            });
        }

    });

    return Filter;
});
