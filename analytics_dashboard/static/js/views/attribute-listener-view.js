define(['backbone'],
    function (Backbone) {
        'use strict';

        /**
         * This base view listens for a change in a model attribute and calls
         * render() when the attribute changes.  By default, it clears out the
         * view.
         */
        var AttributeListenerView = Backbone.View.extend({
            initialize: function (options) {
                var self = this;
                self.modelAttribute = options.modelAttribute;
                self.listenTo(self.model, 'change:' + self.modelAttribute, self.render);
            },

            renderIfDataAvailable: function () {
                var self = this;
                if (self.model.has(self.modelAttribute)) {
                    self.render();
                }
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
