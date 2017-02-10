/**
 * Catches the click event and prevents the default action, which is useful for
 * for preserving the URL fragment when an anchor link is clicked.
 *
 * It is expected that "skipLink" is defined in the ui hash.
 */
define(function(require) {
    'use strict';

    var Marionette = require('marionette'),
        registerBehavior = require('components/utils/register-behavior'),

        SkipLinkBehavior;

    SkipLinkBehavior = Marionette.Behavior.extend({

        events: {
            'click @ui.skipLink': 'clicked'
        },

        clicked: function(e) {
            e.preventDefault();
            this.ui.skipLink.trigger('skipLinkClicked', e);
        }
    });

    registerBehavior(SkipLinkBehavior, 'SkipLinkBehavior');

    return SkipLinkBehavior;
});
