/**
 * A wrapper view for controls.
 */
define(function(require) {
    'use strict';

    var _ = require('underscore'),
        Marionette = require('marionette'),

        rosterControlsTemplate = require('text!generic-list/list/templates/controls.underscore'),

        ListControlsView;

    ListControlsView = Marionette.LayoutView.extend({
        template: _.template(rosterControlsTemplate),

        initialize: function(options) {
            this.options = options || {};
        },

        onBeforeShow: function() {
            _.each(this.childViews, _.bind(function(child) {
                this.showChildView(child.region, new child.class(child.options));
            }, this));
        }
    });

    return ListControlsView;
});
