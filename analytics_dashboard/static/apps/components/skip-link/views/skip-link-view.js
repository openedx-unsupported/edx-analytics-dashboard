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

    return Marionette.ItemView.extend({

        template: false,

        ui: {
            skipLink: '.skip-link',
            content: '#content'
        },

        events: {
            'click @ui.skipLink': 'clicked'
        },

        onRender: function() {
            // enables content to be focusable
            this.ui.content.attr('tabindex', -1);
        },

        clicked: function(e) {
            this.ui.content.focus();
            this.ui.content[0].scrollIntoView();
            e.preventDefault();
        }

    });
});
