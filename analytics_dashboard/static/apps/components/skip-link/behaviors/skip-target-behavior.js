/**
 * Catches the skipLinkClicked event and sets the focus on the target.  It's
 * expected that "skipTarget" is defined in the ui hash.
 */
define((require) => {
  'use strict';

  const $ = require('jquery');
  const Marionette = require('marionette');
  const registerBehavior = require('components/utils/register-behavior');

  const SkipTargetBehavior = Marionette.Behavior.extend({

    events: {
      skipLinkClicked: 'skipLinkClicked',
    },

    skipLinkClicked(e) {
      const targetId = $(e.target).attr('href');
      const thisId = `#${$(this.ui.skipTarget).attr('id')}`;
      // the event can bubble, so check to ensure this is the correct target
      if (targetId === thisId) {
        this.ui.skipTarget.focus();
        this.ui.skipTarget[0].scrollIntoView();
      }
    },

  });

  registerBehavior(SkipTargetBehavior, 'SkipTargetBehavior');

  return SkipTargetBehavior;
});
