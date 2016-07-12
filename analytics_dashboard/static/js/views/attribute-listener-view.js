define([
    'backbone',
    'underscore'
], function(
    Backbone,
    _
) {
    'use strict';

    /**
     * This base view listens for a change in a model attribute and calls
     * render() when the attribute changes.  By default, it clears out the
     * view.
     */
    var AttributeListenerView = Backbone.View.extend({
        /**
         * Initializes an AttributeListenerView.
         *
         * It's recommended that the view's model implements a 'hasData'
         * function, which specifies when the model has data to show.  If
         * 'model.hasData()' is not implemented, this view simply checks for
         * the presence of 'model.modelAttribute' on the model.
         *
         * @param options an options object containing the following keys:
         *   - modelAttribute (String) the attribute on the model which the
         *     view should react to
         */
        initialize: function(options) {
            var self = this;
            this.options = options || {};
            self.modelAttribute = options.modelAttribute;
            self.listenTo(self.model, 'change:' + self.modelAttribute, self.render);
        },

        renderIfDataAvailable: function() {
            var self = this;
            if (self.isDataAvailable()) {
                self.render();
            }
        },

        isDataAvailable: function() {
            var isDataAvailableFunc = this.model.hasData;
            if (_.isFunction(isDataAvailableFunc)) {
                return isDataAvailableFunc.call(this.model);
            }
            return this.model.has(this.modelAttribute);
        },

        /**
         * Clears out the view.
         */
        render: function() {
            var self = this;
            self.$el.empty();
            return self;
        }

    });

    return AttributeListenerView;
});
