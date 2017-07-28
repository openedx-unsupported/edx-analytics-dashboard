/**
 * A type of Marionette LayoutView that contains children views.
 *
 * Subclass this view and set the `childViews` property of the instance during initialize. For example:
 *
 *  this.childViews = [
 *      {
 *          region: 'results',
 *          class: ViewClass,
 *          options: {
 *              collection: this.options.collection,
 *              hasData: this.options.hasData,
 *              trackingModel: this.options.trackingModel
 *          }
 *      }
 *  ];
 *
 * Before the parent view is shown, each of the regions of the view will be filled with the appropriate childView.
 */
define(function(require) {
    'use strict';

    var _ = require('underscore'),
        Marionette = require('marionette'),

        ParentView;

    ParentView = Marionette.LayoutView.extend({

        initialize: function(options) {
            this.options = options || {};
        },

        onBeforeShow: function() {
            this.showChildren();
        },

        showChildren: function() {
            _.each(this.childViews, _.bind(function(child) {
                // es2015 uses default as the constructor function
                var childView = _.isFunction(child.class, 'class') ?
                    new child.class(child.options) : new child.class.default(child.options);
                this.showChildView(child.region, childView);
            }, this));
        }
    });

    return ParentView;
});
