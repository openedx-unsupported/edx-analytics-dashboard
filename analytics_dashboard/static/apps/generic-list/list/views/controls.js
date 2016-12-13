/**
 * A wrapper view for controls.
 */
define(function(require) {
    'use strict';

    var _ = require('underscore'),
        Marionette = require('marionette'),

        ListSearch = require('generic-list/list/views/search'),
        rosterControlsTemplate = require('text!generic-list/list/templates/controls.underscore'),

        ListControlsView;

    ListControlsView = Marionette.LayoutView.extend({
        template: _.template(rosterControlsTemplate),

        regions: {
            search: '.search-container'
        },

        initialize: function(options) {
            this.options = options || {};

            this.childViews = [
                {
                    region: 'search',
                    class: ListSearch,
                    options: {
                        collection: this.options.collection,
                        name: 'text_search',
                        placeholder: gettext('Search'),
                        trackingModel: this.options.trackingModel
                    }
                }
            ];
        },

        onBeforeShow: function() {
            _.each(this.childViews, _.bind(function(child) {
                this.showChildView(child.region, new child.class(child.options));
            }, this));
        }
    });

    return ListControlsView;
});
