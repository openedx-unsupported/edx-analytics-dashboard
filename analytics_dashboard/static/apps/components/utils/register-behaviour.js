/**
 * Registered the Marionette behaviour so that the views can access them.
 */
define(function(require) {
    'use strict';

    var Marionette = require('marionette');

    return function(behaviour, behaviourName) {
        Marionette.Behaviors.behaviorsLookup = function() {
            return window.Behaviors;
        };

        if (!window.Behaviors) {
            window.Behaviors = {};
        }
        window.Behaviors[behaviourName] = behaviour;
    };
});
