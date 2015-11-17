/**
 * Initializes page with the model and various UI elements that need JS hooks.
 */
define(['jquery', 'load/init-models', 'load/init-tooltips'], function ($, models) {
    'use strict';

    // initialize tracking
    require(['load/init-tracking'], function (initTracking) {
        initTracking(models);
    });

    return {
        models: models
    };
});
