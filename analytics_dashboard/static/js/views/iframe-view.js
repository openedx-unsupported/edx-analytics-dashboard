define(['backbone', 'jquery'], function(Backbone, $) {
    'use strict';

    /**
     * Loads the iframe source.  This is useful for loading iframe content after
     * page loads.  Provide "loadingSelector" as an option if a loading message/spinner
     * should be removed after the source loads.
     */
    var IFrameView = Backbone.View.extend({

        initialize: function(options) {
            this.options = options;
        },

        render: function() {
            var self = this;
            self.$el.attr('src', self.$el.data('src'));
            if (self.options.loadingSelector) {
                self.$el.on('load', function() {
                    $(self.options.loadingSelector).remove();
                });
            }
            return self;
        }

    });

    return IFrameView;
});
