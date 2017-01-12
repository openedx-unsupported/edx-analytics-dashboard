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

        courseListSearchTemplate = require('text!course-list/list/templates/search.underscore'),

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

        template: _.template(courseListSearchTemplate, null, {variable: null}),

        initialize: function(options) {
            this.options = options || {};
            this.listenTo(options.collection, 'backgrid:refresh', this.render);
            Backgrid.Extension.ClientSideFilter.prototype.initialize.call(this, options);
        },

        clearButton: function() {
            return this.$el.find('[data-backgrid-action=clear]');
        },

        render: function() {
            this.value = this.options.collection.getSearchString();
            this.$el.empty().append(this.template({
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
            var searchString = this.searchBox().val().trim();
            if (event) event.preventDefault();
            if (searchString === '') {
                this.options.collection.unsetSearchString();
            } else {
                this.options.collection.setSearchString(searchString);
                this.options.trackingModel.trigger('segment:track', 'edx.bi.course-list.searched', {
                    category: 'search'
                });
            }
            Backgrid.Extension.ClientSideFilter.prototype.search.call(this, event);
            this.execute();
        },

        clear: function(event) {
            event.preventDefault();
            this.options.collection.unsetSearchString();
            Backgrid.Extension.ClientSideFilter.prototype.clear.call(this, event);
            this.execute();
        },

        execute: function() {
            this.options.collection.refresh();
            // Surprisingly calling refresh() does not emit a backgrid:refresh event. So do that here:
            this.options.collection.trigger('backgrid:refresh', {collection: this.options.collection});
            this.resetFocus();
        },

        resetFocus: function() {
            $('#course-list-app-focusable').focus();
        }
    });

    return CourseListSearch;
});
