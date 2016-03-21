define(['backbone'],
    function (Backbone) {
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
             * @param options an options object containing the following keys:
             *   - modelAttribute (String) the attribute on the model which the
             *     view should react to
             *   - isDataAvailable (Function) an optional function which, if
             *     provided, specifies how to determine if the model has data.
             *     It is bound to the context of this view.  If not provided,
             *     this view simply checks for the presence of
             *     'model.modelAttribute' on the model.
             */
            initialize: function (options) {
                var self = this;
                this.options = options || {};
                self.modelAttribute = options.modelAttribute;
                self.listenTo(self.model, 'change:' + self.modelAttribute, self.render);
            },

            renderIfDataAvailable: function () {
                var self = this;
                if (self.isDataAvailable()) {
                    self.render();
                }
            },

            isDataAvailable: function () {
                var isDataAvailableFunc = this.options.isDataAvailable;
                if (typeof isDataAvailableFunc === 'function') {
                    return isDataAvailableFunc.call(this);
                }
                return this.model.has(this.modelAttribute);
            },

            /**
             * Clears out the view.
             */
            render: function () {
                var self = this;
                self.$el.empty();
                return self;
            }

        });

        return AttributeListenerView;
    }
);
