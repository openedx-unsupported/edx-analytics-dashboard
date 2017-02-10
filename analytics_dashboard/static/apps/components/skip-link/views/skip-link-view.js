/**
 * This view sets the focus the #content DOM element and scrolls to it.  It's
 * expected that the elements exist on the page already and the skip link has
 * class "skip-link" and the content has ID "content".
 *
 * The element (e.g. "el" attribute) for this view will need to have both the
 * skip link and the main content in it's scope and will most likely be the
 * body element.
 */
define(function(require) {
    'use strict';

    var Marionette = require('marionette');

    require('components/skip-link/behaviors/skip-link-behavior');
    require('components/skip-link/behaviors/skip-target-behavior');

    return Marionette.ItemView.extend({

        template: false,

        ui: {
            skipLink: '#skip.skip-link',
            skipTarget: '#content'
        },

        behaviors: {
            SkipTargetBehavior: {},
            SkipLinkBehavior: {}
        },

        onRender: function() {
            // enables content to be focusable
            this.ui.skipTarget.attr('tabindex', -1);
        }

    });
});
