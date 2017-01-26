/**
 * Subclass of Backgrid.Extension.Filter which allows us to search
 * for learners.  Fixes accessibility issues with the Backgrid
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

        LearnerSearch;

    require('backgrid-filter');

    LearnerSearch = Backgrid.Extension.ServerSideFilter.extend({
        className: function() {
            return [Backgrid.Extension.ServerSideFilter.prototype.className, 'learners-search'].join(' ');
        },

        events: function() {
            return _.extend(Backgrid.Extension.ServerSideFilter.prototype.events,
                {
                    'click .search': 'search',
                    'click .clear.btn': 'clear'
                });
        },

        template: _.template(listSearchTemplate, null, {variable: null}),

        initialize: function(options) {
            this.options = options || {};
            this.listenTo(options.collection, 'sync', this.render);
            Backgrid.Extension.ServerSideFilter.prototype.initialize.call(this, options);
        },

        clearButton: function() {
            return this.$el.find('[data-backgrid-action=clear]');
        },

        render: function() {
            this.value = this.options.collection.getSearchString();
            this.$el.empty().append(this.template({
                id: 'search-learners',
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

        search: function(event) {
            var searchString = this.searchBox().val().trim();
            event.preventDefault();
            if (searchString === '') {
                this.collection.unsetSearchString();
            } else {
                this.collection.setSearchString(searchString);
                this.options.trackingModel.trigger('segment:track', 'edx.bi.roster.searched', {
                    category: 'search'
                });
            }
            this.execute();
        },

        clear: function(event) {
            event.preventDefault();
            this.collection.unsetSearchString();
            this.searchBox().val('');
            this.execute();
        },

        execute: function() {
            this.collection.refresh();
            this.resetFocus();
        },

        resetFocus: function() {
            $('#learner-app-focusable').focus();
        }
    });

    return LearnerSearch;
});
