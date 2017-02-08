/**
 * Catches the click event and prevents the default action, which is useful for
 * for preserving the URL fragment when an anchor link is clicked.
 *
 * It is expected that "skipLink" is defined in the ui hash.
 */
define(function(require) {
    'use strict';

    var Marionette = require('marionette'),
        registerBehaviour = require('components/utils/register-behaviour'),

        SkipLinkBehaviour;

    SkipLinkBehaviour = Marionette.Behavior.extend({

        events: {
            'click @ui.skipLink': 'clicked'
        },

        clicked: function(e) {
            e.preventDefault();
            this.ui.skipLink.trigger('skipLinkClicked', e);
        }
    });

    registerBehaviour(SkipLinkBehaviour, 'SkipLinkBehaviour');

    return SkipLinkBehaviour;
});
