define(function(require) {
    'use strict';

    var Backbone = require('backbone'),

        ListUtils = require('generic-list/common/utils'),

        ListItemModel;

    ListItemModel = Backbone.Model.extend({
        defaults: function() {
            return {
                id: 0
            };
        },

        idAttribute: 'id',

        url: function() {
            return Backbone.Model.prototype.url.call(this) + '?id=' + encodeURIComponent(this.get('id'));
        },

        fetch: function(options) {
            return Backbone.Model.prototype.fetch.call(this, options)
                .fail(ListUtils.handleAjaxFailure.bind(this));
        },

        /**
         * Returns true if the id has been set.  False otherwise.
         */
        hasData: function() {
            return this.get('id') !== 0;
        }
    });

    return ListItemModel;
});
