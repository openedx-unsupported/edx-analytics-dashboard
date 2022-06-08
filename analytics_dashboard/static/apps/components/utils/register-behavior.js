/**
 * Registered the Marionette behavior so that the views can access them.
 */
define((require) => {
  'use strict';

  const Marionette = require('marionette');

  return (behavior, behaviorName) => {
    Marionette.Behaviors.behaviorsLookup = () => window.Behaviors;

    if (!window.Behaviors) {
      window.Behaviors = {};
    }
    window.Behaviors[behaviorName] = behavior;
  };
});
