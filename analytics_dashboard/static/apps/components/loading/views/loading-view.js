define(function(require) {
    'use strict';

    var Marionette = require('marionette'),

        LoadingView;

    /**
     * Displays loading spinner.  Upon a successful load, the view will be
     * replaced with the "success" view.
     *
     * This view expects a template with a "loading" class and "loadingText"
     * template variable.
     */
    LoadingView = Marionette.LayoutView.extend({

        templateHelpers: function() {
            return {
                // Translators: This message indicates content is loading in the page.
                loadingText: gettext('Loading...')
            };
        },

        regions: {
            loadingRegion: '.loading'
        },

        onBeforeShow: function() {
            this.listenTo(this.model, 'sync', function() {
                this.showChildView('loadingRegion', this.options.successView);
            });
        }
    });

    return LoadingView;
});
