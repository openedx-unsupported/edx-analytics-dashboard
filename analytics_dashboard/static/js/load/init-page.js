/**
 * Initializes page with the model and various UI elements that need JS hooks.
 */

var initTracking = require('load/init-tracking');
define(['jquery', 'load/init-models', 'load/init-tooltips'], function($, models) {
    'use strict';

    // initialize tracking
    (function() {
        initTracking(models);
    });

    return {
        models: models
    };
});
