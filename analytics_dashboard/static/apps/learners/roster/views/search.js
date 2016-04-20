/**
 * Subclass of Backgrid.Extension.Filter which allows us to search
 * for learners.  Fixes accessibility issues with the Backgrid
 * filter component.
 *
 * This class is a hack in that it directly copies source code from
 * backgrid.filter 0.3.5, making it heavily reliant on that
 * particular implementation.
 */
define(function (require) {
    'use strict';

    var $ = require('jquery'),
        _ = require('underscore'),
        Backgrid = require('backgrid'),

        learnerSearchTemplate = require('text!learners/roster/templates/search.underscore'),

        LearnerSearch;

    require('backgrid-filter');

    LearnerSearch = Backgrid.Extension.ServerSideFilter.extend({
        className: function () {
            return [Backgrid.Extension.ServerSideFilter.prototype.className, 'learners-search'].join(' ');
        },
        events: function () {
            return _.extend(Backgrid.Extension.ServerSideFilter.prototype.events, {'click .search': 'search'});
        },
        template: _.template(learnerSearchTemplate, null, {variable: null}),
        initialize: function (options) {
            this.value = options.collection.searchString;
            Backgrid.Extension.ServerSideFilter.prototype.initialize.call(this, options);
        },
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

    return LearnerSearch;
});
