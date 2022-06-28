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
define((require) => {
  'use strict';

  const _ = require('underscore');
  const Marionette = require('marionette');

  const ParentView = Marionette.LayoutView.extend({

    initialize(options) {
      this.options = options || {};
    },

    onBeforeShow() {
      this.showChildren();
    },

    showChildren() {
      _.each(this.childViews, _.bind(function (child) {
        // eslint-disable-next-line new-cap
        this.showChildView(child.region, new child.class(child.options));
      }, this));
    },
  });

  return ParentView;
});
