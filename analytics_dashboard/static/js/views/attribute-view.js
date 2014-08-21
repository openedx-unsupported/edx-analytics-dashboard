define(['views/attribute-listener-view'],
    function (AttributeListenerView) {
        'use strict';

        /**
         * Displays the model attribute as text in the el.
         */
        var AttributeView = AttributeListenerView.extend({

            initialize: function (options) {
                AttributeListenerView.prototype.initialize.call(this, options);
                var self = this;
                self.renderIfDataAvailable();
            },

            render: function () {
                AttributeListenerView.prototype.render.call(this);
                var self = this;
                self.$el.html(self.model.get(self.modelAttribute));
                return self;
            }

        });

        return AttributeView;
    }
);
