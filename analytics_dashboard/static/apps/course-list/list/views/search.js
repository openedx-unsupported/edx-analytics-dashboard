/**
 * Subclass of Backgrid.Extension.Filter which allows us to search
 * for courses.  Fixes accessibility issues with the Backgrid
 * filter component.
 *
 * This class is a hack in that it directly copies source code from
 * backgrid.filter 0.3.5, making it heavily reliant on that
 * particular implementation.
 */
define(function(require) {
    'use strict';

    var $ = require('jquery'),
        _ = require('underscore'),
        Backgrid = require('backgrid'),

        listSearchTemplate = require('text!components/generic-list/list/templates/search.underscore'),

        CourseListSearch;

    require('backgrid-filter');

    CourseListSearch = Backgrid.Extension.ClientSideFilter.extend({
        className: function() {
            return [Backgrid.Extension.ClientSideFilter.prototype.className, 'course-list-search'].join(' ');
        },

        events: function() {
            var superEvents = Backgrid.Extension.ClientSideFilter.prototype.events;
            delete superEvents['keydown input[type=search]']; // Don't search on key down
            return _.extend(superEvents,
                {
                    'click .search': 'search',
                    'click .clear.btn': 'clear'
                }
            );
        },

        fields: ['catalog_course_title', 'course_id'],

        template: _.template(listSearchTemplate, null, {variable: null}),

        initialize: function(options) {
            this.options = options || {};
            this.listenTo(options.collection, 'backgrid:refresh', this.render);
            this.listenTo(options.collection, 'backgrid:searchChanged', this.searchChanged);
            this.listenTo(options.collection, 'backgrid:filtersCleared', this.filtersCleared);

            // these lines are taken from backgrid-filter because we don't call
            // ClientSideFilter's initialize()
            this.fields = options.fields || this.fields;
            this.wait = options.wait || this.wait;

            // the ClientSideFilter creates a copy of the collection for storing and restoring
            // the results and we want to manage the "shadowCollection" within the course-list
            // collection.  Calling the parent (ServerSideFilter) of ClientSideFiter ensures this.
            Backgrid.Extension.ServerSideFilter.prototype.initialize.call(this, options);
        },

        clearButton: function() {
            return this.$el.find('[data-backgrid-action=clear]');
        },

        render: function() {
            this.value = this.options.collection.getSearchString();
            this.$el.empty().append(this.template({
                id: 'search-course-list',
                name: this.name,
                placeholder: this.placeholder,
                value: this.value,
                labelText: gettext('Search courses'),
                executeSearchText: gettext('search'),
                clearSearchText: gettext('clear search')
            }));
            this.showClearButtonMaybe();
            this.delegateEvents();
            return this;
        },

        search: function(event) {
            var searchString = this.searchBox().val().trim(),
                matcher = _.bind(this.makeMatcher(this.query()), this);

            if (event) {
                event.preventDefault();
            }

            if (searchString === '') {
                this.clear(event);
            } else {
                this.options.collection.setSearchString(searchString, matcher);
            }
        },

        clear: function(event) {
            if (event) {
                event.preventDefault();
            }
            this.options.collection.unsetSearchString();
            this.clearSearchBox();
        },

        /**
         * Called when the search changes and triggers a tracking event if something is
         * searched for.
         */
        searchChanged: function(options) {
            if (options.searchTerm) {
                this.options.trackingModel.trigger('segment:track', 'edx.bi.course_list.searched', {
                    category: 'search'
                });
            }
            $('#course-list-focusable').focus();
        },

        filtersCleared: function(filters) {
            if (_(filters).has('text_search')) {
                this.clear();
            }
        }
    });

    return CourseListSearch;
});
